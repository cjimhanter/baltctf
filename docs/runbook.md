# Руководство по запуску и эксплуатации

## Локальный запуск

Перейти в каталог проекта:

```bash
cd ~/Projects/baltctf
```

Если нужны кастомные переменные среды:

```bash
cp .env.example .env
```

Поднять и пересобрать стек:

```bash
docker compose up --build
```

## Миграции и демо-данные

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_demo_data --reset
```

## Адреса

- frontend dashboard: `http://localhost:5173/`
- service matrix: `http://localhost:5173/services`
- team portal: `http://localhost:5173/team`
- admin tools: `http://localhost:5173/admin`
- backend API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`

## Демо-аккаунты

### Игроки

- примеры логинов:
  - `northern_lights_captain`
  - `amber_byte_player1`
- пароль для всех demo users:
  - `BaltCTFdemo123!`

### Администратор

- логин:
  - `admin`
- пароль:
  - `BaltCTFadmin123!`

## Как проверить checker flow

1. Войти под `admin`
2. Перейти на `/admin`
3. Создать или запустить раунд
4. Нажать `Run checker tick` или подождать автоцикл контейнера `checker`
5. Перейти на `/services` и посмотреть матрицу состояний

## Если менялись зависимости

### Python

Если менялся `backend/requirements.txt` или `checker/requirements.txt`:

```bash
docker compose build backend checker
```

### Frontend

Если менялся `frontend/package.json`:

```bash
docker compose build frontend
```

## Частые проблемы

### Не применяются новые Python-пакеты

Пересобрать образы:

```bash
docker compose build backend checker
```

### Vite ругается на Sass

Пересобрать frontend:

```bash
docker compose build frontend
docker compose up frontend
```

### После изменений UI не обновился

Обычно помогает полный restart:

```bash
docker compose down
docker compose up --build
```
