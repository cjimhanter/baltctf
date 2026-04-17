# Приложение А. Основные API-эндпоинты платформы

В приложении приведен перечень основных HTTP API платформы `baltctf`. Все пути указаны относительно префикса `/api/`. Ответы возвращаются в формате JSON. Для защищенных запросов используется заголовок:

```http
Authorization: Token <token>
```

В таблицах указаны основные поля запросов и ответов. Полный состав JSON-ответа зависит от сценария, но сохраняет общую структуру: при изменяющих операциях обычно возвращаются `ok`, `message` и актуальный срез данных, необходимый frontend-приложению.

## Public API

Публичные маршруты доступны без авторизации. Они используются главной страницей, таблицей результатов, страницей статусов сервисов и формами регистрации.

| Метод | Путь | Доступ | Назначение | Основные поля |
| --- | --- | --- | --- | --- |
| `GET` | `/health/` | Public | Проверка доступности backend. | Ответ: `status`. |
| `GET` | `/summary/` | Public | Краткая сводка соревнования для dashboard. | Ответ: количество команд, сервисов, раундов, пользователей, атакующие и защитные баллы, счетчики отправок и checker-статусов. |
| `GET` | `/scoreboard/` | Public | Полная таблица результатов. | Ответ: `current_round`, `summary`, `services`, `service_stats`, `recent_rounds`, `scoreboard`, `submission_history`. |
| `GET` | `/dashboard/` | Public | Единый JSON-ответ главной страницы. | Ответ: `summary`, `current_round`, `services`, `service_stats`, `scoreboard`, `recent_rounds`, `recent_activity`, `submission_history`, `service_status_history`. |
| `GET` | `/service-status/` | Public | Матрица состояния сервисов и история проверок. | Ответ: `current_round`, `services`, `summary`, `teams`, `history`. |
| `GET` | `/registration/settings/` | Public | Текущие настройки регистрации. | Ответ: `registration_open`, временные границы, режим reservation, auto approve, длительность раунда и перерыва. |
| `POST` | `/team-reservations/` | Public, если регистрация доступна | Создание заявки на резервирование названия команды. | Запрос: `team_name`, `team_slug`, `captain_username`, `contact_email`. Ответ: `reservation`, `settings`, `message`. |

## Auth API

Маршруты аутентификации обслуживают регистрацию команды, вход, выход и восстановление пользовательского контекста после перезагрузки SPA.

| Метод | Путь | Доступ | Назначение | Основные поля |
| --- | --- | --- | --- | --- |
| `POST` | `/auth/register/` | Public, если регистрация доступна | Регистрация команды, капитана и участников. | Запрос: `team_name`, `team_slug`, `affiliation`, `contact_email`, `captain`, `participants`, `reservation_token`. Ответ: `token`, `user`, `team`, `membership`, `members`, `message`. |
| `POST` | `/auth/login/` | Public | Вход пользователя и выдача токена. | Запрос: `username`, `password`. Ответ: `token`, `user`, `team`, `membership`, `members`, `recent_submissions`. |
| `POST` | `/auth/logout/` | Authenticated | Отзыв текущего токена. | Запрос без тела. Ответ: `ok`, `message`. |
| `GET` | `/auth/me/` | Optional token | Получение текущей сессии. | Без токена возвращает `authenticated: false`; с токеном возвращает пользователя, команду, роль, состав и последние отправки. |

## Team API

Командные маршруты требуют токен пользователя команды. Операции управления составом доступны только капитану, а отправка флага доступна участнику активной одобренной команды при наличии запущенного раунда.

| Метод | Путь | Доступ | Назначение | Основные поля |
| --- | --- | --- | --- | --- |
| `POST` | `/team/update/` | Captain | Обновление профиля команды. | Запрос: `affiliation`, `contact_email`. Ответ: обновленный auth context. |
| `POST` | `/team/members/` | Captain | Добавление участника в команду. | Запрос: `username`, `password`, `email`, `first_name`, `last_name`. Ответ: `member`, обновленный auth context. |
| `POST` | `/team/members/<user_id>/role/` | Captain | Изменение роли участника. | Запрос: `role` со значением `captain` или `player`. Ответ: `member`, обновленный auth context. |
| `POST` | `/team/members/<user_id>/remove/` | Captain | Удаление участника из команды. | Запрос без тела. Ответ: обновленный auth context. |
| `POST` | `/submit-flag/` | Authenticated team member | Отправка найденного флага. | Запрос: `flag`. Ответ: `submission`; при успешной отправке дополнительно возвращается обновленный `scoreboard`. |

Для `/submit-flag/` backend выполняет основные проверки честности соревнования: наличие активного раунда, членство в активной одобренной команде, ограничение частоты отправок, существование флага, запрет сдачи собственного флага, принадлежность флага текущему раунду, срок действия и отсутствие ранее принятой отправки этого же флага.

Текущие числовые правила реализации:

- максимальный размер команды — 6 участников;
- accepted flag дает 25 attack points;
- лимит отправки флагов — 10 попыток от команды за 60 секунд;
- defense points: `up` — 10, `mumble` — 5, `corrupt` — 2, `down` — 0.

## Admin API

Административные маршруты требуют токен staff-пользователя. Они используются панелью организатора и управляют состоянием соревнования.

| Метод | Путь | Доступ | Назначение | Основные поля |
| --- | --- | --- | --- | --- |
| `GET` | `/admin/state/` | Staff | Единый срез данных для панели администратора. | Ответ: `settings`, `teams`, `reservations`, `services`, `rounds`, `recent_submissions`, `current_round`, `current_status_summary`, `current_checker_diagnostics`, `latest_checker_report_at`, `next_round_number`. |
| `POST` | `/admin/settings/update/` | Staff | Изменение настроек соревнования. | Запрос: `registration_open`, `registration_starts_at`, `registration_ends_at`, `reservation_required_for_registration`, `auto_approve_registrations`, `round_duration_minutes`, `round_break_minutes`. |
| `POST` | `/admin/reservations/<id>/approve/` | Staff | Одобрение заявки на резервирование. | Запрос без тела. Ответ: `reservation`, `admin_state`. |
| `POST` | `/admin/reservations/<id>/reject/` | Staff | Отклонение заявки на резервирование. | Запрос: `note`. Ответ: `reservation`, `admin_state`. |
| `POST` | `/admin/teams/` | Staff | Создание команды вручную. | Запрос: `name`, `slug`, `affiliation`, `contact_email`, `is_active`, `moderation_status`, `moderation_note`. |
| `POST` | `/admin/teams/<id>/update/` | Staff | Изменение команды. | Запрос: те же поля, что при создании команды. Ответ: `team`, `admin_state`. |
| `POST` | `/admin/teams/<id>/delete/` | Staff | Удаление команды. | Запрос без тела. Ответ: `admin_state`. |
| `POST` | `/admin/services/` | Staff | Создание сервиса соревнования. | Запрос: `name`, `slug`, `description`, `port`, `is_active`. |
| `POST` | `/admin/services/<id>/update/` | Staff | Изменение сервиса. | Запрос: те же поля, что при создании сервиса. Ответ: `service`, `admin_state`. |
| `POST` | `/admin/services/<id>/delete/` | Staff | Удаление сервиса. | Запрос без тела. Ответ: `admin_state`. |
| `POST` | `/admin/rounds/` | Staff | Создание одного запланированного раунда. | Запрос: необязательное `number`. Ответ: `round`, `admin_state`. |
| `POST` | `/admin/rounds/schedule/` | Staff | Пакетное планирование раундов. | Запрос: `count`, необязательное `start_at`. Ответ: `rounds`, `admin_state`. |
| `POST` | `/admin/rounds/<id>/start/` | Staff | Запуск раунда. | Запрос без тела. Ответ: `round`, `created_flags`, `admin_state`. |
| `POST` | `/admin/rounds/<id>/finish/` | Staff | Завершение раунда. | Запрос без тела. Ответ: `round`, `admin_state`. |
| `POST` | `/admin/rounds/<id>/generate-flags/` | Staff | Генерация недостающих флагов для раунда. | Запрос без тела. Ответ: `created_flags`, `round`, `admin_state`. |

## Checker API

Внешний контейнер `checker` не обращается к уязвимым сервисам напрямую. Он авторизуется в backend как staff-пользователь и запускает административный маршрут проверки текущего раунда.

| Метод | Путь | Доступ | Назначение | Основные поля |
| --- | --- | --- | --- | --- |
| `POST` | `/auth/login/` | Checker staff account | Получение токена для checker-контейнера. | Запрос: `username`, `password`. Ответ: `token`. |
| `POST` | `/admin/checker/tick/` | Staff / checker token | Запуск проверки сервисов текущего `running` round. | Запрос без тела. Ответ: `checker_tick`, `admin_state`, `message`. |

Ответ `checker_tick` содержит `round`, `created_flags`, `statuses_processed`, `status_breakdown` и `reported_at`. Если запущенного раунда нет, backend возвращает конфликтное состояние, а checker-контейнер остается в режиме ожидания до следующего цикла.

Поле `current_checker_diagnostics` в `/admin/state/` показывает диагностический срез активного раунда: количество активных команд и сервисов, ожидаемых проверок, полученных проверок, unknown-статусов, проблемных статусов, status breakdown и последние non-UP checker messages.
