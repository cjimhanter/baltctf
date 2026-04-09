# Обзор API

Ниже перечислены основные текущие эндпоинты. Все пути указаны относительно `/api/`.

## Public

- `GET /health/` — healthcheck backend
- `GET /summary/` — агрегированные счётчики для dashboard
- `GET /scoreboard/` — таблица результатов
- `GET /dashboard/` — единый payload для главной страницы
- `GET /service-status/` — матрица состояний сервисов
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

Frontend дополнительно отправляет `Accept-Language`, чтобы UI и будущая серверная локализация могли работать согласованно.
