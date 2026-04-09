from __future__ import annotations

from .base import (
    CheckerCorruptError,
    build_url,
    ensure_status_code,
    read_base_url,
)


BASE_URL = read_base_url("SIGNAL_API_BASE_URL", "http://localhost:8082")


def _build_token(team_slug: str) -> str:
    return f"signal-{team_slug}"


def run(*, session, team, flag, round_obj, timeout_seconds: float) -> str:
    slot = f"round-{round_obj.number}-primary-flag"
    headers = {
        "X-Team-Token": _build_token(team.slug),
    }

    create_response = session.post(
        build_url(BASE_URL, f"/api/teams/{team.slug}/records"),
        json={
            "slot": slot,
            "secret": flag.value,
            "title": f"Round {round_obj.number} telemetry",
        },
        headers=headers,
        timeout=timeout_seconds,
    )
    ensure_status_code(
        create_response,
        {200, 201},
        message=f"Signal API rejected flag placement for {team.slug}",
    )

    fetch_response = session.get(
        build_url(BASE_URL, f"/api/teams/{team.slug}/records/{slot}"),
        headers=headers,
        timeout=timeout_seconds,
    )
    ensure_status_code(
        fetch_response,
        {200},
        message=f"Signal API could not fetch the stored record for {team.slug}",
    )
    payload = fetch_response.json()
    returned_secret = ((payload.get("record") or {}).get("secret") or "").strip()
    if returned_secret != flag.value:
        raise CheckerCorruptError("Signal API returned a record, but the stored secret mismatched.")

    return f"Signal API stored and returned the round secret for {team.slug}."
