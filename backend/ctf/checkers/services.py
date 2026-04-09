from __future__ import annotations

from . import atlas_board, cold_storage, signal_api


SERVICE_CHECKERS = {
    "atlas-board": atlas_board.run,
    "signal-api": signal_api.run,
    "cold-storage": cold_storage.run,
}


def run_service_checker(service_slug: str, **kwargs) -> str:
    checker = SERVICE_CHECKERS.get(service_slug)
    if checker is None:
        raise KeyError(service_slug)
    return checker(**kwargs)
