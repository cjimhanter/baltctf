"""
notes — уязвимый сервис командных заметок для формата Attack/Defense.

Назначение
----------
Каждая команда ведёт набор приватных записей (notes). В штатном режиме
команда видит только свои записи. В начале раунда checker-система,
действуя как легитимный пользователь своей команды, размещает в записи
флаг вида BALTCTF{...} (операция put) и затем читает эту же запись
штатным авторизованным способом (операция get).

В сервис намеренно заложена цепочка из трёх связанных уязвимостей
(bug chaining). Флаг checker-системы достижим атакующей командой только
по этой цепочке и недоступен через штатный интерфейс:

  Шаг 1. Разведка через небезопасную конфигурацию  (A02:2025; CWE-489, CWE-209, CWE-306)
  Шаг 2. Подмена командного контекста при слабой аутентификации (A07:2025; CWE-287, CWE-306)
  Шаг 3. Нарушение контроля доступа — IDOR           (A01:2025; CWE-639, CWE-862, CWE-863, CWE-284)
  Цель.  Извлечение флага                            (CWE-200)

Переключатели окружения (см. README.md):
  NOTES_DEBUG   "1" (по умолчанию) — отладочный режим: маршрут /api/debug и
                подробные трассировки в ответах. "0" — выключить разведку.
  NOTES_SECURE  "0" (по умолчанию) — IDOR присутствует (уязвимое состояние).
                "1" — серверная проверка принадлежности записи (рекомендуемый
                фикс от IDOR). Это «заплатка», которую защищающаяся команда
                ставит прямо во время игры; штатный путь checker-системы при
                этом продолжает работать.
  NOTES_DB_PATH путь к файлу SQLite (по умолчанию рядом с app.py).
  NOTES_HOST / NOTES_PORT — адрес прослушивания (по умолчанию 0.0.0.0:8080).
"""

from __future__ import annotations

import base64
import hmac
import os
import sqlite3
import traceback
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException


# --- Конфигурация (намеренно небезопасные значения по умолчанию) ---------------

def _flag_env(name: str, default: bool) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() in {"1", "true", "yes", "on"}


DEBUG = _flag_env("NOTES_DEBUG", True)      # Шаг 1: отладочный режим оставлен включённым.
SECURE = _flag_env("NOTES_SECURE", False)   # Шаг 3: IDOR-фикс по умолчанию выключен.
DB_PATH = os.getenv("NOTES_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.db"))
HOST = os.getenv("NOTES_HOST", "0.0.0.0")
PORT = int(os.getenv("NOTES_PORT", "8080"))

app = Flask(__name__)


# --- Хранилище: компактная реляционная база SQLite -----------------------------
#
# Идентификатор записи — целочисленный и присваивается последовательно
# (INTEGER PRIMARY KEY AUTOINCREMENT). Последовательный id выбран осознанно:
# он соответствует распространённому в реальных приложениях шаблону и делает
# учебную уязвимость (IDOR) наблюдаемой и воспроизводимой.

SCHEMA = """
CREATE TABLE IF NOT EXISTS teams (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    slug       TEXT UNIQUE NOT NULL,
    auth_key   TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id    INTEGER NOT NULL,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams (id)
);
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Командный сессионный токен ------------------------------------------------
#
# УЯЗВИМОСТЬ (Шаг 2, A07:2025, CWE-287): токен НЕ подписан. Это обратимое
# кодирование идентификатора команды — base64url("team:<team_id>"). Любой,
# кто знает схему (она раскрывается на Шаге 1), может подделать токен другой
# команды без какого-либо секретного ключа.

def make_token(team_id: int) -> str:
    raw = f"team:{team_id}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


def parse_token(token: str) -> int | None:
    try:
        raw = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
    except Exception:
        return None
    if not raw.startswith("team:"):
        return None
    try:
        return int(raw.split(":", 1)[1])
    except ValueError:
        return None


def read_token_from_request() -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    header = request.headers.get("X-Team-Token")
    if header:
        return header.strip()
    return None


def current_team() -> sqlite3.Row | None:
    """Аутентификация по токену.

    Токен лишь декодируется — подпись не проверяется (CWE-287). Команда
    обязана существовать в базе, но это легко обойти: id последовательны,
    поэтому подделать токен существующей команды тривиально.
    """
    token = read_token_from_request()
    if not token:
        return None
    team_id = parse_token(token)
    if team_id is None:
        return None
    return get_db().execute(
        "SELECT id, slug, auth_key, created_at FROM teams WHERE id = ?",
        (team_id,),
    ).fetchone()


# --- Единый формат ответов об ошибке -------------------------------------------

def error(status: int, message: str, **extra):
    payload = {"error": message, "status": status}
    payload.update(extra)
    return jsonify(payload), status


# --- CORS для браузерного клиента ----------------------------------------------
#
# Разрешаем кросс-доменные запросы, чтобы веб-клиент (ui/notes-client.html) мог
# обращаться к API из браузера. Аутентификация идёт через заголовок Authorization
# (Bearer), а не через cookie, поэтому Access-Control-Allow-Origin: * безопасен.
# Flask автоматически отвечает на предзапрос OPTIONS; здесь добавляются заголовки.

CORS_ENABLED = _flag_env("NOTES_CORS", True)


@app.after_request
def add_cors_headers(response):
    if CORS_ENABLED:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Max-Age"] = "86400"
    return response


# --- Служебные маршруты --------------------------------------------------------

@app.get("/")
@app.get("/api/status")
def status():
    return {
        "service": "notes",
        "status": "ok",
        "description": "Team notes service (Attack/Defense training target).",
    }


# --- Аутентификация: выдача командного токена -----------------------------------
#
# Штатный путь: команда предъявляет свой slug и команд­ный ключ (auth_key),
# а сервис возвращает сессионный токен. checker-система знает ключ своей
# команды и вызывает этот маршрут в начале раунда. Ключ закрывает атакующему
# возможность ПОЛУЧИТЬ чужой токен здесь — но не подделать его (см. Шаг 2).

@app.post("/api/session")
def session_login():
    data = request.get_json(silent=True) or {}
    slug = (data.get("team") or "").strip()
    key = (data.get("key") or "").strip()
    if not slug or not key:
        return error(400, "team and key are required")

    db = get_db()
    row = db.execute("SELECT id, auth_key FROM teams WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        # Первое обращение команды — регистрируем её (bootstrap для checker-а).
        cur = db.execute(
            "INSERT INTO teams (slug, auth_key, created_at) VALUES (?, ?, ?)",
            (slug, key, now_iso()),
        )
        db.commit()
        team_id = cur.lastrowid
    else:
        team_id = row["id"]
        if not hmac.compare_digest(row["auth_key"], key):
            return error(403, "invalid team key")

    return {"team_id": team_id, "token": make_token(team_id)}


# --- Создание записи -----------------------------------------------------------

@app.post("/api/notes")
def create_note():
    team = current_team()
    if team is None:
        return error(401, "authentication required")

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "Untitled note").strip()
    body = (data.get("body") or "").strip()
    if not body:
        return error(400, "body is required")

    db = get_db()
    cur = db.execute(
        "INSERT INTO notes (team_id, title, body, created_at) VALUES (?, ?, ?, ?)",
        (team["id"], title, body, now_iso()),
    )
    db.commit()
    note_id = cur.lastrowid
    return (
        jsonify(
            {
                "ok": True,
                "note": {
                    "id": note_id,
                    "team_id": team["id"],
                    "title": title,
                    "body": body,
                },
            }
        ),
        201,
    )


# --- Список собственных записей (ШТАТНЫЙ, защищённый путь) ----------------------
#
# Выборка строго ограничена записями вызывающей команды (WHERE team_id = ?).
# Через этот маршрут чужой флаг получить нельзя — он формирует «штатный путь»,
# по которому checker и легитимная команда работают только со своими данными.

@app.get("/api/notes")
def list_notes():
    team = current_team()
    if team is None:
        return error(401, "authentication required")

    rows = get_db().execute(
        "SELECT id, title, created_at FROM notes WHERE team_id = ? ORDER BY id",
        (team["id"],),
    ).fetchall()
    return {"team_id": team["id"], "notes": [dict(row) for row in rows]}


# --- Чтение записи по идентификатору -------------------------------------------
#
# УЯЗВИМОСТЬ (Шаг 3, A01:2025, CWE-639/862/863/284): маршрут использует
# переданный пользователем id напрямую для выборки записи и НЕ проверяет,
# принадлежит ли запись запрашивающей команде. Перебирая последовательные id,
# участник читает произвольные записи (горизонтальное повышение привилегий).
#
# Этот же маршрут checker использует для штатного чтения собственной записи
# по id. Поэтому добавление проверки принадлежности (NOTES_SECURE=1) закрывает
# уязвимый путь, но не ломает checker: чтение СВОЕЙ записи остаётся доступным.

@app.get("/api/notes/<int:note_id>")
def get_note(note_id: int):
    team = current_team()
    if team is None:
        return error(401, "authentication required")

    row = get_db().execute(
        "SELECT id, team_id, title, body, created_at FROM notes WHERE id = ?",
        (note_id,),
    ).fetchone()
    if row is None:
        return error(404, "note not found")

    # --- ФИКС от IDOR (рекомендуемая мера) -------------------------------------
    # Включается переключателем NOTES_SECURE=1 или внесением этих двух строк в код.
    if SECURE and row["team_id"] != team["id"]:
        return error(403, "you do not own this note")
    # ---------------------------------------------------------------------------

    return {"note": dict(row)}


# --- Диагностический маршрут (ШАГ 1: РАЗВЕДКА) ----------------------------------
#
# УЯЗВИМОСТЬ (Шаг 1, A02:2025, CWE-489/209/306): оставленный отладочный
# маршрут без аутентификации раскрывает внутренние детали — последовательную
# природу id записей, наличие маршрута прямого чтения и схему токена с живым
# примером. Сам по себе доступа к флагу не даёт, но формирует «карту» атаки.

@app.get("/api/debug")
def debug_panel():
    if not DEBUG:
        return error(404, "not found")

    db = get_db()
    teams_stat = db.execute("SELECT COUNT(*) AS c, MAX(id) AS mx FROM teams").fetchone()
    notes_stat = db.execute("SELECT COUNT(*) AS c, MIN(id) AS mn, MAX(id) AS mx FROM notes").fetchone()
    sample = db.execute("SELECT id, slug FROM teams ORDER BY id LIMIT 1").fetchone()

    token_example = None
    if sample is not None:
        token_example = {
            "team_id": sample["id"],
            "slug": sample["slug"],
            "decoded": f"team:{sample['id']}",
            "token": make_token(sample["id"]),
        }

    return {
        "service": "notes",
        "debug": True,
        "config": {"NOTES_DEBUG": DEBUG, "NOTES_SECURE": SECURE, "db_path": DB_PATH},
        "token_scheme": "base64url('team:<team_id>')  # UNSIGNED — forgeable, do not ship",
        "token_example": token_example,
        "notes_id_sequence": {
            "type": "sequential integer (INTEGER PRIMARY KEY AUTOINCREMENT)",
            "count": notes_stat["c"],
            "min_id": notes_stat["mn"],
            "max_id": notes_stat["mx"],
        },
        "teams": {"count": teams_stat["c"], "max_id": teams_stat["mx"]},
        "routes": sorted({rule.rule for rule in app.url_map.iter_rules()}),
        "hint": "GET /api/notes/<id> fetches a note by its global sequential id.",
    }


# --- Обработка ошибок -----------------------------------------------------------
#
# УЯЗВИМОСТЬ (Шаг 1, A02:2025, CWE-209): в отладочном режиме сервис возвращает
# подробную трассировку стека в теле ответа — это раскрытие чувствительных
# сведений в сообщении об ошибке.

@app.errorhandler(Exception)
def handle_exception(exc):
    if isinstance(exc, HTTPException):
        return jsonify({"error": exc.name, "status": exc.code}), exc.code
    if DEBUG:
        return (
            jsonify(
                {
                    "error": "internal server error",
                    "exception": repr(exc),
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )
    return jsonify({"error": "internal server error", "status": 500}), 500


def main() -> None:
    init_db()
    app.run(host=HOST, port=PORT)


if __name__ == "__main__":
    main()
