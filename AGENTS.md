# AGENTS.md

Last reviewed: 2026-04-13

This file is the handoff note for future Codex/chat sessions working on this repo. Read it first, then skim the linked docs/code before making changes. Keep it current whenever a request changes project knowledge, setup, commands, architecture, or working conventions.

## Project Essence

`baltctf` is a graduation project for an Attack/Defense CTF platform.

Core idea: teams register, play rounds, attack vulnerable demo services, submit captured flags, and watch scoreboard/service status. Operators manage teams, services, registration windows, rounds, and checker ticks.

## Stack

- Backend: Django 5.1, Django REST Framework, PostgreSQL, token auth.
- Frontend: Vue 3, Vite, Vue Router, SCSS 7-1 architecture, Vitest.
- Local orchestration: Docker Compose.
- Checker: Python service that logs into backend as staff and periodically calls backend checker tick.
- Vulnbox demos: three intentionally vulnerable Python services.

## Repository Map

- `backend/` - Django project and API.
- `backend/ctf/models.py` - domain models: teams, members, settings, reservations, services, rounds, flags, submissions, service statuses.
- `backend/ctf/views.py` - API endpoint implementations.
- `backend/ctf/urls.py` - API routes under `/api/`.
- `backend/ctf/checkers/` - service-specific checker modules.
- `backend/ctf/management/commands/seed_demo_data.py` - demo data and demo accounts.
- `frontend/` - Vue application.
- `frontend/src/App.vue` - app shell with navigation/language switch/router view.
- `frontend/src/router/index.js` - routes: `/`, `/scoreboard`, `/services`, `/team`, `/admin`.
- `frontend/src/pages/` - route-level pages.
- `frontend/src/components/` - feature UI blocks by domain, including dashboard service timeline and submission history panels.
- `frontend/src/composables/useCompetitionPage.js` - orchestration entrypoint for shared page context.
- `frontend/src/composables/competitionPage*.js` - state, factories, derived data, loaders, mutations, auth/team/admin actions.
- `frontend/src/i18n.js` - English/Russian UI dictionary and language state.
- `frontend/src/styles/` - SCSS 7-1 structure with BEM-style classes and local normalize.
- `checker/` - periodic checker client container.
- `vulnbox/` - demo vulnerable services: `atlas-board`, `signal-api`, `cold-storage`.
- `docs/` - project notes and technical docs. Start with `docs/current-state.md`, `docs/architecture.md`, `docs/frontend.md`, `docs/api.md`, and `docs/runbook.md`.

## Local Runbook

Optional environment override:

```bash
cp .env.example .env
```

Start stack:

```bash
docker compose up --build
```

Migrate and seed demo data:

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_demo_data --reset
```

Useful URLs:

- Frontend dashboard: `http://localhost:5173/`
- Full scoreboard: `http://localhost:5173/scoreboard`
- Service matrix: `http://localhost:5173/services`
- Team portal: `http://localhost:5173/team`
- Admin tools: `http://localhost:5173/admin`
- Backend API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`

Demo accounts after seeding:

- Admin: `admin` / `BaltCTFadmin123!`
- Player examples: `northern_lights_captain`, `amber_byte_player1`
- Demo player password: `BaltCTFdemo123!`

## Test And Verification Commands

Frontend:

```bash
cd frontend
npm run test:run
npm run build
```

Backend:

```bash
docker compose run --rm backend python manage.py test
docker compose run --rm backend python manage.py migrate
```

Full local smoke check:

```bash
docker compose up --build
```

If frontend dependencies change, update both `frontend/package.json` and `frontend/package-lock.json`. If Python dependencies change, update the relevant `requirements.txt` and rebuild affected Docker images.

## Current Functional Slice

Implemented:

- Team registration with captain and optional participants.
- Team name reservation and moderation workflow.
- Token login/logout/current-user context.
- Captain-only team profile and member management.
- Flag submission with duplicate, expiry, and own-flag checks.
- Staff API for competition settings, teams, services, reservations, round planning/start/finish, flag generation, and checker tick.
- Dashboard, scoreboard, and service-status payloads with expanded attack/defense/service/round stats.
- Checker history/service timeline data from existing `ServiceStatus` rows.
- Submission history for dashboard, admin state, and team workspace from existing `Submission` rows.
- Vue routes for dashboard, full scoreboard, service matrix, team portal, and admin console.
- English/Russian language switch; frontend sends `Accept-Language`.
- Vitest coverage for app/pages/composables.
- Checker tick performs real HTTP `put/get` operations against demo vulnbox services and records `ServiceStatus`.

Still simplified:

- Checker work runs synchronously inside backend request handling.
- Demo vulnbox services are shared in local Docker, not isolated per team VM/container.
- Some backend validation messages remain English-only.
- No full Docker-based end-to-end checker/vulnbox test suite yet.

## API Overview

Main public/auth/team endpoints:

- `GET /api/health/`
- `GET /api/summary/`
- `GET /api/scoreboard/` - ranked teams plus summary, service stats, recent rounds, and submission history.
- `GET /api/dashboard/` - combined dashboard payload with expanded stats, service analytics, checker history, and submission history.
- `GET /api/service-status/` - current service matrix plus checker history by round.
- `GET /api/registration/settings/`
- `POST /api/team-reservations/`
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`
- `POST /api/team/update/`
- `POST /api/team/members/`
- `POST /api/team/members/<user_id>/role/`
- `POST /api/team/members/<user_id>/remove/`
- `POST /api/submit-flag/`

Staff endpoints live under `/api/admin/...`; see `backend/ctf/urls.py` and `docs/api.md`.

## Frontend Conventions

- Use Vue single-file components and Composition API style already present in the repo.
- Keep route-level composition in `src/pages/`; reusable domain UI in `src/components/`.
- Shared competition state/actions should go through `useCompetitionPage.js` and the split `competitionPage*.js` modules.
- Preserve the `i18n.js` dictionary pattern for user-facing copy. Add both English and Russian strings when adding UI text.
- Keep BEM-like class names consistent with the existing SCSS.
- Styles follow SCSS 7-1:
  - `abstracts/`
  - `base/`
  - `components/`
  - `layout/`
  - `pages/`
  - `themes/`
  - `vendors/`
- `frontend/src/styles/main.scss` imports the style layers.
- Do not introduce a new UI framework unless explicitly requested.

## Backend Conventions

- API is function-based DRF in `backend/ctf/views.py`.
- Authentication uses DRF token auth with `Authorization: Token <token>`.
- Staff-only operations should remain protected by staff checks.
- Domain changes usually need models, migrations, admin registration if relevant, serializers/response helpers in views, docs updates, and frontend API usage.
- Seed/demo behavior lives in `seed_demo_data.py`; keep demo credentials aligned with README/docs if changed.

## Checker And Vulnbox Notes

- The standalone `checker` container logs into backend using:
  - `CHECKER_API_BASE_URL`
  - `CHECKER_ADMIN_USERNAME`
  - `CHECKER_ADMIN_PASSWORD`
  - `CHECKER_INTERVAL_SECONDS`
- It calls `POST /api/admin/checker/tick/`.
- Backend checker modules are selected by `service.slug`.
- Current demo slugs/services:
  - `atlas-board` - HTML board service.
  - `signal-api` - JSON API service.
  - `cold-storage` - text/file storage service.

## Working Rules For Future Agents

- Start each task by checking `git status --short`; this repo may have user edits in progress.
- Do not revert or overwrite unrelated user changes.
- Prefer `rg`/`rg --files` for searching.
- Before changing behavior, inspect the nearby tests and docs.
- Update docs when changing setup, endpoints, data model, commands, routes, or user-visible workflows.
- Keep this `AGENTS.md` updated with durable facts, not noisy minute-by-minute logs.
- Never add real secrets here. Demo local credentials are okay because they are already part of the repo docs.

## Recent Notes

- 2026-04-13: Added expanded dashboard/scoreboard stats, service checker timeline history, and submission history by extending existing dashboard/scoreboard/service-status/auth/admin payloads without adding migrations or new routes.
- 2026-04-13: Added a Vue `/scoreboard` route and first control-room UI pass inspired by the reference Attack-and-Defense-CTF-Platform frontend, without changing backend APIs.
- 2026-04-13: Created this file after reviewing README, docs, Docker Compose, backend models/routes, frontend router/API setup, package scripts, and current project structure.
