# ПРИЛОЖЕНИЕ Б. Заготовки схем и рисунков

В этом приложении собраны черновые схемы, которые можно использовать при финальной верстке ВКР. В Markdown они оформлены как Mermaid-диаграммы. При переносе в `.docx` их можно экспортировать в изображения и подписать в соответствии с требованиями методических указаний.

## Рисунок 2.1 — Общая архитектура платформы `baltctf`

```mermaid
flowchart LR
    Player[Игрок / капитан команды]
    Admin[Организатор]
    Frontend[Frontend\nVue 3 + Vite]
    Backend[Backend API\nDjango + DRF]
    DB[(PostgreSQL)]
    Checker[Checker container\nperiodic tick]
    Atlas[atlas-board\nvulnbox-web]
    Signal[signal-api\nvulnbox-api]
    Storage[cold-storage\nvulnbox-storage]

    Player --> Frontend
    Admin --> Frontend
    Frontend --> Backend
    Backend --> DB
    Checker --> Backend
    Backend --> Atlas
    Backend --> Signal
    Backend --> Storage
```

К схеме следует добавить подпись: "Рисунок 2.1 — Общая архитектура платформы `baltctf`". На рисунке важно показать, что frontend не работает с базой данных напрямую, checker вызывает только backend API, а backend является центральной доверенной частью системы.

## Рисунок 2.2 — ER-диаграмма основных сущностей

```mermaid
erDiagram
    Team ||--o{ TeamMember : includes
    Team ||--o{ Flag : owns
    Team ||--o{ Submission : submits
    Team ||--o{ ServiceStatus : receives
    User ||--|| TeamMember : has
    User ||--o{ Submission : creates
    Service ||--o{ Flag : contains
    Service ||--o{ ServiceStatus : checked_as
    Round ||--o{ Flag : generates
    Round ||--o{ ServiceStatus : records
    Flag ||--o{ Submission : accepted_for

    Team {
        int id PK
        string name UK
        string slug UK
        string affiliation
        string contact_email
        bool is_active
        string moderation_status
        datetime created_at
    }

    TeamMember {
        int id PK
        int user_id UK
        int team_id FK
        string role
        datetime created_at
    }

    TeamReservation {
        int id PK
        string name
        string slug
        string contact_email
        string captain_username
        string token
        string status
        datetime expires_at
    }

    CompetitionSettings {
        int id PK
        bool registration_open
        bool reservation_required_for_registration
        bool auto_approve_registrations
        int round_duration_minutes
        int round_break_minutes
    }

    Service {
        int id PK
        string name UK
        string slug UK
        int port
        bool is_active
    }

    Round {
        int id PK
        int number UK
        string state
        datetime started_at
        datetime finished_at
    }

    Flag {
        int id PK
        string value UK
        int team_id FK
        int service_id FK
        int round_id FK
        datetime expires_at
    }

    Submission {
        int id PK
        int submitting_team_id FK
        int submitted_by_id FK
        int flag_id FK
        string submitted_value
        string status
        int points_awarded
        datetime submitted_at
    }

    ServiceStatus {
        int id PK
        int team_id FK
        int service_id FK
        int round_id FK
        string status
        int points_awarded
        datetime reported_at
    }
```

`TeamReservation` и `CompetitionSettings` показаны как отдельные сущности, потому что они участвуют в регистрационном и административном сценариях, но не образуют внешних ключей с игровыми таблицами. На финальной схеме рядом с диаграммой следует указать ограничения уникальности: `Team.name`, `Team.slug`, `Service.name`, `Service.slug`, `Round.number`, `Flag.value`, `TeamReservation.name`, `TeamReservation.slug`, `TeamReservation.token`, а также составные ограничения `Flag(team, service, round)` и `ServiceStatus(team, service, round)`.

## Рисунок 3.1 — Поток выполнения checker tick

```mermaid
sequenceDiagram
    participant C as Checker container
    participant B as Backend API
    participant DB as PostgreSQL
    participant V as Demo vulnbox service

    C->>B: POST /api/auth/login/
    B->>DB: Проверка staff-пользователя
    B-->>C: Token
    loop Каждые CHECKER_INTERVAL_SECONDS
        C->>B: POST /api/admin/checker/tick/
        B->>DB: Поиск running round
        B->>DB: Создание недостающих Flag
        B->>V: put(flag)
        B->>V: get(flag)
        V-->>B: Результат проверки
        B->>DB: update_or_create ServiceStatus
        B-->>C: checker_tick summary
    end
```

Для главы 3 эту схему можно использовать рядом с описанием checker system. Она показывает, что внешний checker-контейнер инициирует цикл, но доменная логика генерации флагов, выбора сервисных checker modules и записи `ServiceStatus` находится на стороне backend-а.
