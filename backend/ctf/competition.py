from __future__ import annotations

import requests
import secrets
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .checkers import (
    CheckerCorruptError,
    CheckerDownError,
    CheckerMumbleError,
    run_service_checker,
)
from .models import Flag, Round, Service, ServiceStatus, Team


@dataclass
class CheckerTickResult:
    round: Round
    created_flags: int
    statuses_processed: int
    status_breakdown: dict[str, int]
    reported_at: str


def generate_flag_value(round_obj: Round, team: Team, service: Service) -> str:
    token = secrets.token_hex(10).upper()
    return f"BALTCTF{{R{round_obj.number}_T{team.id}_S{service.id}_{token}}}"


def ensure_flags_for_round(round_obj: Round) -> int:
    created_count = 0
    teams = Team.objects.filter(
        is_active=True,
        moderation_status=Team.ModerationStatus.APPROVED,
    ).order_by("id")
    services = Service.objects.filter(is_active=True).order_by("id")

    for team in teams:
        for service in services:
            _, created = Flag.objects.get_or_create(
                round=round_obj,
                team=team,
                service=service,
                defaults={
                    "value": generate_flag_value(round_obj, team, service),
                },
            )
            if created:
                created_count += 1

    return created_count


def _run_service_check(session, round_obj: Round, team: Team, service: Service, flag: Flag):
    timeout_seconds = 5.0
    try:
        from .checkers.base import read_timeout_seconds

        timeout_seconds = read_timeout_seconds()
    except Exception:
        timeout_seconds = 5.0

    try:
        message = run_service_checker(
            service.slug,
            session=session,
            team=team,
            flag=flag,
            round_obj=round_obj,
            timeout_seconds=timeout_seconds,
        )
        return ServiceStatus.Status.UP, message
    except KeyError:
        return (
            ServiceStatus.Status.DOWN,
            f"{service.name}: no checker is configured for slug '{service.slug}'.",
        )
    except CheckerCorruptError as error:
        return ServiceStatus.Status.CORRUPT, str(error)
    except CheckerMumbleError as error:
        return ServiceStatus.Status.MUMBLE, str(error)
    except CheckerDownError as error:
        return ServiceStatus.Status.DOWN, str(error)
    except requests.RequestException as error:
        return (
            ServiceStatus.Status.DOWN,
            f"{service.name}: network error while reaching the demo vulnbox ({error}).",
        )
    except ValueError as error:
        return (
            ServiceStatus.Status.MUMBLE,
            f"{service.name}: checker received malformed data ({error}).",
        )


def run_checker_tick(round_obj: Round) -> CheckerTickResult:
    if round_obj.state != Round.State.RUNNING:
        raise ValidationError("Checker tick requires a running round.")

    created_flags = ensure_flags_for_round(round_obj)
    teams = list(
        Team.objects.filter(
            is_active=True,
            moderation_status=Team.ModerationStatus.APPROVED,
        ).order_by("id")
    )
    services = list(Service.objects.filter(is_active=True).order_by("id"))
    flags = {
        (flag.team_id, flag.service_id): flag
        for flag in Flag.objects.select_related("team", "service", "round").filter(
            round=round_obj,
            team__in=teams,
            service__in=services,
        )
    }
    status_breakdown = {
        ServiceStatus.Status.UP: 0,
        ServiceStatus.Status.MUMBLE: 0,
        ServiceStatus.Status.CORRUPT: 0,
        ServiceStatus.Status.DOWN: 0,
    }
    statuses_processed = 0

    with requests.Session() as session:
        session.headers.update({"Accept": "application/json, text/html;q=0.9, text/plain;q=0.8"})
        with transaction.atomic():
            for team in teams:
                for service in services:
                    flag = flags.get((team.id, service.id))
                    if flag is None:
                        status = ServiceStatus.Status.CORRUPT
                        message = (
                            f"{service.name}: the round flag was missing in the controller database."
                        )
                    else:
                        status, message = _run_service_check(
                            session=session,
                            round_obj=round_obj,
                            team=team,
                            service=service,
                            flag=flag,
                        )
                    points_awarded = ServiceStatus.suggested_points(status)
                    ServiceStatus.objects.update_or_create(
                        round=round_obj,
                        team=team,
                        service=service,
                        defaults={
                            "status": status,
                            "points_awarded": points_awarded,
                            "message": message,
                        },
                    )
                    status_breakdown[status] += 1
                    statuses_processed += 1

    return CheckerTickResult(
        round=round_obj,
        created_flags=created_flags,
        statuses_processed=statuses_processed,
        status_breakdown=status_breakdown,
        reported_at=timezone.now().isoformat(),
    )
