# Приложение А. Основные API-эндпоинты платформы

Ниже приведен укрупненный перечень endpoint-ов платформы. Все пути указаны относительно `/api/`.

## Public

- `GET /health/` — проверка доступности backend.
- `GET /summary/` — агрегированные счетчики dashboard.
- `GET /scoreboard/` — таблица результатов.
- `GET /dashboard/` — объединенный payload главной страницы.
- `GET /service-status/` — матрица сервисов и история checker-проверок.
- `GET /registration/settings/` — настройки окна регистрации.
- `POST /team-reservations/` — заявка на резервирование названия команды.

## Auth

- `POST /auth/register/` — регистрация команды и участников.
- `POST /auth/login/` — вход и получение token.
- `POST /auth/logout/` — отзыв текущего token.
- `GET /auth/me/` — контекст текущего пользователя.

## Team

- `POST /team/update/` — обновление данных команды капитаном.
- `POST /team/members/` — добавление участника.
- `POST /team/members/<user_id>/role/` — изменение роли участника.
- `POST /team/members/<user_id>/remove/` — удаление участника.
- `POST /submit-flag/` — отправка найденного флага.

## Admin

- `GET /admin/state/` — общий срез административных данных.
- `POST /admin/settings/update/` — изменение настроек соревнования.
- `POST /admin/reservations/<id>/approve/` — одобрение заявки на резервирование.
- `POST /admin/reservations/<id>/reject/` — отклонение заявки.
- `POST /admin/teams/` — создание команды.
- `POST /admin/teams/<id>/update/` — изменение команды.
- `POST /admin/teams/<id>/delete/` — удаление команды.
- `POST /admin/services/` — создание сервиса.
- `POST /admin/services/<id>/update/` — изменение сервиса.
- `POST /admin/services/<id>/delete/` — удаление сервиса.
- `POST /admin/rounds/` — создание раунда.
- `POST /admin/rounds/schedule/` — пакетное планирование раундов.
- `POST /admin/rounds/<id>/start/` — запуск раунда.
- `POST /admin/rounds/<id>/finish/` — завершение раунда.
- `POST /admin/rounds/<id>/generate-flags/` — генерация флагов.
- `POST /admin/checker/tick/` — запуск checker-проверки.

