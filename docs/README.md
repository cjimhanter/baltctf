# Документация BaltCTF

Этот каталог теперь разделён на две части:

- проектные черновики для ВКР и планирования
- техническая документация по текущей реализации

## Техническая документация

- [current-state.md](current-state.md) — что уже реализовано в backend, frontend, checker и vulnbox
- [runbook.md](runbook.md) — локальный запуск, миграции, демо-данные, доступ к PostgreSQL и маршруты UI
- [api.md](api.md) — обзор текущих API-эндпоинтов
- [frontend.md](frontend.md) — структура Vue-приложения, маршруты и переключение языка
- [architecture.md](architecture.md) — архитектурный обзор текущего состояния системы

## Проектные материалы

- [requirements.md](requirements.md) — краткая фиксация функциональных требований
- [plan.md](plan.md) — поэтапный план до сдачи
- [diploma-structure.md](diploma-structure.md) — структура ВКР
- [diploma/](diploma/) — Markdown-черновик ВКР по подглавам

## Что важно сейчас

Текущий репозиторий уже содержит рабочий вертикальный срез Attack/Defense платформы:

- регистрация команд и участников
- reservation / approval flow для имени команды
- scoreboard и матрица статусов сервисов
- отправка флагов через web UI
- админские сценарии для настройки регистрации, модерации и раундов
- service-specific checker scripts против demo vulnbox-сервисов
- checker diagnostics в admin console
- базовые backend и frontend тесты
