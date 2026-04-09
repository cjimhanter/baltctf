from datetime import datetime, UTC

from flask import Flask, jsonify, request

app = Flask(__name__)
TEAM_RECORDS: dict[str, dict[str, dict]] = {}


def expected_token(team_slug: str) -> str:
    return f"signal-{team_slug}"


def get_team_records(team_slug: str) -> dict[str, dict]:
    return TEAM_RECORDS.setdefault(team_slug, {})


@app.get("/api/status")
def status():
    return {
        "service": "signal-api",
        "status": "ok",
        "description": "Demo JSON API with an intentionally exposed debug export.",
    }


@app.post("/api/teams/<team_slug>/records")
def create_record(team_slug: str):
    if request.headers.get("X-Team-Token") != expected_token(team_slug):
        return jsonify({"message": "invalid team token"}), 403

    payload = request.get_json(silent=True) or {}
    slot = (payload.get("slot") or "").strip()
    secret = (payload.get("secret") or "").strip()
    title = (payload.get("title") or "Untitled record").strip()
    if not slot or not secret:
        return jsonify({"message": "slot and secret are required"}), 400

    record = {
        "slot": slot,
        "secret": secret,
        "title": title,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    get_team_records(team_slug)[slot] = record
    return jsonify({"ok": True, "record": record}), 201


@app.get("/api/teams/<team_slug>/records/<slot>")
def get_record(team_slug: str, slot: str):
    if request.headers.get("X-Team-Token") != expected_token(team_slug):
        return jsonify({"message": "invalid team token"}), 403

    record = get_team_records(team_slug).get(slot)
    if record is None:
        return jsonify({"message": "record not found"}), 404

    return {"record": record}


@app.get("/api/debug/export")
def debug_export():
    team_slug = (request.args.get("team") or "").strip()
    if not team_slug:
        return jsonify({"message": "team is required"}), 400
    return {"team": team_slug, "records": list(get_team_records(team_slug).values())}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
