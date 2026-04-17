# Требования к системе

Актуально на **17 апреля 2026**.

## Функциональные требования

- регистрация команд и участников
- аутентификация пользователей по логину и паролю
- резервирование имени команды и approval flow
- отображение scoreboard
- отображение статусов сервисов
- отправка флагов через web-интерфейс
- управление составом команды капитаном
- админские сценарии для команд, сервисов, раундов и окна регистрации
- диагностика checker-а для текущего running round в панели администратора
- checker system для генерации, размещения и проверки флагов
- demo vulnbox-сервисы для Attack/Defense сценария

## Нефункциональные требования

- понятный web-интерфейс для игроков и администраторов
- адаптивный frontend
- базовая защита от некорректных сабмитов и дубликатов флагов
- масштабируемость на небольшой учебный контур
- отказоустойчивость на уровне локального Docker-стека
- поддержка двух языков интерфейса: `English / Русский`

## Что уже реализовано

- backend на `Django + PostgreSQL`
- frontend на `Vue 3 + Vite`
- token auth, reservation flow, регистрация команд и управление составом
- dashboard, full scoreboard, service status matrix, team portal и admin tools
- расширенные payload'ы dashboard/scoreboard/service-status с attack/defense stats, checker history и submission history
- локализация основных frontend-строк и частых backend validation/error messages при `Accept-Language: ru`
- service-specific checker scripts с реальными HTTP `put/get` проверками
- три demo vulnbox-сервиса: `atlas-board`, `signal-api`, `cold-storage`
- базовые backend-тесты и Vitest-тесты для app/pages/composables

## Что ещё желательно довести

- асинхронный запуск checker вне backend request-а
- e2e и интеграционные тесты полного стека
- более полная локализация редких Django/backend validation messages
- изоляция vulnbox-сервисов по командам вместо общего local demo-контура
