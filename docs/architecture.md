# Architecture Draft

## Main subsystems

### Web platform
- team registration
- scoreboard
- flag submission
- service status page
- Django admin panel

### Frontend implementation structure
- `App.vue` собирает приложение как shell с верхней навигацией и `router-view`
- `router/index.js` управляет маршрутами `/`, `/services`, `/team`, `/admin`
- `components/access` отвечает за гостевой auth/registration flow
- `components/workspace` отвечает за team session, captain tools и flag submission
- `components/admin` отвечает за operator console
- `components/dashboard` отвечает за hero, scoreboard, service matrix, activity feed и timeline
- `components/services` отвечает за выделенную матрицу статусов сервисов
- `pages/` содержит route-level страницы для dashboard, team profile, service status и admin tools
- `composables/useCompetitionPage.js` хранит shared state и операции с backend API
- `i18n.js` хранит словарь интерфейса и глобальное переключение языка `EN/RU`
- шаблоны Vue приведены к BEM-именованию, а SCSS разложен по 7-1 архитектуре

### Checking system
- flag generation
- flag placement
- service health checks
- result submission to backend

### Current checker implementation status
- отдельный контейнер `checker` логинится в backend под staff-учёткой
- по таймеру вызывает `POST /api/admin/checker/tick/`
- backend генерирует недостающие флаги и для каждого `service.slug` вызывает отдельный checker module
- checker для `atlas-board` делает `POST` и затем `GET` HTML-страницы с флагом
- checker для `signal-api` делает `POST` и затем `GET` JSON-секрета с токеном команды
- checker для `cold-storage` делает `POST` и затем `GET` текстового файла
- по результатам реальных HTTP `put/get` операций backend записывает `ServiceStatus`

### Vulnbox
- vulnerable web service
- vulnerable API service
- vulnerable storage service

### Current vulnbox demo services
- `atlas-board` - demo board service, в котором checker хранит флаг в post body, а leak endpoint позволяет читать чужие записи
- `signal-api` - demo JSON API, в котором checker кладёт секрет в record, а debug export раскрывает данные без авторизации
- `cold-storage` - demo file storage, в котором checker загружает текстовый файл, а raw endpoint позволяет читать файлы по произвольному пути

## Proposed data model

- `Team`
- `CompetitionSettings`
- `TeamReservation`
- `TeamMember` / `User`
- `Service`
- `Round`
- `Flag`
- `Submission`
- `ServiceStatus`

### Current backend implementation

- `Team`: командная сущность с `slug`, названием, контактным email, moderation status и note
- `CompetitionSettings`: singleton-настройки окна регистрации, approval flow и таймингов раундов
- `TeamReservation`: резервирование имени команды с токеном и статусами `pending/approved/rejected/claimed`
- `TeamMember`: участник команды на базе встроенного Django `User` с ролями `captain/player`
- `Service`: сервис с `slug`, описанием и портом vulnbox
- `Round`: игровой раунд со статусом `planned/running/finished`
- `Flag`: флаг для комбинации `team + service + round`
- `Submission`: отправка флага атакующей командой и конкретным пользователем с результатом проверки
- `ServiceStatus`: результат проверки доступности сервиса в конкретном раунде

## Current API slice

- `GET /api/summary/` - агрегированные счётчики
- `GET /api/scoreboard/` - таблица команд и очков
- `GET /api/dashboard/` - единый payload для frontend dashboard
- `GET /api/service-status/` - матрица статусов сервисов
- `GET /api/registration/settings/` - публичные настройки окна регистрации
- `POST /api/team-reservations/` - заявка на резервирование названия команды
- `POST /api/auth/register/` - регистрация команды и участников
- `POST /api/auth/login/` / `POST /api/auth/logout/` - токен-аутентификация участников
- `GET /api/auth/me/` - профиль текущего пользователя и состав его команды
- `POST /api/team/update/` - captain-only обновление affiliation/contact email команды
- `POST /api/team/members/` - captain-only добавление нового участника в свою команду
- `POST /api/team/members/<user_id>/role/` - captain-only смена роли участника
- `POST /api/team/members/<user_id>/remove/` - captain-only удаление участника из своей команды
- `POST /api/submit-flag/` - отправка флага с проверкой дублей, чужой команды и срока жизни
- `GET /api/admin/state/` - staff-only snapshot для operator console
- `POST /api/admin/settings/update/` - управление registration windows и параметрами соревнования
- `POST /api/admin/reservations/<id>/approve|reject/` - обработка reservation requests
- `POST /api/admin/teams/...` - базовое управление командами
- `POST /api/admin/services/...` - базовое управление сервисами
- `POST /api/admin/rounds/...` - создание, батч-планирование, запуск, остановка раунда и генерация флагов
- `POST /api/admin/checker/tick/` - ручной запуск checker tick из operator console или внешнего checker service

## Integration flow

1. Backend stores teams, services, rounds, flags, and submissions.
2. Checker service periodically authenticates in the backend and requests a checker tick for the current running round.
3. Backend ensures flags exist for each approved active team/service pair and runs service-specific `put/get` checks against the demo vulnbox services.
4. Teams submit captured flags through the web platform.
5. Backend calculates the scoreboard from checker results and valid submissions.
