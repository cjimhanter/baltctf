# Frontend-приложение

## Технологии

- `Vue 3`
- `Vite`
- `vue-router`
- `SCSS` с декомпозицией по `7-1 architecture`
- локальный vendor-слой нормализации в `src/styles/vendors/_normalize.scss`
- `Vitest + @vue/test-utils + jsdom` для frontend-тестов

## Структура

- `src/App.vue` — shell приложения с BEM-блоком `app-layout`, верхней навигацией, language switch и `router-view`
- `src/router/` — описание маршрутов
- `src/pages/` — route-level страницы
- `src/components/` — feature-компоненты
- `src/composables/useCompetitionPage.js` — orchestration entrypoint для общего page context
- `src/composables/competitionPage*.js` — разнесённые модули factories/state/derived/loaders/mutations/auth-team/admin логики
- `src/i18n.js` — словарь интерфейса и переключение языка
- `src/styles/` — SCSS-архитектура, локальный vendor normalize и BEM-классы
- `src/test/setup.js` — общий setup для `Vitest`
- `src/App.spec.js`, `src/pages/pages.spec.js`, `src/composables/useCompetitionPage.spec.js` — базовое покрытие app/pages/composables

## Маршруты

- `/` — dashboard со scoreboard, expanded summary metrics, checker history и recent submission history
- `/scoreboard` — отдельная полная таблица результатов с service posture, per-team counts и service analytics
- `/services` — выделенная матрица статусов сервисов и checker timeline по раундам
- `/team` — регистрация, логин, состав команды, отправка флагов и submission history команды
- `/admin` — admin console для staff users, включая recent submissions и checker diagnostics по активному running round

## Переключение языка

В приложении есть встроенный language switch `English / Русский`.

### Как это работает

- активный язык хранится в `localStorage`
- все основные UI-строки берутся из `src/i18n.js`
- форматирование даты также зависит от выбранного языка
- frontend отправляет выбранный язык в `Accept-Language`

## Frontend tests

- установка зависимостей: `npm install` в каталоге `frontend/`
- запуск тестов: `npm run test:run`
- `vite.config.js` уже содержит конфигурацию `Vitest` с окружением `jsdom` и `setupFiles: "./src/test/setup.js"`
- при изменении frontend-зависимостей обновляйте `frontend/package.json` и `frontend/package-lock.json` вместе

## Что уже локализовано

- верхняя навигация
- route-level заголовки
- dashboard, scoreboard, checker timeline, service analytics и submission history
- team portal
- admin console
- клиентские success/fallback messages
- частые backend API validation/error messages при `Accept-Language: ru`

## Ограничение текущей версии

Часть редких backend/Django validation messages по-прежнему может приходить с сервера на английском. Для полного двуязычного опыта потребуется расширять серверный словарь и унифицировать все Django-ответы.
