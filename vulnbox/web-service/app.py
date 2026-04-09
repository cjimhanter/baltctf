from datetime import datetime, UTC

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
BOARD_POSTS: dict[str, dict[str, dict]] = {}


def get_team_posts(team_slug: str) -> dict[str, dict]:
    return BOARD_POSTS.setdefault(team_slug, {})


@app.get("/")
def index():
    return {
        "service": "atlas-board",
        "status": "ok",
        "description": "Demo team board with intentionally exposed leak endpoint.",
    }


@app.post("/teams/<team_slug>/posts")
def create_post(team_slug: str):
    payload = request.get_json(silent=True) or {}
    slot = (payload.get("slot") or "").strip()
    headline = (payload.get("headline") or "Untitled incident report").strip()
    body = payload.get("body") or ""
    if not slot or not body:
        return jsonify({"message": "slot and body are required"}), 400

    post = {
        "slot": slot,
        "headline": headline,
        "body": body,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    get_team_posts(team_slug)[slot] = post
    return (
        jsonify(
            {
                "ok": True,
                "team": team_slug,
                "post": post,
                "preview_url": f"/teams/{team_slug}/posts/{slot}",
            }
        ),
        201,
    )


@app.get("/teams/<team_slug>/posts/<slot>")
def view_post(team_slug: str, slot: str):
    post = get_team_posts(team_slug).get(slot)
    if post is None:
        return jsonify({"message": "post not found"}), 404

    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>{{ team_slug }} :: {{ post.headline }}</title>
          </head>
          <body>
            <main>
              <h1>{{ post.headline }}</h1>
              <p>Team space: {{ team_slug }}</p>
              <article>{{ post.body }}</article>
            </main>
          </body>
        </html>
        """,
        team_slug=team_slug,
        post=post,
    )


@app.get("/teams/<team_slug>/feed")
def team_feed(team_slug: str):
    posts = list(get_team_posts(team_slug).values())
    return {"team": team_slug, "posts": posts}


@app.get("/leak-board")
def leak_board():
    team_slug = (request.args.get("team") or "").strip()
    if not team_slug:
        return jsonify({"message": "team is required"}), 400
    return {"team": team_slug, "posts": list(get_team_posts(team_slug).values())}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
