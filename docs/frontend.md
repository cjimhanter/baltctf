# Frontend-приложение

## Технологии

- `Vue 3`
- `Vite`
- `vue-router`
- `SCSS` с декомпозицией по `7-1 architecture`

## Структура

- `src/App.vue` — shell приложения, верхняя навигация, language switch и `router-view`
- `src/router/` — описание маршрутов
- `src/pages/` — route-level страницы
- `src/components/` — feature-компоненты
- `src/composables/useCompetitionPage.js` — shared state и действия с API
- `src/i18n.js` — словарь интерфейса и переключение языка
- `src/styles/` — SCSS-архитектура и BEM-классы

## Маршруты

- `/` — dashboard со scoreboard, summary metrics и recent activity
- `/services` — выделенная матрица статусов сервисов
- `/team` — регистрация, логин, состав команды и отправка флагов
- `/admin` — admin console для staff users

## Переключение языка

В приложении есть встроенный language switch `English / Русский`.

### Как это работает

- активный язык хранится в `localStorage`
- все основные UI-строки берутся из `src/i18n.js`
- форматирование даты также зависит от выбранного языка
- frontend отправляет выбранный язык в `Accept-Language`

## Что уже локализовано

- верхняя навигация
- route-level заголовки
- dashboard, scoreboard и timeline
- team portal
- admin console
- клиентские success/fallback messages

## Ограничение текущей версии

Часть backend validation messages по-прежнему приходит с сервера на английском. Для полного двуязычного опыта потребуется отдельная локализация Django-ответов.
