# Checker Service

The `checker` container is the periodic scheduler for the local BaltCTF
Attack/Defense flow.

It does not talk to the demo vulnbox services directly. Instead, it
authenticates into the Django backend as a staff user and calls the backend
checker tick endpoint:

```http
POST /api/admin/checker/tick/
```

The backend then generates missing flags, runs the service-specific checker
modules for the current running round, and stores results in `ServiceStatus`.

## Runtime Configuration

- `CHECKER_API_BASE_URL` - backend API base URL, default `http://backend:8000/api`
- `CHECKER_ADMIN_USERNAME` - staff username, default `admin`
- `CHECKER_ADMIN_PASSWORD` - staff password, default `BaltCTFadmin123!`
- `CHECKER_INTERVAL_SECONDS` - delay between cycles, default `60`
- `CHECKER_REQUEST_TIMEOUT_SECONDS` - timeout for login/tick requests, default `10`

## Behavior

1. Create a `requests.Session`.
2. Login through `POST /api/auth/login/`.
3. Store the returned DRF token in memory.
4. Call `POST /api/admin/checker/tick/` every interval.
5. If backend returns `409` because no round is running, log an idle message and retry later.
6. If backend returns `401` or `403`, clear the token and re-authenticate on the next cycle.

## Local Run

From the repository root:

```bash
docker compose up --build checker
```

For a meaningful tick, the backend must be running, migrations must be applied,
demo data should be seeded, and at least one round must be in `running` state.

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_demo_data --reset
docker compose up --build
```

Demo staff credentials are created by `seed_demo_data --reset`:

```text
admin / BaltCTFadmin123!
```

These credentials are for local demonstration only.
