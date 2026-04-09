from __future__ import annotations

import os
import time
from typing import Any

import requests


def log(message: str) -> None:
    print(f"checker: {message}", flush=True)


def read_float_env(name: str, default: float) -> float:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        return float(raw_value)
    except ValueError:
        log(f"invalid {name}={raw_value!r}; falling back to {default}.")
        return default


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def parse_error_message(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        return payload.get("message") or payload.get("detail") or f"HTTP {response.status_code}"

    return response.text.strip() or f"HTTP {response.status_code}"


def authenticate(
    session: requests.Session,
    base_url: str,
    username: str,
    password: str,
    timeout_seconds: float,
) -> str:
    response = session.post(
        build_url(base_url, "/auth/login/"),
        json={
            "username": username,
            "password": password,
        },
        timeout=timeout_seconds,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"authentication failed: {parse_error_message(response)}")

    payload = response.json()
    token = payload.get("token")
    if not token:
        raise RuntimeError("authentication succeeded without returning an API token.")

    authenticated_user = payload.get("user", {}).get("username") or username
    log(f"authenticated as {authenticated_user}.")
    return token


def trigger_checker_tick(
    session: requests.Session,
    base_url: str,
    token: str,
    timeout_seconds: float,
) -> dict[str, Any] | None:
    response = session.post(
        build_url(base_url, "/admin/checker/tick/"),
        headers={
            "Authorization": f"Token {token}",
        },
        timeout=timeout_seconds,
    )

    if response.status_code in {401, 403}:
        raise PermissionError(parse_error_message(response))
    if response.status_code == 409:
        log(f"idle: {parse_error_message(response)}")
        return None
    if response.status_code >= 400:
        raise RuntimeError(f"checker tick failed: {parse_error_message(response)}")

    return response.json()


def main() -> None:
    api_base_url = os.getenv("CHECKER_API_BASE_URL", "http://backend:8000/api")
    admin_username = os.getenv("CHECKER_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("CHECKER_ADMIN_PASSWORD", "BaltCTFadmin123!")
    interval_seconds = read_float_env("CHECKER_INTERVAL_SECONDS", 60.0)
    timeout_seconds = read_float_env("CHECKER_REQUEST_TIMEOUT_SECONDS", 10.0)

    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    token = ""

    log(f"starting loop with interval={interval_seconds:.0f}s against {api_base_url}.")

    while True:
        if not token:
            try:
                token = authenticate(
                    session=session,
                    base_url=api_base_url,
                    username=admin_username,
                    password=admin_password,
                    timeout_seconds=timeout_seconds,
                )
            except (requests.RequestException, RuntimeError) as error:
                log(str(error))
                time.sleep(interval_seconds)
                continue

        try:
            payload = trigger_checker_tick(
                session=session,
                base_url=api_base_url,
                token=token,
                timeout_seconds=timeout_seconds,
            )
        except PermissionError as error:
            log(f"authorization rejected: {error}. Re-authenticating on the next cycle.")
            token = ""
            time.sleep(interval_seconds)
            continue
        except (requests.RequestException, RuntimeError) as error:
            log(str(error))
            time.sleep(interval_seconds)
            continue

        if payload is not None:
            tick = payload.get("checker_tick", {})
            round_number = tick.get("round", {}).get("number", "?")
            statuses_processed = tick.get("statuses_processed", 0)
            created_flags = tick.get("created_flags", 0)
            status_breakdown = tick.get("status_breakdown", {})
            log(
                "tick completed for round "
                f"{round_number}: statuses={statuses_processed}, "
                f"created_flags={created_flags}, breakdown={status_breakdown}."
            )

        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
