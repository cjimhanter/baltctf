# Текущее состояние проекта

## Что уже реализовано

### Backend

- модели команд, участников, сервисов, раундов, флагов, сабмитов и статусов сервисов
- singleton-настройки соревнования `CompetitionSettings`
- резервирование имени команды через `TeamReservation`
- токен-аутентификация пользователей
- регистрация команды с капитаном и несколькими участниками
- captain-only управление составом команды
- отправка флагов с проверкой срока жизни, дубликатов и запретом на сдачу собственного флага
- локализация частых API validation/error messages по `Accept-Language: ru`
- staff-only API для:
  - модерации команд
  - настройки registration windows
  - approval / reject резервирований
  - создания и пакетного планирования раундов
  - запуска checker tick
- расширенные payload’ы dashboard/scoreboard/service-status:
  - attack/defense totals
  - per-team submission/check counts
  - service analytics
  - recent checker history по раундам
  - recent submission history для dashboard, admin и team workspace

### Checker

- backend больше не использует детерминированную mock-оценку
- для каждого `service.slug` есть отдельный checker module
- checker делает реальные HTTP `put/get` операции против demo vulnbox-сервисов
- результаты checker tick сохраняются в `ServiceStatus`

### Vulnbox demo services

- `atlas-board` — demo web board, куда checker кладёт флаг в публикацию
- `signal-api` — demo JSON API, где флаг хранится в record
- `cold-storage` — demo файловое хранилище, где флаг хранится в текстовом файле

Эти сервисы умышленно уязвимы и подходят для демонстрации Attack/Defense сценария.

### Frontend

- приложение собрано на `Vue 3 + Vite`
- используется `vue-router`
- есть маршруты:
  - `/` — dashboard
  - `/scoreboard` — полная таблица результатов
  - `/services` — матрица статусов сервисов
  - `/team` — регистрация, логин и профиль команды
  - `/admin` — staff-only инструменты
- dashboard и scoreboard показывают расширенные attack/defense/service/round stats
- `/services` дополнительно показывает checker timeline по раундам
- team workspace и admin console показывают recent submission history
- admin console показывает checker diagnostics для активного раунда: ожидаемые, полученные и unknown проверки, количество проблем и последние сообщения checker/vulnbox
- стили организованы по `SCSS 7-1 architecture`
- интерфейс поддерживает переключение языка `English / Русский`

## Что остаётся упрощённым

- checker выполняется синхронно внутри backend request-а
- vulnbox-сервисы общие для локальной среды, а не изолированы по отдельной машине на команду
- часть редких backend/Django validation messages пока остаётся англоязычной
- полноценные e2e-тесты с Docker-контейнерами ещё не добавлены
