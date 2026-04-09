from __future__ import annotations

from .base import (
    CheckerCorruptError,
    build_url,
    ensure_status_code,
    read_base_url,
)


BASE_URL = read_base_url("ATLAS_BOARD_BASE_URL", "http://localhost:8081")


def run(*, session, team, flag, round_obj, timeout_seconds: float) -> str:
    slot = f"round-{round_obj.number}-primary-flag"
    create_response = session.post(
        build_url(BASE_URL, f"/teams/{team.slug}/posts"),
        json={
            "slot": slot,
            "headline": f"Round {round_obj.number} incident log",
            "body": flag.value,
        },
        timeout=timeout_seconds,
    )
    ensure_status_code(
        create_response,
        {200, 201},
        message=f"Atlas Board rejected flag placement for {team.slug}",
    )

    fetch_response = session.get(
        build_url(BASE_URL, f"/teams/{team.slug}/posts/{slot}"),
        timeout=timeout_seconds,
    )
    ensure_status_code(
        fetch_response,
        {200},
        message=f"Atlas Board could not read back the stored post for {team.slug}",
    )
    if flag.value not in fetch_response.text:
        raise CheckerCorruptError("Atlas Board returned the post, but the flag body was corrupted.")

    return f"Atlas Board stored and rendered the round flag for {team.slug}."
