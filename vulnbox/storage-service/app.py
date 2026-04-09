from datetime import datetime, UTC

from flask import Flask, Response, jsonify, request

app = Flask(__name__)
STORAGE: dict[str, dict[str, dict]] = {}


def get_team_files(team_slug: str) -> dict[str, dict]:
    return STORAGE.setdefault(team_slug, {})


@app.get("/files")
def files():
    return {
        "service": "cold-storage",
        "status": "ok",
        "description": "Demo storage service with intentionally unprotected raw file reads.",
    }


@app.post("/files/<team_slug>/upload")
def upload_file(team_slug: str):
    payload = request.get_json(silent=True) or {}
    path = (payload.get("path") or "").strip()
    content = payload.get("content") or ""
    if not path or not content:
        return jsonify({"message": "path and content are required"}), 400

    file_entry = {
        "path": path,
        "content": content,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    get_team_files(team_slug)[path] = file_entry
    return (
        jsonify(
            {
                "ok": True,
                "file": {
                    "path": path,
                    "updated_at": file_entry["updated_at"],
                },
                "download_url": f"/files/{team_slug}/download/{path}",
            }
        ),
        201,
    )


@app.get("/files/<team_slug>/download/<path:file_path>")
def download_file(team_slug: str, file_path: str):
    file_entry = get_team_files(team_slug).get(file_path)
    if file_entry is None:
        return jsonify({"message": "file not found"}), 404
    return Response(file_entry["content"], mimetype="text/plain")


@app.get("/files/<team_slug>/index")
def team_index(team_slug: str):
    return {"team": team_slug, "files": list(get_team_files(team_slug).values())}


@app.get("/files/raw/<path:raw_path>")
def raw_download(raw_path: str):
    team_slug, separator, file_path = raw_path.partition("/")
    if not separator or not file_path:
        return jsonify({"message": "raw path must include team and filename"}), 400

    file_entry = get_team_files(team_slug).get(file_path)
    if file_entry is None:
        return jsonify({"message": "file not found"}), 404
    return Response(file_entry["content"], mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
