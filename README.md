# Attack/Defense CTF Platform

Graduation project for an Attack/Defense CTF platform.

## Stack

- Django + Django REST Framework
- PostgreSQL
- Vue 3 + Vite + SCSS
- Docker Compose for local development
- Proxmox as a target deployment/infrastructure direction

## Components

- `backend/` - Django API and admin panel
- `frontend/` - Vue scoreboard/operator UI
- `checker/` - periodic scheduler that authenticates into the backend and triggers checker ticks
- `vulnbox/` - demo vulnerable services used by the checker and by manual A/D experiments
- `docs/` - diploma notes plus technical docs for the current implementation

## Current Baseline

This repository now contains the first working platform slice. It provides:

- a containerized local development layout
- Django domain models for teams, participants, services, rounds, flags, service checks, submissions, competition settings, and team name reservations
- API endpoints for registration windows, team name reservations, authentication, moderation, round scheduling, dashboard data, service status, and flag submission
- a Vue frontend with dedicated routes for dashboard, service status, team profile, and admin tools
- frontend styles decomposed with the SCSS 7-1 architecture
- a checker service that authenticates into the backend and triggers checker ticks for running rounds
- three intentionally vulnerable demo services used by real service-specific checker modules:
  - `atlas-board`
  - `signal-api`
  - `cold-storage`

The current checker tick now performs real `put` and `get` actions against the demo vulnbox services instead of using a deterministic mock state.

## Frontend Structure

The Vue frontend now follows a feature-oriented structure:

- `src/components/` - UI blocks split by domain (`access`, `workspace`, `admin`, `dashboard`, `common`)
- `src/components/services/` - dedicated service status matrix blocks
- `src/pages/` - route-level pages for dashboard, services, team, and admin
- `src/router/` - `vue-router` configuration
- `src/composables/useCompetitionPage.js` - shared page-level state, derived data, and API actions
- `src/i18n.js` - app-wide English/Russian language switch
- `src/styles/` - SCSS 7-1 architecture with BEM-oriented blocks wired to the Vue components

## Quick Start

1. Optional: copy `.env.example` to `.env` if you want to override the default local settings.
2. Start PostgreSQL first:
   `docker compose up -d db`
3. Apply database migrations:
   `docker compose run --rm backend python manage.py migrate`
4. Load demo data for the dashboard:
   `docker compose run --rm backend python manage.py seed_demo_data --reset`
5. Start the full stack:
   `docker compose up --build`
6. Backend will be available at `http://localhost:8000`.
7. Frontend will be available at `http://localhost:5173`.
8. Demo credentials after seeding:
   username examples: `northern_lights_captain`, `amber_byte_player1`
   password for all seeded users: `BaltCTFdemo123!`
9. Demo admin after seeding:
   username: `admin`
   password: `BaltCTFadmin123!`
10. Checker behavior in local Docker:
   the `checker` container signs in as the admin user and tries to run a checker tick every 60 seconds; if there is no running round yet, it stays idle and logs the reason.
11. Frontend note:
   the dev container now runs `npm install` on startup so SCSS dependencies stay in sync after frontend package changes.
12. Backend/checker note:
   the Python dev containers now sync `requirements.txt` on startup too, so `docker compose run --rm backend ...` and `docker compose up` keep working after dependency updates.
13. Frontend routes:
   - dashboard: `http://localhost:5173/`
   - service matrix: `http://localhost:5173/services`
   - team portal: `http://localhost:5173/team`
   - admin tools: `http://localhost:5173/admin`

## Checker And Vulnbox Environment

- `CHECKER_API_BASE_URL` - backend API base URL for the checker container, default `http://backend:8000/api`
- `CHECKER_ADMIN_USERNAME` - backend staff account used by the checker, default `admin`
- `CHECKER_ADMIN_PASSWORD` - password for the checker account, default `BaltCTFadmin123!`
- `CHECKER_INTERVAL_SECONDS` - pause between checker cycles, default `60`
- `CHECKER_REQUEST_TIMEOUT_SECONDS` - HTTP timeout for login/tick requests, default `10`
- `ATLAS_BOARD_BASE_URL` - backend-side checker URL for the web vulnbox, default `http://vulnbox-web:8080`
- `SIGNAL_API_BASE_URL` - backend-side checker URL for the API vulnbox, default `http://vulnbox-api:8080`
- `COLD_STORAGE_BASE_URL` - backend-side checker URL for the storage vulnbox, default `http://vulnbox-storage:8080`
- `CHECKER_SERVICE_REQUEST_TIMEOUT_SECONDS` - timeout for service-specific `put/get` operations, default `5`

## API Endpoints

- `GET /api/health/` - health check
- `GET /api/summary/` - aggregate counters for the control panel
- `GET /api/scoreboard/` - ranked teams with points
- `GET /api/dashboard/` - combined dashboard payload for the frontend
- `GET /api/service-status/` - current round service matrix
- `GET /api/registration/settings/` - public registration window settings
- `POST /api/team-reservations/` - request a team name reservation
- `POST /api/auth/register/` - team registration with captain and optional participants
- `POST /api/auth/login/` - obtain API token for a participant
- `POST /api/auth/logout/` - revoke the current API token
- `GET /api/auth/me/` - current authenticated participant and team context
- `POST /api/team/update/` - captain-only update of team affiliation and contact email
- `POST /api/team/members/` - captain-only creation of a new player account in the current team
- `POST /api/team/members/<user_id>/role/` - captain-only role reassignment between `captain` and `player`
- `POST /api/team/members/<user_id>/remove/` - captain-only removal of another team member
- `POST /api/submit-flag/` - submit a captured flag
- `GET /api/admin/state/` - staff-only operator snapshot for teams, services, and rounds
- `POST /api/admin/settings/update/` - update registration windows, approval rules, and round timing
- `POST /api/admin/reservations/<id>/approve/` - approve a team name reservation
- `POST /api/admin/reservations/<id>/reject/` - reject a team name reservation with an optional note
- `POST /api/admin/teams/` - create a team from the operator console
- `POST /api/admin/teams/<id>/update/` - update or enable/disable a team
- `POST /api/admin/teams/<id>/delete/` - delete a team
- `POST /api/admin/services/` - create a service
- `POST /api/admin/services/<id>/update/` - update or enable/disable a service
- `POST /api/admin/services/<id>/delete/` - delete a service
- `POST /api/admin/rounds/` - create a planned round
- `POST /api/admin/rounds/schedule/` - create a batch of planned rounds based on timing settings
- `POST /api/admin/rounds/<id>/start/` - start a round and generate missing flags
- `POST /api/admin/rounds/<id>/finish/` - finish a running round
- `POST /api/admin/rounds/<id>/generate-flags/` - generate missing flags for a round
- `POST /api/admin/checker/tick/` - run a staff-only checker tick for the current running round

## Suggested Next Steps

1. Move the service-specific checker logic from synchronous backend requests into a dedicated worker pipeline with retries and round deadlines.
2. Replace in-memory demo vulnboxes with per-team isolated containers or VM-backed services.
3. Add end-to-end tests that spin up the vulnbox containers and verify checker `put/get` behavior against real HTTP responses.
4. Split the shared frontend state into domain composables or a small store layer as the operator workflows continue to grow.
