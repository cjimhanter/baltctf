# Руководство по запуску и эксплуатации

## Локальный запуск

Перейти в каталог проекта:

```bash
cd ~/Projects/baltctf
```

Если нужны кастомные переменные среды:

```bash
cp .env.example .env
```

Поднять и пересобрать стек:

```bash
docker compose up --build
```

Альтернативно можно сначала поднять только базу, применить миграции и загрузить демонстрационные данные:

```bash
docker compose up -d db
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_demo_data --reset
docker compose up --build
```

## Миграции и демо-данные

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_demo_data --reset
```

## Адреса

- frontend dashboard: `http://localhost:5173/`
- scoreboard: `http://localhost:5173/scoreboard`
- service matrix: `http://localhost:5173/services`
- team portal: `http://localhost:5173/team`
- admin tools: `http://localhost:5173/admin`
- backend API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`
- PostgreSQL: `localhost:5432`
- vulnbox web demo: `http://localhost:8081/`
- vulnbox API demo: `http://localhost:8082/api/status`
- vulnbox storage demo: `http://localhost:8083/files`

## Доступ к PostgreSQL

Параметры по умолчанию из `docker-compose.yml` и `.env.example`:

```text
Host: 127.0.0.1
Port: 5432
Database: baltctf
User: baltctf
Password: baltctf
```

Для TablePlus выбрать тип подключения `PostgreSQL`, указать параметры выше и отключить SSL или оставить режим `Prefer`.

Проверить фактический проброшенный порт:

```bash
docker compose port db 5432
```

Открыть `psql` внутри контейнера:

```bash
docker compose exec db psql -U baltctf -d baltctf
```

Основные таблицы:

```text
ctf_team
ctf_teammember
ctf_teamreservation
ctf_competitionsettings
ctf_service
ctf_round
ctf_flag
ctf_submission
ctf_servicestatus
auth_user
authtoken_token
```

## Демо-аккаунты

### Игроки

- примеры логинов:
  - `northern_lights_captain`
  - `amber_byte_player1`
- пароль для всех demo users:
  - `BaltCTFdemo123!`

### Администратор

- логин:
  - `admin`
- пароль:
  - `BaltCTFadmin123!`

## Как проверить checker flow

1. Войти под `admin`
2. Перейти на `/admin`
3. Создать или запустить раунд
4. Нажать `Run checker tick` или подождать автоцикл контейнера `checker`
5. Перейти на `/services` и посмотреть матрицу состояний

Checker tick выполняет реальные HTTP `put/get` проверки против demo-сервисов `atlas-board`, `signal-api` и `cold-storage`. Если running round отсутствует, checker-контейнер логирует idle-состояние и ждёт следующего цикла.

## Проверка тестами

Backend:

```bash
docker compose run --rm backend python manage.py test
```

Frontend:

```bash
cd frontend
npm run test:run
npm run build
```

Корневые npm-скрипты для удобства:

```bash
npm run up
npm run down
npm run backend:migrate
```

## Если менялись зависимости

### Python

Если менялся `backend/requirements.txt` или `checker/requirements.txt`:

```bash
docker compose build backend checker
```

### Frontend

Если менялся `frontend/package.json`:

```bash
docker compose build frontend
```

## Частые проблемы

### Не применяются новые Python-пакеты

Пересобрать образы:

```bash
docker compose build backend checker
```

### Vite ругается на Sass

Пересобрать frontend:

```bash
docker compose build frontend
docker compose up frontend
```

### После изменений UI не обновился

Обычно помогает полный restart:

```bash
docker compose down
docker compose up --build
```
