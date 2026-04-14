# Обзор API

Ниже перечислены основные текущие эндпоинты. Все пути указаны относительно `/api/`.

## Public

- `GET /health/` — healthcheck backend
- `GET /summary/` — агрегированные счётчики для dashboard, включая attack/defense totals и checker counts
- `GET /scoreboard/` — таблица результатов с per-team submission/check counts, service stats и recent submissions
- `GET /dashboard/` — единый payload для главной страницы: scoreboard, service analytics, checker history и submission history
- `GET /service-status/` — матрица состояний сервисов текущего раунда и recent checker history по раундам
- `GET /registration/settings/` — текущее окно регистрации и related settings
- `POST /team-reservations/` — создать заявку на резервирование имени команды

## Auth

- `POST /auth/register/` — регистрация команды и участников
- `POST /auth/login/` — логин и выдача token
- `POST /auth/logout/` — отзыв текущего token
- `GET /auth/me/` — контекст текущего пользователя, команды и состава

## Team captain actions

- `POST /team/update/` — обновить affiliation и contact email команды
- `POST /team/members/` — добавить участника в текущую команду
- `POST /team/members/<user_id>/role/` — сменить роль участника
- `POST /team/members/<user_id>/remove/` — удалить участника
- `POST /submit-flag/` — отправить найденный флаг

## Staff admin actions

- `GET /admin/state/` — срез админских данных
- `POST /admin/settings/update/` — изменить registration settings и параметры тайминга
- `POST /admin/reservations/<id>/approve/` — одобрить резервирование
- `POST /admin/reservations/<id>/reject/` — отклонить резервирование
- `POST /admin/teams/` — создать команду
- `POST /admin/teams/<id>/update/` — изменить команду
- `POST /admin/teams/<id>/delete/` — удалить команду
- `POST /admin/services/` — создать сервис
- `POST /admin/services/<id>/update/` — изменить сервис
- `POST /admin/services/<id>/delete/` — удалить сервис
- `POST /admin/rounds/` — создать запланированный раунд
- `POST /admin/rounds/schedule/` — создать batch из нескольких раундов
- `POST /admin/rounds/<id>/start/` — запустить раунд
- `POST /admin/rounds/<id>/finish/` — завершить раунд
- `POST /admin/rounds/<id>/generate-flags/` — сгенерировать флаги для раунда
- `POST /admin/checker/tick/` — запустить checker tick для текущего running round

## Аутентификация

Используется token auth через header:

```http
Authorization: Token <token>
```

Frontend дополнительно отправляет `Accept-Language`. Backend использует `Accept-Language: ru` для частых validation/error messages auth, registration, team management, flag submission и admin workflow; английский остаётся языком по умолчанию.

## Payload notes

- `dashboard.summary` и `/summary/` теперь включают `attack_points_total`, `defense_points_total`, `submission_count`, `rejected_submissions_count`, `checker_status_count`, `acceptance_rate`, `checker_status_breakdown`, `current_round_status_breakdown`, `latest_submission_at` и `latest_checker_report_at`.
- `dashboard.service_stats` агрегирует по каждому сервису generated flags, accepted submissions, attack points, defense points, checker status counts и uptime percentage.
- `dashboard.recent_rounds` содержит round-level attack/defense/checker counters для последних раундов.
- `dashboard.service_status_history` и `service-status.history` показывают checker timeline по раундам: для каждого сервиса есть counts `up/mumble/corrupt/down/unknown`, checked count, issue count, defense points и latest report timestamp.
- `dashboard.submission_history`, `scoreboard.submission_history`, `admin/state.recent_submissions` и `auth/me.recent_submissions` используют общий submission serializer с submitting team, submitted user, target team, service, round, status, points и timestamps.
- `admin/state.current_checker_diagnostics` показывает диагностический срез активного running round для operator console: active team/service counts, expected/checked/unknown status counts, issue count, status counts с `unknown`, latest report timestamp и последние проблемные checker results с team, service, status, message и points.
