# Документация BaltCTF

Этот каталог теперь разделён на две части:

- проектные черновики для ВКР и планирования
- техническая документация по текущей реализации

## Техническая документация

- [current-state.md](/home/baka/Projects/baltctf/docs/current-state.md) — что уже реализовано в backend, frontend, checker и vulnbox
- [runbook.md](/home/baka/Projects/baltctf/docs/runbook.md) — локальный запуск, миграции, демо-данные и маршруты UI
- [api.md](/home/baka/Projects/baltctf/docs/api.md) — обзор текущих API-эндпоинтов
- [frontend.md](/home/baka/Projects/baltctf/docs/frontend.md) — структура Vue-приложения, маршруты и переключение языка
- [architecture.md](/home/baka/Projects/baltctf/docs/architecture.md) — архитектурный обзор текущего состояния системы

## Проектные материалы

- [requirements.md](/home/baka/Projects/baltctf/docs/requirements.md) — краткая фиксация функциональных требований
- [plan.md](/home/baka/Projects/baltctf/docs/plan.md) — поэтапный план разработки
- [diploma-structure.md](/home/baka/Projects/baltctf/docs/diploma-structure.md) — структура ВКР

## Что важно сейчас

Текущий репозиторий уже содержит рабочий вертикальный срез Attack/Defense платформы:

- регистрация команд и участников
- reservation / approval flow для имени команды
- scoreboard и матрица статусов сервисов
- отправка флагов через web UI
- админские сценарии для настройки регистрации, модерации и раундов
- service-specific checker scripts против demo vulnbox-сервисов
