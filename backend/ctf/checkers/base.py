from __future__ import annotations

import os
from collections.abc import Iterable


class CheckerFailure(RuntimeError):
    pass


class CheckerDownError(CheckerFailure):
    pass


class CheckerMumbleError(CheckerFailure):
    pass


class CheckerCorruptError(CheckerFailure):
    pass


def read_base_url(env_name: str, default: str) -> str:
    return os.getenv(env_name, default).rstrip("/")


def read_timeout_seconds() -> float:
    raw_value = os.getenv("CHECKER_SERVICE_REQUEST_TIMEOUT_SECONDS", "5").strip()
    try:
        return max(1.0, float(raw_value))
    except ValueError:
        return 5.0


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def ensure_status_code(response, expected_statuses: Iterable[int], *, message: str) -> None:
    if response.status_code not in set(expected_statuses):
        raise CheckerMumbleError(f"{message} (HTTP {response.status_code}).")
