from __future__ import annotations

from .base import (
    CheckerCorruptError,
    build_url,
    ensure_status_code,
    read_base_url,
)


BASE_URL = read_base_url("COLD_STORAGE_BASE_URL", "http://localhost:8083")


def run(*, session, team, flag, round_obj, timeout_seconds: float) -> str:
    filename = f"round-{round_obj.number}-backup.txt"
    upload_response = session.post(
        build_url(BASE_URL, f"/files/{team.slug}/upload"),
        json={
            "path": filename,
            "content": flag.value,
        },
        timeout=timeout_seconds,
    )
    ensure_status_code(
        upload_response,
        {200, 201},
        message=f"Cold Storage rejected upload for {team.slug}",
    )

    download_response = session.get(
        build_url(BASE_URL, f"/files/{team.slug}/download/{filename}"),
        timeout=timeout_seconds,
    )
    ensure_status_code(
        download_response,
        {200},
        message=f"Cold Storage could not return the uploaded file for {team.slug}",
    )
    if download_response.text.strip() != flag.value:
        raise CheckerCorruptError("Cold Storage returned the file, but the flag contents mismatched.")

    return f"Cold Storage uploaded and downloaded the round file for {team.slug}."
