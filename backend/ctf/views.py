import json
import re
import secrets
from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models, transaction
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from rest_framework.authtoken.models import Token

from .competition import ensure_flags_for_round, run_checker_tick
from .models import (
    CompetitionSettings,
    Flag,
    Round,
    Service,
    ServiceStatus,
    Submission,
    Team,
    TeamMember,
    TeamReservation,
)

User = get_user_model()

SUBMISSION_RATE_LIMIT = 10
SUBMISSION_RATE_WINDOW_SECONDS = 60
ATTACK_POINTS_PER_FLAG = 25
MAX_TEAM_MEMBERS = 6
SERVICE_STATUS_ORDER = [
    ServiceStatus.Status.UP,
    ServiceStatus.Status.MUMBLE,
    ServiceStatus.Status.CORRUPT,
    ServiceStatus.Status.DOWN,
]
SERVICE_STATUS_HISTORY_LIMIT = 6
SUBMISSION_HISTORY_LIMIT = 12
CHECKER_ISSUE_LIMIT = 6


API_MESSAGE_TRANSLATIONS = {
    "ru": {
        "Request body must be valid JSON.": "Тело запроса должно быть корректным JSON.",
        "Authentication token is required.": "Требуется токен авторизации.",
        "Staff access is required for this action.": "Для этого действия требуется доступ оператора.",
        "User is not assigned to a team.": "Пользователь не привязан к команде.",
        "Captain role is required for this action.": "Для этого действия нужна роль капитана.",
        "Member role must be either 'captain' or 'player'.": "Роль участника должна быть 'captain' или 'player'.",
        "Team member not found.": "Участник команды не найден.",
        "Each participant must have a username.": "У каждого участника должно быть имя пользователя.",
        "Each participant must be represented as an object.": "Каждый участник должен быть передан как объект.",
        "Each team member must use a unique username.": "У каждого участника команды должно быть уникальное имя пользователя.",
        "Team name is required.": "Укажите название команды.",
        "Team slug could not be generated.": "Не удалось сформировать slug команды.",
        "Team slug could not be generated. Provide team_slug explicitly.": "Не удалось сформировать slug команды. Укажите team_slug явно.",
        "A team with this name already exists.": "Команда с таким названием уже существует.",
        "A team with this slug already exists.": "Команда с таким slug уже существует.",
        "Team moderation status must be approved, pending, or suspended.": "Статус модерации команды должен быть approved, pending или suspended.",
        "Captain username is required.": "Укажите имя пользователя капитана.",
        "Contact email is required.": "Укажите контактный email.",
        "This team name is already reserved.": "Это название команды уже зарезервировано.",
        "This team slug is already reserved.": "Этот slug команды уже зарезервирован.",
        "Registration is currently closed.": "Регистрация сейчас закрыта.",
        "Captain payload must be an object.": "Данные капитана должны быть объектом.",
        "Participants payload must be a list.": "Список участников должен быть массивом.",
        "An approved reservation token is required for registration.": "Для регистрации нужен одобренный токен резервирования.",
        "Reservation token is invalid or not approved.": "Токен резервирования недействителен или не одобрен.",
        "Reservation token has expired.": "Срок действия токена резервирования истёк.",
        "Reservation token does not match the selected team name.": "Токен резервирования не соответствует выбранному названию команды.",
        "Reservation token does not match the selected team slug.": "Токен резервирования не соответствует выбранному slug команды.",
        "Username and password are required.": "Укажите имя пользователя и пароль.",
        "Invalid username or password.": "Неверное имя пользователя или пароль.",
        "Logged out successfully.": "Сессия завершена.",
        "Team profile updated.": "Профиль команды обновлён.",
        "Team must always have at least one captain.": "В команде всегда должен оставаться хотя бы один капитан.",
        "You cannot remove your own account through the team management API.": "Нельзя удалить собственную учётную запись через API управления командой.",
        "Only approved active teams can submit flags.": "Флаги могут отправлять только одобренные активные команды.",
        "Flag value is required.": "Укажите значение флага.",
        "Flag value is too long.": "Значение флага слишком длинное.",
        "There is no active round for flag submission.": "Сейчас нет активного раунда для отправки флагов.",
        "Too many submissions in a short time. Please wait a moment before retrying.": "Слишком много отправок за короткое время. Подождите немного перед повторной попыткой.",
        "Unknown flag.": "Неизвестный флаг.",
        "You cannot submit your own team's flag.": "Нельзя отправлять флаг своей команды.",
        "This flag is not valid for the current round.": "Этот флаг не подходит для текущего раунда.",
        "This flag belongs to a round that has not started yet.": "Этот флаг относится к раунду, который ещё не начался.",
        "This flag has expired.": "Срок действия этого флага истёк.",
        "This flag has already been submitted successfully.": "Этот флаг уже был успешно отправлен.",
        "registration_ends_at must be later than registration_starts_at.": "registration_ends_at должен быть позже registration_starts_at.",
        "round_duration_minutes must be positive.": "round_duration_minutes должен быть положительным.",
        "round_break_minutes cannot be negative.": "round_break_minutes не может быть отрицательным.",
        "Round schedule count must be an integer.": "Количество раундов в расписании должно быть целым числом.",
        "Round schedule count must be between 1 and 10.": "Количество раундов в расписании должно быть от 1 до 10.",
        "Service name is required.": "Укажите название сервиса.",
        "Service slug could not be generated.": "Не удалось сформировать slug сервиса.",
        "A service with this name already exists.": "Сервис с таким названием уже существует.",
        "A service with this slug already exists.": "Сервис с таким slug уже существует.",
        "Service port must be an integer.": "Порт сервиса должен быть целым числом.",
        "Service port must be between 1 and 65535.": "Порт сервиса должен быть от 1 до 65535.",
        "Reservation not found.": "Резервирование не найдено.",
        "Claimed reservations cannot be modified.": "Использованное резервирование нельзя изменить.",
        "Team not found.": "Команда не найдена.",
        "Service not found.": "Сервис не найден.",
        "Round number must be an integer.": "Номер раунда должен быть целым числом.",
        "A round with this number already exists.": "Раунд с таким номером уже существует.",
        "Round not found.": "Раунд не найден.",
        "Finished rounds cannot be restarted.": "Завершённые раунды нельзя запускать повторно.",
        "Only a running round can be finished.": "Завершить можно только running round.",
        "There is no running round for the checker tick.": "Нет running round для запуска checker tick.",
        "Enter a valid email address.": "Введите корректный email-адрес.",
        "This password is too short. It must contain at least 8 characters.": "Пароль слишком короткий. Он должен содержать минимум 8 символов.",
        "This password is too common.": "Этот пароль слишком распространён.",
        "This password is entirely numeric.": "Пароль не должен состоять только из цифр.",
    }
}

API_MESSAGE_PATTERNS = {
    "ru": [
        (
            re.compile(r"^Team registration is limited to (?P<count>\d+) members\.$"),
            "Регистрация команды ограничена {count} участниками.",
        ),
        (
            re.compile(r"^Team size is limited to (?P<count>\d+) members\.$"),
            "Размер команды ограничен {count} участниками.",
        ),
        (
            re.compile(r"^User '(?P<username>[^']+)' must have a password\.$"),
            "У пользователя '{username}' должен быть пароль.",
        ),
        (
            re.compile(r"^Username '(?P<username>[^']+)' is already taken\.$"),
            "Имя пользователя '{username}' уже занято.",
        ),
        (
            re.compile(r"^Member '(?P<username>[^']+)' is already a (?P<role>[^.]+)\.$"),
            "Участник '{username}' уже имеет роль {role}.",
        ),
        (
            re.compile(r"^Member '(?P<username>[^']+)' role updated to (?P<role>[^.]+)\.$"),
            "Роль участника '{username}' изменена на {role}.",
        ),
        (
            re.compile(r"^Member '(?P<username>[^']+)' removed from the team\.$"),
            "Участник '{username}' удалён из команды.",
        ),
        (
            re.compile(r"^Round (?P<number>\d+) is already running\.$"),
            "Раунд {number} уже запущен.",
        ),
        (
            re.compile(
                r"^Round (?P<number>\d+) is already running\. Finish it before starting another round\.$"
            ),
            "Раунд {number} уже запущен. Завершите его перед запуском другого раунда.",
        ),
    ]
}


def _get_request_language(request) -> str:
    if request is None:
        return "en"

    accept_language = request.headers.get("Accept-Language", "")
    for language_range in accept_language.split(","):
        language_code = language_range.split(";")[0].strip().lower()
        if language_code == "ru" or language_code.startswith("ru-"):
            return "ru"
        if language_code == "en" or language_code.startswith("en-"):
            return "en"

    return "en"


def _localize_api_message(message: str, request=None) -> str:
    language_code = _get_request_language(request)
    if language_code == "en":
        return message

    translations = API_MESSAGE_TRANSLATIONS.get(language_code, {})
    patterns = API_MESSAGE_PATTERNS.get(language_code, [])
    localized_parts = []

    for part in message.split("; "):
        translated = translations.get(part)
        if translated is None:
            for pattern, template in patterns:
                match = pattern.match(part)
                if match:
                    translated = template.format(**match.groupdict())
                    break
        localized_parts.append(translated or part)

    return "; ".join(localized_parts)


def _json_error(message: str, status: int = 400, request=None, **extra):
    payload = {"ok": False, "message": _localize_api_message(message, request)}
    payload.update(extra)
    return JsonResponse(payload, status=status)


def _parse_json_body(request):
    if not request.body:
        return {}

    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValidationError("Request body must be valid JSON.")


def _extract_token_key(request) -> str | None:
    authorization = request.headers.get("Authorization", "").strip()
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) != 2:
        return None

    scheme, token_key = parts
    if scheme.lower() not in {"token", "bearer"}:
        return None

    return token_key.strip()


def _get_request_user(request):
    token_key = _extract_token_key(request)
    if not token_key:
        return None

    token = Token.objects.select_related("user").filter(key=token_key).first()
    return token.user if token else None


def _require_staff_user(request):
    user = _get_request_user(request)
    if user is None:
        return None, _json_error(
            "Authentication token is required.",
            status=401,
            request=request,
        )
    if not user.is_staff:
        return None, _json_error(
            "Staff access is required for this action.",
            status=403,
            request=request,
        )
    return user, None


def _serialize_team(team: Team) -> dict:
    return {
        "id": team.id,
        "name": team.name,
        "slug": team.slug,
        "affiliation": team.affiliation,
        "contact_email": team.contact_email,
        "is_active": team.is_active,
        "moderation_status": team.moderation_status,
        "moderation_status_label": team.get_moderation_status_display(),
        "moderation_note": team.moderation_note,
    }


def _serialize_member(member: TeamMember) -> dict:
    return {
        "id": member.user_id,
        "username": member.user.username,
        "email": member.user.email,
        "first_name": member.user.first_name,
        "last_name": member.user.last_name,
        "role": member.role,
        "role_label": member.get_role_display(),
    }


def _serialize_round(round_obj: Round | None) -> dict | None:
    if round_obj is None:
        return None

    return {
        "id": round_obj.id,
        "number": round_obj.number,
        "state": round_obj.state,
        "state_label": round_obj.get_state_display(),
        "started_at": round_obj.started_at.isoformat(),
        "finished_at": round_obj.finished_at.isoformat() if round_obj.finished_at else None,
    }


def _serialize_service(service: Service) -> dict:
    return {
        "id": service.id,
        "name": service.name,
        "slug": service.slug,
        "description": service.description,
        "port": service.port,
    }


def _serialize_submission(submission: Submission) -> dict:
    target_team = submission.flag.team if submission.flag_id else None
    target_service = submission.flag.service if submission.flag_id else None
    target_round = submission.flag.round if submission.flag_id else None

    return {
        "id": submission.id,
        "submitted_value": submission.submitted_value,
        "status": submission.status,
        "status_label": submission.get_status_display(),
        "points_awarded": submission.points_awarded,
        "message": submission.message,
        "submitted_at": submission.submitted_at.isoformat(),
        "submitted_by": (
            {
                "id": submission.submitted_by_id,
                "username": submission.submitted_by.username,
            }
            if submission.submitted_by_id
            else None
        ),
        "submitting_team": {
            "id": submission.submitting_team_id,
            "name": submission.submitting_team.name,
            "slug": submission.submitting_team.slug,
        },
        "target_team": (
            {
                "id": target_team.id,
                "name": target_team.name,
                "slug": target_team.slug,
            }
            if target_team
            else None
        ),
        "service": (
            {
                "id": target_service.id,
                "name": target_service.name,
                "slug": target_service.slug,
            }
            if target_service
            else None
        ),
        "round": _serialize_round(target_round) if target_round else None,
        "processed_at": (
            submission.processed_at.isoformat() if submission.processed_at else None
        ),
    }


def _serialize_admin_team(team: Team) -> dict:
    payload = _serialize_team(team)
    payload["member_count"] = getattr(team, "member_count", None)
    payload["submission_count"] = getattr(team, "submission_count", None)
    return payload


def _serialize_settings(settings_obj: CompetitionSettings) -> dict:
    return {
        "registration_open": settings_obj.registration_open,
        "registration_starts_at": (
            settings_obj.registration_starts_at.isoformat()
            if settings_obj.registration_starts_at
            else None
        ),
        "registration_ends_at": (
            settings_obj.registration_ends_at.isoformat()
            if settings_obj.registration_ends_at
            else None
        ),
        "reservation_required_for_registration": (
            settings_obj.reservation_required_for_registration
        ),
        "auto_approve_registrations": settings_obj.auto_approve_registrations,
        "round_duration_minutes": settings_obj.round_duration_minutes,
        "round_break_minutes": settings_obj.round_break_minutes,
        "registration_available": settings_obj.is_registration_available(),
    }


def _serialize_team_reservation(reservation: TeamReservation) -> dict:
    return {
        "id": reservation.id,
        "name": reservation.name,
        "slug": reservation.slug,
        "contact_email": reservation.contact_email,
        "captain_username": reservation.captain_username,
        "token": reservation.token,
        "status": reservation.status,
        "status_label": reservation.get_status_display(),
        "note": reservation.note,
        "expires_at": reservation.expires_at.isoformat() if reservation.expires_at else None,
        "created_at": reservation.created_at.isoformat(),
        "reviewed_at": reservation.reviewed_at.isoformat() if reservation.reviewed_at else None,
    }


def _serialize_admin_service(service: Service) -> dict:
    payload = _serialize_service(service)
    payload["flag_count"] = getattr(service, "flag_count", None)
    payload["status_count"] = getattr(service, "status_count", None)
    return payload


def _serialize_admin_round(round_obj: Round) -> dict:
    payload = _serialize_round(round_obj)
    payload["flag_count"] = getattr(round_obj, "flag_count", None)
    payload["accepted_submission_count"] = getattr(
        round_obj,
        "accepted_submission_count",
        None,
    )
    return payload


def _serialize_checker_tick_result(result) -> dict:
    return {
        "round": _serialize_round(result.round),
        "created_flags": result.created_flags,
        "statuses_processed": result.statuses_processed,
        "status_breakdown": result.status_breakdown,
        "reported_at": result.reported_at,
    }


def _get_settings() -> CompetitionSettings:
    return CompetitionSettings.get_solo()


def _get_active_approved_teams():
    return Team.objects.filter(
        is_active=True,
        moderation_status=Team.ModerationStatus.APPROVED,
    )


def _get_current_round() -> Round | None:
    current_round = Round.objects.filter(state=Round.State.RUNNING).order_by("-number").first()
    if current_round:
        return current_round

    return Round.objects.order_by("-number").first()


def _get_team_membership(user):
    if not user:
        return None

    return (
        TeamMember.objects.select_related("team", "user")
        .filter(user=user)
        .first()
    )


def _require_team_membership(request):
    user = _get_request_user(request)
    if user is None:
        return None, None, _json_error(
            "Authentication token is required.",
            status=401,
            request=request,
        )

    membership = _get_team_membership(user)
    if membership is None:
        return user, None, _json_error(
            "User is not assigned to a team.",
            status=403,
            request=request,
        )

    return user, membership, None


def _require_team_captain(request):
    user, membership, error_response = _require_team_membership(request)
    if error_response is not None:
        return user, membership, error_response

    if membership.role != TeamMember.Role.CAPTAIN:
        return user, membership, _json_error(
            "Captain role is required for this action.",
            status=403,
            request=request,
        )

    return user, membership, None


def _validate_member_role(role: str) -> str:
    if role not in TeamMember.Role.values:
        raise ValidationError("Member role must be either 'captain' or 'player'.")
    return role


def _get_team_member_or_404(team: Team, user_id: int):
    membership = (
        TeamMember.objects.select_related("user", "team")
        .filter(team=team, user_id=user_id)
        .first()
    )
    if membership is None:
        raise ValidationError("Team member not found.")
    return membership


def _empty_counts(keys: list[str]) -> dict[str, int]:
    return {key: 0 for key in keys}


def _serialize_status_breakdown(
    rows,
    keys: list[str],
    include_unknown: int | None = None,
) -> dict[str, int]:
    counts = _empty_counts(keys)
    for row in rows:
        counts[row["status"]] = row["count"]
    if include_unknown is not None:
        counts["unknown"] = include_unknown
    return counts


def _build_dashboard_summary(current_round: Round | None) -> dict:
    submission_summary = Submission.objects.aggregate(
        submission_count=models.Count("id"),
        accepted_submissions_count=models.Count(
            "id",
            filter=models.Q(status=Submission.Status.ACCEPTED),
        ),
        rejected_submissions_count=models.Count(
            "id",
            filter=models.Q(status=Submission.Status.REJECTED),
        ),
        pending_submissions_count=models.Count(
            "id",
            filter=models.Q(status=Submission.Status.PENDING),
        ),
        attack_points_total=models.Sum(
            "points_awarded",
            filter=models.Q(status=Submission.Status.ACCEPTED),
        ),
        latest_submission_at=models.Max("submitted_at"),
    )
    checker_summary = ServiceStatus.objects.aggregate(
        checker_status_count=models.Count("id"),
        defense_points_total=models.Sum("points_awarded"),
        latest_checker_report_at=models.Max("reported_at"),
    )
    status_breakdown = _serialize_status_breakdown(
        ServiceStatus.objects.values("status").annotate(count=models.Count("id")),
        SERVICE_STATUS_ORDER,
    )
    current_round_status_breakdown = _empty_counts(SERVICE_STATUS_ORDER)
    if current_round is not None:
        current_round_status_breakdown = _serialize_status_breakdown(
            ServiceStatus.objects.filter(round=current_round)
            .values("status")
            .annotate(count=models.Count("id")),
            SERVICE_STATUS_ORDER,
        )

    submission_count = submission_summary["submission_count"] or 0
    accepted_count = submission_summary["accepted_submissions_count"] or 0

    return {
        "team_count": _get_active_approved_teams().count(),
        "service_count": Service.objects.filter(is_active=True).count(),
        "round_count": Round.objects.count(),
        "accepted_submissions_count": accepted_count,
        "rejected_submissions_count": submission_summary["rejected_submissions_count"] or 0,
        "pending_submissions_count": submission_summary["pending_submissions_count"] or 0,
        "submission_count": submission_count,
        "registered_users_count": TeamMember.objects.count(),
        "attack_points_total": submission_summary["attack_points_total"] or 0,
        "defense_points_total": checker_summary["defense_points_total"] or 0,
        "checker_status_count": checker_summary["checker_status_count"] or 0,
        "acceptance_rate": (
            round((accepted_count / submission_count) * 100)
            if submission_count
            else 0
        ),
        "checker_status_breakdown": status_breakdown,
        "current_round_status_breakdown": current_round_status_breakdown,
        "latest_submission_at": (
            submission_summary["latest_submission_at"].isoformat()
            if submission_summary["latest_submission_at"]
            else None
        ),
        "latest_checker_report_at": (
            checker_summary["latest_checker_report_at"].isoformat()
            if checker_summary["latest_checker_report_at"]
            else None
        ),
    }


def _build_scoreboard(
    services: list[Service],
    current_round: Round | None,
    teams: list[Team] | None = None,
) -> list[dict]:
    teams = teams if teams is not None else list(_get_active_approved_teams().order_by("name"))

    attack_totals = {
        row["submitting_team_id"]: row["total"] or 0
        for row in Submission.objects.filter(status=Submission.Status.ACCEPTED)
        .values("submitting_team_id")
        .annotate(total=models.Sum("points_awarded"))
    }
    submission_stats: dict[int, dict] = {}
    for row in (
        Submission.objects.values("submitting_team_id", "status")
        .annotate(
            count=models.Count("id"),
            total=models.Sum("points_awarded"),
        )
        .order_by()
    ):
        team_stats = submission_stats.setdefault(
            row["submitting_team_id"],
            {
                "submission_count": 0,
                "accepted_submission_count": 0,
                "rejected_submission_count": 0,
                "pending_submission_count": 0,
            },
        )
        status = row["status"]
        team_stats["submission_count"] += row["count"]
        team_stats[f"{status}_submission_count"] = row["count"]

    defense_totals = {
        row["team_id"]: row["total"] or 0
        for row in ServiceStatus.objects.values("team_id").annotate(total=models.Sum("points_awarded"))
    }
    defense_check_counts = {
        row["team_id"]: row["count"]
        for row in ServiceStatus.objects.values("team_id").annotate(count=models.Count("id"))
    }

    status_map: dict[tuple[int, int], ServiceStatus] = {}
    current_round_team_stats: dict[int, dict] = {}
    if current_round is not None:
        current_status_entries = list(
            ServiceStatus.objects.filter(round=current_round).select_related(
                "team",
                "service",
            )
        )
        status_map = {
            (status_entry.team_id, status_entry.service_id): status_entry
            for status_entry in current_status_entries
        }
        for status_entry in current_status_entries:
            team_stats = current_round_team_stats.setdefault(
                status_entry.team_id,
                {
                    "status_counts": _empty_counts(SERVICE_STATUS_ORDER),
                    "checked_count": 0,
                    "defense_points": 0,
                },
            )
            team_stats["status_counts"][status_entry.status] += 1
            team_stats["checked_count"] += 1
            team_stats["defense_points"] += status_entry.points_awarded

    scoreboard = []
    for team in teams:
        attack_points = attack_totals.get(team.id, 0)
        defense_points = defense_totals.get(team.id, 0)
        team_submission_stats = submission_stats.get(
            team.id,
            {
                "submission_count": 0,
                "accepted_submission_count": 0,
                "rejected_submission_count": 0,
                "pending_submission_count": 0,
            },
        )
        current_team_stats = current_round_team_stats.get(
            team.id,
            {
                "status_counts": _empty_counts(SERVICE_STATUS_ORDER),
                "checked_count": 0,
                "defense_points": 0,
            },
        )
        unknown_count = max(len(services) - current_team_stats["checked_count"], 0)
        service_breakdown = []

        for service in services:
            status_entry = status_map.get((team.id, service.id))
            service_breakdown.append(
                {
                    "service": _serialize_service(service),
                    "status": status_entry.status if status_entry else "unknown",
                    "status_label": status_entry.get_status_display() if status_entry else "No data",
                    "points_awarded": status_entry.points_awarded if status_entry else 0,
                    "message": status_entry.message if status_entry else "",
                }
            )

        scoreboard.append(
            {
                "team": _serialize_team(team),
                "attack_points": attack_points,
                "defense_points": defense_points,
                "total_points": attack_points + defense_points,
                "submission_count": team_submission_stats["submission_count"],
                "accepted_submission_count": team_submission_stats[
                    "accepted_submission_count"
                ],
                "rejected_submission_count": team_submission_stats[
                    "rejected_submission_count"
                ],
                "pending_submission_count": team_submission_stats[
                    "pending_submission_count"
                ],
                "defense_check_count": defense_check_counts.get(team.id, 0),
                "current_round_defense_points": current_team_stats["defense_points"],
                "service_health": {
                    **current_team_stats["status_counts"],
                    "unknown": unknown_count,
                    "checked_count": current_team_stats["checked_count"],
                    "issue_count": (
                        current_team_stats["status_counts"][ServiceStatus.Status.MUMBLE]
                        + current_team_stats["status_counts"][ServiceStatus.Status.CORRUPT]
                        + current_team_stats["status_counts"][ServiceStatus.Status.DOWN]
                        + unknown_count
                    ),
                },
                "service_breakdown": service_breakdown,
            }
        )

    scoreboard.sort(
        key=lambda entry: (
            -entry["total_points"],
            -entry["defense_points"],
            -entry["attack_points"],
            entry["team"]["name"].lower(),
        )
    )

    for index, entry in enumerate(scoreboard, start=1):
        entry["rank"] = index

    return scoreboard


def _build_service_stats(services: list[Service]) -> list[dict]:
    service_ids = [service.id for service in services]
    service_stats = {
        service.id: {
            "service": _serialize_service(service),
            "flag_count": 0,
            "accepted_submission_count": 0,
            "attack_points": 0,
            "defense_points": 0,
            "checker_status_count": 0,
            "status_counts": _empty_counts(SERVICE_STATUS_ORDER),
            "uptime_percent": 0,
        }
        for service in services
    }

    if not service_ids:
        return []

    for row in (
        Flag.objects.filter(service_id__in=service_ids)
        .values("service_id")
        .annotate(count=models.Count("id"))
    ):
        service_stats[row["service_id"]]["flag_count"] = row["count"]

    for row in (
        Submission.objects.filter(
            status=Submission.Status.ACCEPTED,
            flag__service_id__in=service_ids,
        )
        .values("flag__service_id")
        .annotate(
            count=models.Count("id"),
            total=models.Sum("points_awarded"),
        )
    ):
        service_stats[row["flag__service_id"]]["accepted_submission_count"] = row[
            "count"
        ]
        service_stats[row["flag__service_id"]]["attack_points"] = row["total"] or 0

    for row in (
        ServiceStatus.objects.filter(service_id__in=service_ids)
        .values("service_id", "status")
        .annotate(
            count=models.Count("id"),
            total=models.Sum("points_awarded"),
        )
    ):
        stats = service_stats[row["service_id"]]
        stats["status_counts"][row["status"]] = row["count"]
        stats["checker_status_count"] += row["count"]
        stats["defense_points"] += row["total"] or 0

    for stats in service_stats.values():
        checks = stats["checker_status_count"]
        stats["uptime_percent"] = (
            round((stats["status_counts"][ServiceStatus.Status.UP] / checks) * 100)
            if checks
            else 0
        )

    return list(service_stats.values())


def _build_round_stats(
    services: list[Service],
    teams: list[Team],
    limit: int = SERVICE_STATUS_HISTORY_LIMIT,
) -> list[dict]:
    rounds = list(Round.objects.order_by("-number")[:limit])
    if not rounds:
        return []

    round_ids = [round_obj.id for round_obj in rounds]
    expected_checks = len(services) * len(teams)
    round_stats = {
        round_obj.id: {
            **_serialize_round(round_obj),
            "accepted_submission_count": 0,
            "attack_points": 0,
            "defense_points": 0,
            "checker_status_count": 0,
            "status_counts": _empty_counts(SERVICE_STATUS_ORDER),
        }
        for round_obj in rounds
    }

    for row in (
        Submission.objects.filter(
            status=Submission.Status.ACCEPTED,
            flag__round_id__in=round_ids,
        )
        .values("flag__round_id")
        .annotate(
            count=models.Count("id"),
            total=models.Sum("points_awarded"),
        )
    ):
        stats = round_stats[row["flag__round_id"]]
        stats["accepted_submission_count"] = row["count"]
        stats["attack_points"] = row["total"] or 0

    for row in (
        ServiceStatus.objects.filter(round_id__in=round_ids)
        .values("round_id", "status")
        .annotate(
            count=models.Count("id"),
            total=models.Sum("points_awarded"),
        )
    ):
        stats = round_stats[row["round_id"]]
        stats["status_counts"][row["status"]] = row["count"]
        stats["checker_status_count"] += row["count"]
        stats["defense_points"] += row["total"] or 0

    for stats in round_stats.values():
        stats["unknown_status_count"] = max(
            expected_checks - stats["checker_status_count"],
            0,
        )

    return list(round_stats.values())


def _build_service_status_history(
    services: list[Service],
    teams: list[Team],
    limit: int = SERVICE_STATUS_HISTORY_LIMIT,
) -> list[dict]:
    rounds = list(Round.objects.order_by("-number")[:limit])
    if not rounds:
        return []

    round_ids = [round_obj.id for round_obj in rounds]
    expected_checks_per_service = len(teams)
    service_history = {
        (round_obj.id, service.id): {
            "service": _serialize_service(service),
            "status_counts": _empty_counts(SERVICE_STATUS_ORDER),
            "unknown": expected_checks_per_service,
            "checked_count": 0,
            "defense_points": 0,
            "latest_reported_at": None,
        }
        for round_obj in rounds
        for service in services
    }

    for row in (
        ServiceStatus.objects.filter(round_id__in=round_ids)
        .values("round_id", "service_id", "status")
        .annotate(
            count=models.Count("id"),
            total=models.Sum("points_awarded"),
            latest_reported_at=models.Max("reported_at"),
        )
    ):
        stats = service_history[(row["round_id"], row["service_id"])]
        stats["status_counts"][row["status"]] = row["count"]
        stats["checked_count"] += row["count"]
        stats["defense_points"] += row["total"] or 0
        latest_reported_at = row["latest_reported_at"]
        if latest_reported_at and (
            stats["latest_reported_at"] is None
            or latest_reported_at > stats["latest_reported_at"]
        ):
            stats["latest_reported_at"] = latest_reported_at

    history = []
    for round_obj in rounds:
        round_services = []
        for service in services:
            stats = service_history[(round_obj.id, service.id)]
            stats["unknown"] = max(
                expected_checks_per_service - stats["checked_count"],
                0,
            )
            stats["status_counts"]["unknown"] = stats["unknown"]
            stats["issue_count"] = (
                stats["status_counts"][ServiceStatus.Status.MUMBLE]
                + stats["status_counts"][ServiceStatus.Status.CORRUPT]
                + stats["status_counts"][ServiceStatus.Status.DOWN]
                + stats["unknown"]
            )
            stats["latest_reported_at"] = (
                stats["latest_reported_at"].isoformat()
                if stats["latest_reported_at"]
                else None
            )
            round_services.append(stats)

        history.append(
            {
                "round": _serialize_round(round_obj),
                "services": round_services,
            }
        )

    return history


def _build_dashboard_payload() -> dict:
    services = list(Service.objects.filter(is_active=True))
    teams = list(_get_active_approved_teams().order_by("name"))
    current_round = _get_current_round()
    recent_rounds = _build_round_stats(services, teams, limit=5)
    recent_activity = list(
        Submission.objects.select_related(
            "submitted_by",
            "submitting_team",
            "flag__team",
            "flag__service",
            "flag__round",
        )[:SUBMISSION_HISTORY_LIMIT]
    )
    service_status_history = _build_service_status_history(services, teams)

    scoreboard = _build_scoreboard(services, current_round, teams=teams)

    return {
        "summary": _build_dashboard_summary(current_round),
        "current_round": _serialize_round(current_round),
        "services": [_serialize_service(service) for service in services],
        "service_stats": _build_service_stats(services),
        "scoreboard": scoreboard,
        "recent_rounds": recent_rounds,
        "recent_activity": [_serialize_submission(submission) for submission in recent_activity],
        "submission_history": [
            _serialize_submission(submission) for submission in recent_activity
        ],
        "service_status_history": service_status_history,
    }


def _build_service_status_payload() -> dict:
    current_round = _get_current_round()
    services = list(Service.objects.filter(is_active=True))
    teams = list(_get_active_approved_teams().order_by("name"))

    status_map: dict[tuple[int, int], ServiceStatus] = {}
    latest_reported_at = None
    if current_round:
        current_status_entries = list(
            ServiceStatus.objects.filter(round=current_round).select_related(
                "team",
                "service",
            )
        )
        status_map = {
            (status_entry.team_id, status_entry.service_id): status_entry
            for status_entry in current_status_entries
        }
        latest_reported_at = (
            max((status.reported_at for status in current_status_entries), default=None)
        )
    current_status_counts = _empty_counts(SERVICE_STATUS_ORDER)
    for status_entry in status_map.values():
        current_status_counts[status_entry.status] += 1
    expected_status_count = len(teams) * len(services)
    checked_status_count = sum(current_status_counts.values())
    unknown_status_count = max(expected_status_count - checked_status_count, 0)

    return {
        "current_round": _serialize_round(current_round),
        "services": [_serialize_service(service) for service in services],
        "summary": {
            "expected_status_count": expected_status_count,
            "checked_status_count": checked_status_count,
            "unknown_status_count": unknown_status_count,
            "status_counts": {
                **current_status_counts,
                "unknown": unknown_status_count,
            },
            "latest_reported_at": (
                latest_reported_at.isoformat() if latest_reported_at else None
            ),
        },
        "teams": [
            {
                "team": _serialize_team(team),
                "services": [
                    {
                        "service": _serialize_service(service),
                        "status": (
                            status_map[(team.id, service.id)].status
                            if (team.id, service.id) in status_map
                            else "unknown"
                        ),
                        "status_label": (
                            status_map[(team.id, service.id)].get_status_display()
                            if (team.id, service.id) in status_map
                            else "No data"
                        ),
                        "points_awarded": (
                            status_map[(team.id, service.id)].points_awarded
                            if (team.id, service.id) in status_map
                            else 0
                        ),
                        "message": (
                            status_map[(team.id, service.id)].message
                            if (team.id, service.id) in status_map
                            else ""
                        ),
                        "reported_at": (
                            status_map[(team.id, service.id)].reported_at.isoformat()
                            if (team.id, service.id) in status_map
                            else None
                        ),
                    }
                    for service in services
                ],
            }
            for team in teams
        ],
        "history": _build_service_status_history(services, teams),
    }


def _build_checker_diagnostics(current_round: Round | None) -> dict:
    active_team_count = _get_active_approved_teams().count()
    active_service_count = Service.objects.filter(is_active=True).count()
    expected_status_count = (
        active_team_count * active_service_count if current_round is not None else 0
    )
    status_counts = _empty_counts(SERVICE_STATUS_ORDER)
    checked_status_count = 0
    latest_reported_at = None
    latest_issues = []

    if current_round is not None:
        status_counts = _serialize_status_breakdown(
            ServiceStatus.objects.filter(round=current_round)
            .values("status")
            .annotate(count=models.Count("id")),
            SERVICE_STATUS_ORDER,
        )
        checked_status_count = sum(status_counts.values())
        latest_reported_at = (
            ServiceStatus.objects.filter(round=current_round)
            .order_by("-reported_at")
            .values_list("reported_at", flat=True)
            .first()
        )
        latest_issues = list(
            ServiceStatus.objects.filter(round=current_round)
            .exclude(status=ServiceStatus.Status.UP)
            .select_related("team", "service")
            .order_by("-reported_at", "team__name", "service__name")[
                :CHECKER_ISSUE_LIMIT
            ]
        )

    unknown_status_count = max(expected_status_count - checked_status_count, 0)
    status_counts_with_unknown = {
        **status_counts,
        "unknown": unknown_status_count,
    }
    issue_count = (
        status_counts[ServiceStatus.Status.MUMBLE]
        + status_counts[ServiceStatus.Status.CORRUPT]
        + status_counts[ServiceStatus.Status.DOWN]
        + unknown_status_count
    )

    return {
        "round": _serialize_round(current_round),
        "active_team_count": active_team_count,
        "active_service_count": active_service_count,
        "expected_status_count": expected_status_count,
        "checked_status_count": checked_status_count,
        "unknown_status_count": unknown_status_count,
        "issue_count": issue_count,
        "status_counts": status_counts_with_unknown,
        "latest_reported_at": (
            latest_reported_at.isoformat() if latest_reported_at else None
        ),
        "latest_issues": [
            {
                "team": _serialize_team(status_entry.team),
                "service": _serialize_service(status_entry.service),
                "status": status_entry.status,
                "status_label": status_entry.get_status_display(),
                "points_awarded": status_entry.points_awarded,
                "message": status_entry.message,
                "reported_at": status_entry.reported_at.isoformat(),
            }
            for status_entry in latest_issues
        ],
    }


def _build_admin_state_payload() -> dict:
    settings_obj = _get_settings()
    teams = list(
        Team.objects.annotate(
            member_count=models.Count("members", distinct=True),
            submission_count=models.Count("submissions", distinct=True),
        ).order_by("name")
    )
    services = list(
        Service.objects.annotate(
            flag_count=models.Count("flags", distinct=True),
            status_count=models.Count("service_statuses", distinct=True),
        ).order_by("name")
    )
    rounds = list(
        Round.objects.annotate(
            flag_count=models.Count("flags", distinct=True),
            accepted_submission_count=models.Count(
                "flags__submissions",
                filter=models.Q(flags__submissions__status=Submission.Status.ACCEPTED),
                distinct=True,
            ),
        ).order_by("-number")
    )
    reservations = list(TeamReservation.objects.order_by("status", "-created_at")[:20])
    recent_submissions = list(
        Submission.objects.select_related(
            "submitted_by",
            "submitting_team",
            "flag__team",
            "flag__service",
            "flag__round",
        )[:SUBMISSION_HISTORY_LIMIT]
    )
    current_round = Round.objects.filter(state=Round.State.RUNNING).order_by("-number").first()
    current_status_summary = {}
    latest_checker_report_at = None
    if current_round is not None:
        current_status_summary = {
            row["status"]: row["count"]
            for row in ServiceStatus.objects.filter(round=current_round)
            .values("status")
            .annotate(count=models.Count("id"))
        }
        latest_checker_report_at = (
            ServiceStatus.objects.filter(round=current_round)
            .order_by("-reported_at")
            .values_list("reported_at", flat=True)
            .first()
        )
    latest_round_number = Round.objects.aggregate(max_number=models.Max("number"))["max_number"] or 0

    return {
        "settings": _serialize_settings(settings_obj),
        "teams": [_serialize_admin_team(team) for team in teams],
        "reservations": [_serialize_team_reservation(reservation) for reservation in reservations],
        "services": [_serialize_admin_service(service) for service in services],
        "rounds": [_serialize_admin_round(round_obj) for round_obj in rounds],
        "recent_submissions": [
            _serialize_submission(submission) for submission in recent_submissions
        ],
        "current_round": _serialize_round(_get_current_round()),
        "current_status_summary": current_status_summary,
        "current_checker_diagnostics": _build_checker_diagnostics(current_round),
        "latest_checker_report_at": (
            latest_checker_report_at.isoformat() if latest_checker_report_at else None
        ),
        "next_round_number": latest_round_number + 1,
    }


def _build_auth_payload(user) -> dict:
    membership = _get_team_membership(user)
    if membership is None:
        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_staff": user.is_staff,
            },
            "team": None,
            "membership": None,
            "members": [],
            "recent_submissions": [],
        }

    team_members = list(
        TeamMember.objects.select_related("user")
        .filter(team=membership.team)
        .order_by("role", "user__username")
    )
    recent_submissions = list(
        Submission.objects.select_related(
            "submitted_by",
            "submitting_team",
            "flag__team",
            "flag__service",
            "flag__round",
        )
        .filter(submitting_team=membership.team)[:SUBMISSION_HISTORY_LIMIT]
    )

    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
        },
        "team": _serialize_team(membership.team),
        "membership": {
            "role": membership.role,
            "role_label": membership.get_role_display(),
        },
        "members": [_serialize_member(member) for member in team_members],
        "recent_submissions": [_serialize_submission(submission) for submission in recent_submissions],
    }


def _create_user_from_payload(user_data: dict):
    username = (user_data.get("username") or "").strip()
    password = user_data.get("password") or ""
    email = (user_data.get("email") or "").strip()

    if not username:
        raise ValidationError("Each participant must have a username.")
    if not password:
        raise ValidationError(f"User '{username}' must have a password.")
    if User.objects.filter(username__iexact=username).exists():
        raise ValidationError(f"Username '{username}' is already taken.")
    if email:
        validate_email(email)

    validate_password(password)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=(user_data.get("first_name") or "").strip(),
        last_name=(user_data.get("last_name") or "").strip(),
    )
    return user


def _validate_team_payload(
    payload: dict,
    team: Team | None = None,
    *,
    allow_moderation: bool = False,
):
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValidationError("Team name is required.")

    slug = (payload.get("slug") or slugify(name)).strip()
    if not slug:
        raise ValidationError("Team slug could not be generated.")

    qs = Team.objects.all()
    if team is not None:
        qs = qs.exclude(pk=team.pk)

    if qs.filter(name__iexact=name).exists():
        raise ValidationError("A team with this name already exists.")
    if qs.filter(slug=slug).exists():
        raise ValidationError("A team with this slug already exists.")

    contact_email = (payload.get("contact_email") or "").strip()
    if contact_email:
        validate_email(contact_email)

    data = {
        "name": name,
        "slug": slug,
        "affiliation": (payload.get("affiliation") or "").strip(),
        "contact_email": contact_email,
        "is_active": bool(
            payload.get("is_active", team.is_active if team is not None else True)
        ),
    }

    if allow_moderation:
        moderation_status = payload.get(
            "moderation_status",
            team.moderation_status if team is not None else Team.ModerationStatus.APPROVED,
        )
        if moderation_status not in Team.ModerationStatus.values:
            raise ValidationError(
                "Team moderation status must be approved, pending, or suspended."
            )
        data["moderation_status"] = moderation_status
        data["moderation_note"] = (
            (payload.get("moderation_note") or "").strip()
            if "moderation_note" in payload
            else (team.moderation_note if team is not None else "")
        )

    return data


def _validate_team_profile_payload(payload: dict):
    contact_email = (payload.get("contact_email") or "").strip()
    if contact_email:
        validate_email(contact_email)

    return {
        "affiliation": (payload.get("affiliation") or "").strip(),
        "contact_email": contact_email,
    }


def _parse_optional_datetime(value, *, field_name: str):
    if value in (None, ""):
        return None

    if hasattr(value, "tzinfo"):
        return value

    parsed = parse_datetime(value)
    if parsed is None:
        raise ValidationError(f"{field_name} must be a valid ISO datetime.")
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def _validate_settings_payload(payload: dict):
    current_settings = _get_settings()
    starts_at = _parse_optional_datetime(
        payload.get("registration_starts_at", current_settings.registration_starts_at),
        field_name="registration_starts_at",
    )
    ends_at = _parse_optional_datetime(
        payload.get("registration_ends_at", current_settings.registration_ends_at),
        field_name="registration_ends_at",
    )
    if starts_at and ends_at and starts_at >= ends_at:
        raise ValidationError("registration_ends_at must be later than registration_starts_at.")

    round_duration_minutes = int(
        payload.get("round_duration_minutes", current_settings.round_duration_minutes)
    )
    round_break_minutes = int(
        payload.get("round_break_minutes", current_settings.round_break_minutes)
    )
    if round_duration_minutes <= 0:
        raise ValidationError("round_duration_minutes must be positive.")
    if round_break_minutes < 0:
        raise ValidationError("round_break_minutes cannot be negative.")

    return {
        "registration_open": bool(
            payload.get("registration_open", current_settings.registration_open)
        ),
        "registration_starts_at": starts_at,
        "registration_ends_at": ends_at,
        "reservation_required_for_registration": bool(
            payload.get(
                "reservation_required_for_registration",
                current_settings.reservation_required_for_registration,
            )
        ),
        "auto_approve_registrations": bool(
            payload.get(
                "auto_approve_registrations",
                current_settings.auto_approve_registrations,
            )
        ),
        "round_duration_minutes": round_duration_minutes,
        "round_break_minutes": round_break_minutes,
    }


def _validate_reservation_payload(payload: dict):
    team_name = (payload.get("team_name") or "").strip()
    captain_username = (payload.get("captain_username") or "").strip()
    contact_email = (payload.get("contact_email") or "").strip()
    team_slug = (payload.get("team_slug") or slugify(team_name)).strip()

    if not team_name:
        raise ValidationError("Team name is required.")
    if not captain_username:
        raise ValidationError("Captain username is required.")
    if not contact_email:
        raise ValidationError("Contact email is required.")
    validate_email(contact_email)
    if not team_slug:
        raise ValidationError("Team slug could not be generated.")

    if Team.objects.filter(name__iexact=team_name).exists():
        raise ValidationError("A team with this name already exists.")
    if TeamReservation.objects.filter(name__iexact=team_name).exclude(
        status=TeamReservation.Status.REJECTED
    ).exists():
        raise ValidationError("This team name is already reserved.")
    if Team.objects.filter(slug=team_slug).exists() or TeamReservation.objects.filter(
        slug=team_slug
    ).exclude(status=TeamReservation.Status.REJECTED).exists():
        raise ValidationError("This team slug is already reserved.")

    return {
        "name": team_name,
        "slug": team_slug,
        "captain_username": captain_username,
        "contact_email": contact_email,
    }


def _validate_round_schedule_payload(payload: dict):
    try:
        count = int(payload.get("count", 1))
    except (TypeError, ValueError):
        raise ValidationError("Round schedule count must be an integer.")

    if count <= 0 or count > 10:
        raise ValidationError("Round schedule count must be between 1 and 10.")

    start_at = _parse_optional_datetime(payload.get("start_at"), field_name="start_at")
    return {"count": count, "start_at": start_at}


def _validate_service_payload(payload: dict, service: Service | None = None):
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValidationError("Service name is required.")

    slug = (payload.get("slug") or slugify(name)).strip()
    if not slug:
        raise ValidationError("Service slug could not be generated.")

    qs = Service.objects.all()
    if service is not None:
        qs = qs.exclude(pk=service.pk)

    if qs.filter(name__iexact=name).exists():
        raise ValidationError("A service with this name already exists.")
    if qs.filter(slug=slug).exists():
        raise ValidationError("A service with this slug already exists.")

    port = payload.get("port")
    if port in ("", None):
        port = None
    elif not isinstance(port, int):
        raise ValidationError("Service port must be an integer.")
    elif port <= 0 or port > 65535:
        raise ValidationError("Service port must be between 1 and 65535.")

    return {
        "name": name,
        "slug": slug,
        "description": (payload.get("description") or "").strip(),
        "port": port,
        "is_active": bool(payload.get("is_active", True)),
    }


@require_GET
def healthcheck(request):
    return JsonResponse({"status": "ok"})


@require_GET
def summary(request):
    payload = _build_dashboard_payload()
    payload["summary"]["current_round_number"] = (
        payload["current_round"]["number"] if payload["current_round"] else None
    )
    return JsonResponse(payload["summary"])


@require_GET
def scoreboard(request):
    payload = _build_dashboard_payload()
    return JsonResponse(
        {
            "current_round": payload["current_round"],
            "summary": payload["summary"],
            "services": payload["services"],
            "service_stats": payload["service_stats"],
            "recent_rounds": payload["recent_rounds"],
            "scoreboard": payload["scoreboard"],
            "submission_history": payload["submission_history"],
        }
    )


@require_GET
def dashboard(request):
    return JsonResponse(_build_dashboard_payload())


@require_GET
def service_status(request):
    return JsonResponse(_build_service_status_payload())


@require_GET
def registration_settings(request):
    return JsonResponse(_serialize_settings(_get_settings()))


@csrf_exempt
@require_http_methods(["POST"])
def reserve_team_name(request):
    settings_obj = _get_settings()
    if not settings_obj.is_registration_available():
        return _json_error(
            "Registration is currently closed.",
            status=403,
            request=request,
        )

    try:
        payload = _parse_json_body(request)
        reservation_data = _validate_reservation_payload(payload)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    reservation = TeamReservation.objects.create(
        **reservation_data,
        token=secrets.token_hex(12),
        expires_at=timezone.now() + timedelta(days=7),
    )
    return JsonResponse(
        {
            "ok": True,
            "message": f"Reservation request created for '{reservation.name}'.",
            "reservation": _serialize_team_reservation(reservation),
            "settings": _serialize_settings(settings_obj),
        },
        status=201,
    )


@require_GET
def me(request):
    user = _get_request_user(request)
    if user is None:
        return JsonResponse({"authenticated": False})

    return JsonResponse(_build_auth_payload(user))


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    settings_obj = _get_settings()
    if not settings_obj.is_registration_available():
        return _json_error(
            "Registration is currently closed.",
            status=403,
            request=request,
        )

    try:
        payload = _parse_json_body(request)
        team_name = (payload.get("team_name") or "").strip()
        if not team_name:
            raise ValidationError("Team name is required.")

        team_slug = (payload.get("team_slug") or slugify(team_name)).strip()
        if not team_slug:
            raise ValidationError("Team slug could not be generated. Provide team_slug explicitly.")

        if Team.objects.filter(name__iexact=team_name).exists():
            raise ValidationError("A team with this name already exists.")
        if Team.objects.filter(slug=team_slug).exists():
            raise ValidationError("A team with this slug already exists.")

        captain_payload = payload.get("captain") or {}
        if not isinstance(captain_payload, dict):
            raise ValidationError("Captain payload must be an object.")

        participants = payload.get("participants") or []
        if not isinstance(participants, list):
            raise ValidationError("Participants payload must be a list.")

        if len(participants) + 1 > MAX_TEAM_MEMBERS:
            raise ValidationError(f"Team registration is limited to {MAX_TEAM_MEMBERS} members.")

        usernames = []
        for candidate in [captain_payload, *participants]:
            if not isinstance(candidate, dict):
                raise ValidationError("Each participant must be represented as an object.")
            username = (candidate.get("username") or "").strip().lower()
            if username in usernames:
                raise ValidationError("Each team member must use a unique username.")
            usernames.append(username)

        matching_reservation = None
        if settings_obj.reservation_required_for_registration:
            reservation_token = (payload.get("reservation_token") or "").strip()
            if not reservation_token:
                raise ValidationError("An approved reservation token is required for registration.")
            matching_reservation = TeamReservation.objects.filter(
                token=reservation_token,
                status=TeamReservation.Status.APPROVED,
            ).first()
            if matching_reservation is None:
                raise ValidationError("Reservation token is invalid or not approved.")
            if matching_reservation.expires_at and matching_reservation.expires_at < timezone.now():
                raise ValidationError("Reservation token has expired.")
            if matching_reservation.name.lower() != team_name.lower():
                raise ValidationError("Reservation token does not match the selected team name.")
            if matching_reservation.slug != team_slug:
                raise ValidationError("Reservation token does not match the selected team slug.")

        with transaction.atomic():
            captain_user = _create_user_from_payload(captain_payload)
            contact_email = (payload.get("contact_email") or "").strip() or captain_user.email
            if contact_email:
                validate_email(contact_email)
            team = Team.objects.create(
                name=team_name,
                slug=team_slug,
                affiliation=(payload.get("affiliation") or "").strip(),
                contact_email=contact_email,
                moderation_status=(
                    Team.ModerationStatus.APPROVED
                    if settings_obj.auto_approve_registrations
                    else Team.ModerationStatus.PENDING
                ),
            )
            TeamMember.objects.create(
                user=captain_user,
                team=team,
                role=TeamMember.Role.CAPTAIN,
            )

            for participant_payload in participants:
                member_user = _create_user_from_payload(participant_payload)
                TeamMember.objects.create(
                    user=member_user,
                    team=team,
                    role=TeamMember.Role.PLAYER,
                )

            if matching_reservation is not None:
                matching_reservation.status = TeamReservation.Status.CLAIMED
                matching_reservation.reviewed_at = timezone.now()
                matching_reservation.save(update_fields=["status", "reviewed_at"])

            token = Token.objects.create(user=captain_user)

        response_payload = _build_auth_payload(captain_user)
        response_payload["ok"] = True
        response_payload["token"] = token.key
        response_payload["message"] = (
            "Team registered and approved."
            if team.moderation_status == Team.ModerationStatus.APPROVED
            else "Team registered and is waiting for admin approval."
        )
        return JsonResponse(response_payload, status=201)

    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        payload = _parse_json_body(request)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return _json_error(
            "Username and password are required.",
            status=400,
            request=request,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return _json_error(
            "Invalid username or password.",
            status=401,
            request=request,
        )

    token, _ = Token.objects.get_or_create(user=user)
    response_payload = _build_auth_payload(user)
    response_payload["ok"] = True
    response_payload["token"] = token.key
    return JsonResponse(response_payload)


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    user = _get_request_user(request)
    if user is None:
        return _json_error(
            "Authentication token is required.",
            status=401,
            request=request,
        )

    token_key = _extract_token_key(request)
    Token.objects.filter(key=token_key, user=user).delete()
    return JsonResponse({"ok": True, "message": "Logged out successfully."})


@csrf_exempt
@require_http_methods(["POST"])
def team_update(request):
    user, membership, error_response = _require_team_captain(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
        team_profile = _validate_team_profile_payload(payload)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    team = membership.team
    for field, value in team_profile.items():
        setattr(team, field, value)
    team.save(update_fields=list(team_profile.keys()))

    response_payload = _build_auth_payload(user)
    response_payload["ok"] = True
    response_payload["message"] = "Team profile updated."
    return JsonResponse(response_payload)


@csrf_exempt
@require_http_methods(["POST"])
def team_add_member(request):
    user, membership, error_response = _require_team_captain(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    member_count = TeamMember.objects.filter(team=membership.team).count()
    if member_count >= MAX_TEAM_MEMBERS:
        return _json_error(
            f"Team size is limited to {MAX_TEAM_MEMBERS} members.",
            status=409,
            request=request,
        )

    try:
        with transaction.atomic():
            new_user = _create_user_from_payload(payload)
            new_membership = TeamMember.objects.create(
                user=new_user,
                team=membership.team,
                role=TeamMember.Role.PLAYER,
            )
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    response_payload = _build_auth_payload(user)
    response_payload["ok"] = True
    response_payload["message"] = f"Member '{new_membership.user.username}' added to the team."
    response_payload["member"] = _serialize_member(new_membership)
    return JsonResponse(response_payload, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def team_update_member_role(request, user_id: int):
    user, membership, error_response = _require_team_captain(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
        role = _validate_member_role((payload.get("role") or "").strip())
        target_membership = _get_team_member_or_404(membership.team, user_id)
    except ValidationError as error:
        message = "; ".join(error.messages)
        status = 404 if "not found" in message.lower() else 400
        return _json_error(message, status=status, request=request)

    if target_membership.role == TeamMember.Role.CAPTAIN and role != TeamMember.Role.CAPTAIN:
        captain_count = TeamMember.objects.filter(
            team=membership.team,
            role=TeamMember.Role.CAPTAIN,
        ).count()
        if captain_count <= 1:
            return _json_error(
                "Team must always have at least one captain.",
                status=409,
                request=request,
            )

    if target_membership.role == role:
        response_payload = _build_auth_payload(user)
        response_payload["ok"] = True
        response_payload["message"] = (
            f"Member '{target_membership.user.username}' is already a {target_membership.get_role_display().lower()}."
        )
        return JsonResponse(response_payload)

    target_membership.role = role
    target_membership.save(update_fields=["role"])

    response_payload = _build_auth_payload(user)
    response_payload["ok"] = True
    response_payload["message"] = (
        f"Member '{target_membership.user.username}' role updated to "
        f"{target_membership.get_role_display().lower()}."
    )
    response_payload["member"] = _serialize_member(target_membership)
    return JsonResponse(response_payload)


@csrf_exempt
@require_http_methods(["POST"])
def team_remove_member(request, user_id: int):
    user, membership, error_response = _require_team_captain(request)
    if error_response is not None:
        return error_response

    if user.id == user_id:
        return _json_error(
            "You cannot remove your own account through the team management API.",
            status=409,
            request=request,
        )

    try:
        target_membership = _get_team_member_or_404(membership.team, user_id)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=404, request=request)

    if target_membership.role == TeamMember.Role.CAPTAIN:
        captain_count = TeamMember.objects.filter(
            team=membership.team,
            role=TeamMember.Role.CAPTAIN,
        ).count()
        if captain_count <= 1:
            return _json_error(
                "Team must always have at least one captain.",
                status=409,
                request=request,
            )

    username = target_membership.user.username
    with transaction.atomic():
        target_membership.user.delete()

    response_payload = _build_auth_payload(user)
    response_payload["ok"] = True
    response_payload["message"] = f"Member '{username}' removed from the team."
    return JsonResponse(response_payload)


@csrf_exempt
@require_http_methods(["POST"])
def submit_flag(request):
    user, membership, error_response = _require_team_membership(request)
    if error_response is not None:
        return error_response

    if not membership.team.is_active or not membership.team.is_approved:
        return _json_error(
            "Only approved active teams can submit flags.",
            status=403,
            request=request,
        )

    try:
        payload = _parse_json_body(request)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    submitted_value = (payload.get("flag") or "").strip()
    if not submitted_value:
        return _json_error("Flag value is required.", status=400, request=request)
    if len(submitted_value) > 128:
        return _json_error("Flag value is too long.", status=400, request=request)

    current_round = _get_current_round()
    if current_round is None or current_round.state != Round.State.RUNNING:
        return _json_error(
            "There is no active round for flag submission.",
            status=409,
            request=request,
        )

    now = timezone.now()
    recent_cutoff = now - timedelta(seconds=SUBMISSION_RATE_WINDOW_SECONDS)
    recent_submission_count = Submission.objects.filter(
        submitting_team=membership.team,
        submitted_at__gte=recent_cutoff,
    ).count()
    if recent_submission_count >= SUBMISSION_RATE_LIMIT:
        return _json_error(
            "Too many submissions in a short time. Please wait a moment before retrying.",
            status=429,
            request=request,
        )

    submission_data = {
        "submitting_team": membership.team,
        "submitted_by": user,
        "submitted_value": submitted_value,
        "processed_at": now,
    }

    with transaction.atomic():
        flag = (
            Flag.objects.select_for_update()
            .select_related("team", "service", "round")
            .filter(value=submitted_value)
            .first()
        )

        if flag is None:
            submission = Submission.objects.create(
                status=Submission.Status.REJECTED,
                points_awarded=0,
                message="Unknown flag.",
                **submission_data,
            )
            return JsonResponse(
                {
                    "ok": False,
                    "message": _localize_api_message(submission.message, request),
                    "submission": _serialize_submission(submission),
                },
                status=400,
            )

        if flag.team_id == membership.team_id:
            submission = Submission.objects.create(
                flag=flag,
                status=Submission.Status.REJECTED,
                points_awarded=0,
                message="You cannot submit your own team's flag.",
                **submission_data,
            )
            return JsonResponse(
                {
                    "ok": False,
                    "message": _localize_api_message(submission.message, request),
                    "submission": _serialize_submission(submission),
                },
                status=400,
            )

        if flag.round_id != current_round.id:
            submission = Submission.objects.create(
                flag=flag,
                status=Submission.Status.REJECTED,
                points_awarded=0,
                message="This flag is not valid for the current round.",
                **submission_data,
            )
            return JsonResponse(
                {
                    "ok": False,
                    "message": _localize_api_message(submission.message, request),
                    "submission": _serialize_submission(submission),
                },
                status=400,
            )

        if flag.round.started_at > now:
            submission = Submission.objects.create(
                flag=flag,
                status=Submission.Status.REJECTED,
                points_awarded=0,
                message="This flag belongs to a round that has not started yet.",
                **submission_data,
            )
            return JsonResponse(
                {
                    "ok": False,
                    "message": _localize_api_message(submission.message, request),
                    "submission": _serialize_submission(submission),
                },
                status=400,
            )

        if flag.expires_at and now > flag.expires_at:
            submission = Submission.objects.create(
                flag=flag,
                status=Submission.Status.REJECTED,
                points_awarded=0,
                message="This flag has expired.",
                **submission_data,
            )
            return JsonResponse(
                {
                    "ok": False,
                    "message": _localize_api_message(submission.message, request),
                    "submission": _serialize_submission(submission),
                },
                status=400,
            )

        if Submission.objects.filter(flag=flag, status=Submission.Status.ACCEPTED).exists():
            submission = Submission.objects.create(
                flag=flag,
                status=Submission.Status.REJECTED,
                points_awarded=0,
                message="This flag has already been submitted successfully.",
                **submission_data,
            )
            return JsonResponse(
                {
                    "ok": False,
                    "message": _localize_api_message(submission.message, request),
                    "submission": _serialize_submission(submission),
                },
                status=400,
            )

        submission = Submission.objects.create(
            flag=flag,
            status=Submission.Status.ACCEPTED,
            points_awarded=ATTACK_POINTS_PER_FLAG,
            message=f"Flag accepted for {flag.service.name}.",
            **submission_data,
        )

    return JsonResponse(
        {
            "ok": True,
            "message": submission.message,
            "submission": _serialize_submission(submission),
            "scoreboard": _build_scoreboard(
                list(Service.objects.filter(is_active=True)),
                _get_current_round(),
            ),
        },
        status=201,
    )


@require_GET
def admin_state(request):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    return JsonResponse(_build_admin_state_payload())


@csrf_exempt
@require_http_methods(["POST"])
def admin_update_settings(request):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
        update_data = _validate_settings_payload(payload)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    settings_obj = _get_settings()
    for field, value in update_data.items():
        setattr(settings_obj, field, value)
    settings_obj.save(update_fields=list(update_data.keys()) + ["updated_at"])

    return JsonResponse(
        {
            "ok": True,
            "message": "Competition settings updated.",
            "settings": _serialize_settings(settings_obj),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_approve_reservation(request, reservation_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    reservation = TeamReservation.objects.filter(pk=reservation_id).first()
    if reservation is None:
        return _json_error("Reservation not found.", status=404, request=request)
    if reservation.status == TeamReservation.Status.CLAIMED:
        return _json_error(
            "Claimed reservations cannot be modified.",
            status=409,
            request=request,
        )

    reservation.status = TeamReservation.Status.APPROVED
    reservation.reviewed_at = timezone.now()
    reservation.save(update_fields=["status", "reviewed_at"])
    return JsonResponse(
        {
            "ok": True,
            "message": f"Reservation '{reservation.name}' approved.",
            "reservation": _serialize_team_reservation(reservation),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_reject_reservation(request, reservation_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    reservation = TeamReservation.objects.filter(pk=reservation_id).first()
    if reservation is None:
        return _json_error("Reservation not found.", status=404, request=request)
    if reservation.status == TeamReservation.Status.CLAIMED:
        return _json_error(
            "Claimed reservations cannot be modified.",
            status=409,
            request=request,
        )

    try:
        payload = _parse_json_body(request)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    reservation.status = TeamReservation.Status.REJECTED
    reservation.note = (payload.get("note") or "").strip()
    reservation.reviewed_at = timezone.now()
    reservation.save(update_fields=["status", "note", "reviewed_at"])
    return JsonResponse(
        {
            "ok": True,
            "message": f"Reservation '{reservation.name}' rejected.",
            "reservation": _serialize_team_reservation(reservation),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_create_team(request):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
        team = Team.objects.create(**_validate_team_payload(payload, allow_moderation=True))
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    return JsonResponse(
        {
            "ok": True,
            "message": f"Team '{team.name}' created.",
            "team": _serialize_admin_team(team),
            "admin_state": _build_admin_state_payload(),
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_update_team(request, team_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    team = Team.objects.filter(pk=team_id).first()
    if team is None:
        return _json_error("Team not found.", status=404, request=request)

    try:
        payload = _parse_json_body(request)
        update_data = _validate_team_payload(payload, team=team, allow_moderation=True)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    for field, value in update_data.items():
        setattr(team, field, value)
    team.save(update_fields=list(update_data.keys()))

    return JsonResponse(
        {
            "ok": True,
            "message": f"Team '{team.name}' updated.",
            "team": _serialize_admin_team(team),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_delete_team(request, team_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    team = Team.objects.filter(pk=team_id).first()
    if team is None:
        return _json_error("Team not found.", status=404, request=request)

    team_name = team.name
    team.delete()

    return JsonResponse(
        {
            "ok": True,
            "message": f"Team '{team_name}' deleted.",
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_create_service(request):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
        service = Service.objects.create(**_validate_service_payload(payload))
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    return JsonResponse(
        {
            "ok": True,
            "message": f"Service '{service.name}' created.",
            "service": _serialize_admin_service(service),
            "admin_state": _build_admin_state_payload(),
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_update_service(request, service_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    service = Service.objects.filter(pk=service_id).first()
    if service is None:
        return _json_error("Service not found.", status=404, request=request)

    try:
        payload = _parse_json_body(request)
        update_data = _validate_service_payload(payload, service=service)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    for field, value in update_data.items():
        setattr(service, field, value)
    service.save(update_fields=list(update_data.keys()))

    return JsonResponse(
        {
            "ok": True,
            "message": f"Service '{service.name}' updated.",
            "service": _serialize_admin_service(service),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_delete_service(request, service_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    service = Service.objects.filter(pk=service_id).first()
    if service is None:
        return _json_error("Service not found.", status=404, request=request)

    service_name = service.name
    service.delete()

    return JsonResponse(
        {
            "ok": True,
            "message": f"Service '{service_name}' deleted.",
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_create_round(request):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
        next_round_number = (
            Round.objects.aggregate(max_number=models.Max("number"))["max_number"] or 0
        ) + 1
        number = payload.get("number", next_round_number)
        if not isinstance(number, int):
            raise ValidationError("Round number must be an integer.")
        if Round.objects.filter(number=number).exists():
            raise ValidationError("A round with this number already exists.")

        round_obj = Round.objects.create(
            number=number,
            state=Round.State.PLANNED,
            started_at=timezone.now(),
        )
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    return JsonResponse(
        {
            "ok": True,
            "message": f"Round {round_obj.number} created.",
            "round": _serialize_admin_round(round_obj),
            "admin_state": _build_admin_state_payload(),
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_schedule_rounds(request):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    try:
        payload = _parse_json_body(request)
        schedule_data = _validate_round_schedule_payload(payload)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=400, request=request)

    settings_obj = _get_settings()
    duration = timedelta(minutes=settings_obj.round_duration_minutes)
    break_duration = timedelta(minutes=settings_obj.round_break_minutes)
    latest_round = Round.objects.order_by("-number").first()
    latest_number = latest_round.number if latest_round else 0

    if schedule_data["start_at"] is not None:
        next_start = schedule_data["start_at"]
    elif latest_round and latest_round.finished_at:
        next_start = latest_round.finished_at + break_duration
    elif latest_round:
        next_start = latest_round.started_at + duration + break_duration
    else:
        next_start = timezone.now()

    created_rounds = []
    for offset in range(schedule_data["count"]):
        round_obj = Round.objects.create(
            number=latest_number + offset + 1,
            state=Round.State.PLANNED,
            started_at=next_start + offset * (duration + break_duration),
        )
        created_rounds.append(_serialize_admin_round(round_obj))

    return JsonResponse(
        {
            "ok": True,
            "message": f"Scheduled {len(created_rounds)} round(s).",
            "rounds": created_rounds,
            "admin_state": _build_admin_state_payload(),
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_start_round(request, round_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    round_obj = Round.objects.filter(pk=round_id).first()
    if round_obj is None:
        return _json_error("Round not found.", status=404, request=request)

    if round_obj.state == Round.State.FINISHED:
        return _json_error(
            "Finished rounds cannot be restarted.",
            status=409,
            request=request,
        )
    if round_obj.state == Round.State.RUNNING:
        return _json_error(
            f"Round {round_obj.number} is already running.",
            status=409,
            request=request,
        )

    running_round = Round.objects.filter(state=Round.State.RUNNING).exclude(pk=round_obj.pk).first()
    if running_round is not None:
        return _json_error(
            f"Round {running_round.number} is already running. Finish it before starting another round.",
            status=409,
            request=request,
        )

    round_obj.state = Round.State.RUNNING
    round_obj.started_at = timezone.now()
    round_obj.finished_at = None
    round_obj.save(update_fields=["state", "started_at", "finished_at"])
    created_flags = ensure_flags_for_round(round_obj)

    return JsonResponse(
        {
            "ok": True,
            "message": f"Round {round_obj.number} started.",
            "created_flags": created_flags,
            "round": _serialize_admin_round(round_obj),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_finish_round(request, round_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    round_obj = Round.objects.filter(pk=round_id).first()
    if round_obj is None:
        return _json_error("Round not found.", status=404, request=request)

    if round_obj.state != Round.State.RUNNING:
        return _json_error(
            "Only a running round can be finished.",
            status=409,
            request=request,
        )

    finished_at = timezone.now()
    round_obj.state = Round.State.FINISHED
    round_obj.finished_at = finished_at
    round_obj.save(update_fields=["state", "finished_at"])
    Flag.objects.filter(round=round_obj, expires_at__isnull=True).update(expires_at=finished_at)

    return JsonResponse(
        {
            "ok": True,
            "message": f"Round {round_obj.number} finished.",
            "round": _serialize_admin_round(round_obj),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_generate_flags(request, round_id: int):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    round_obj = Round.objects.filter(pk=round_id).first()
    if round_obj is None:
        return _json_error("Round not found.", status=404, request=request)

    created_flags = ensure_flags_for_round(round_obj)
    return JsonResponse(
        {
            "ok": True,
            "message": f"Flag generation completed for round {round_obj.number}.",
            "created_flags": created_flags,
            "round": _serialize_admin_round(round_obj),
            "admin_state": _build_admin_state_payload(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def admin_checker_tick(request):
    _, error_response = _require_staff_user(request)
    if error_response is not None:
        return error_response

    current_round = Round.objects.filter(state=Round.State.RUNNING).order_by("-number").first()
    if current_round is None:
        return _json_error(
            "There is no running round for the checker tick.",
            status=409,
            request=request,
        )

    try:
        tick_result = run_checker_tick(current_round)
    except ValidationError as error:
        return _json_error("; ".join(error.messages), status=409, request=request)

    return JsonResponse(
        {
            "ok": True,
            "message": f"Checker tick completed for round {current_round.number}.",
            "checker_tick": _serialize_checker_tick_result(tick_result),
            "admin_state": _build_admin_state_payload(),
        }
    )
