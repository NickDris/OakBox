# Docker Conventions & Style Guide

## File Organization

```
docker/
  backend.Dockerfile        # Python backend image
  frontend.Dockerfile       # React frontend image (multi-stage with nginx)
  docker-compose.yml        # Full-stack local dev environment
  docker-compose.prod.yml   # Production overrides
  .dockerignore             # Shared ignore rules (copied to build context)
```

- One Dockerfile per service, named `<service>.Dockerfile`.
- Compose files live in `docker/`. Run with `docker compose -f docker/docker-compose.yml`.
- The Makefile at project root wraps all compose commands (see Makefile guide).

---

## Image Standards

### Base Images

| Service   | Base image                          |
|-----------|-------------------------------------|
| Backend   | `python:3.12-slim`                  |
| Frontend  | Build: `node:20-alpine`; Run: `nginx:alpine` |
| Database  | `postgres:16-alpine`                |

- Always pin the **minor** version (`python:3.12-slim`, not `python:3-slim`).
- Always use `-slim` or `-alpine` variants — never full images.
- Never use `latest` tag.

### Build Stages

Use multi-stage builds. Every Dockerfile must have at minimum:

1. **`deps`** — install dependencies only (maximizes layer cache).
2. **`build`** — compile/bundle application code.
3. **`runtime`** — copy only artifacts needed to run.

---

## Backend Dockerfile

```dockerfile
# --- deps ---
FROM python:3.12-slim AS deps

RUN pip install --no-cache-dir uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# --- runtime ---
FROM python:3.12-slim AS runtime

RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --no-create-home app

WORKDIR /app
COPY --from=deps /app/.venv /app/.venv
COPY src/backend ./backend

ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Rules

- Install dependencies in a separate stage using `uv sync --frozen --no-dev`.
- Run as non-root user (`app:1000`).
- Never install dev dependencies in the runtime image.
- Set `ENV PATH` to the venv bin — do not activate in shell.

---

## Frontend Dockerfile

```dockerfile
# --- deps ---
FROM node:20-alpine AS deps

WORKDIR /app
COPY src/frontend/package.json src/frontend/package-lock.json ./
RUN npm ci

# --- build ---
FROM node:20-alpine AS build

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY src/frontend ./
RUN npm run build

# --- runtime ---
FROM nginx:alpine AS runtime

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
```

### Rules

- Use `npm ci` (not `npm install`) in Docker — it respects the lockfile exactly.
- Copy `package.json` and `package-lock.json` before source code to cache the `npm ci` layer.
- The runtime stage contains only static files served by nginx.

---

## Docker Compose

```yaml
# docker/docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: oakbox
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?required}
      POSTGRES_DB: oakbox
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U oakbox"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ..
      dockerfile: docker/backend.Dockerfile
    ports:
      - "8000:8000"
    environment:
      OAKBOX_DATABASE_URL: postgresql+asyncpg://oakbox:${POSTGRES_PASSWORD}@db:5432/oakbox
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build:
      context: ..
      dockerfile: docker/frontend.Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  pgdata:
```

### Compose Rules

- All secrets and passwords passed via environment variables — never hard-coded.
- Use `${VAR:?required}` syntax to fail fast on missing env vars.
- Always define `healthcheck` on database services.
- Use `depends_on` with `condition: service_healthy` where supported.
- Bind-mount source code for local dev (override in `docker-compose.override.yml`).
- Named volumes for persistent data only (`pgdata`).

---

## .dockerignore

Place at project root (or copy into build context):

```
.git
.venv
__pycache__
node_modules
*.pyc
.env
.env.*
docker/
docs/
tests/
.oakbox/
*.md
!pyproject.toml
```

- Always ignore `.git`, `node_modules`, `.venv`, `__pycache__`, and `tests/`.
- Never ship `.env` files or documentation into images.

---

## Naming & Tagging

| Convention        | Format                               | Example                          |
|-------------------|--------------------------------------|----------------------------------|
| Image name        | `oakbox-<service>`                   | `oakbox-backend`                 |
| Dev tag           | `dev`                                | `oakbox-backend:dev`             |
| Release tag       | `<semver>`                           | `oakbox-backend:1.2.0`           |
| CI tag            | `<branch>-<short-sha>`               | `oakbox-backend:main-a1b2c3d`    |

---

## Security

- Run containers as non-root. Create a dedicated user in the Dockerfile.
- Never store secrets in image layers — use environment variables or mounted secrets.
- Scan images with `docker scout` or Trivy before release.
- Keep base images up to date — rebuild weekly in CI.
- No `--privileged` or `SYS_ADMIN` capabilities unless explicitly justified.

---

## Performance

- Order `COPY` instructions from least-to-most frequently changing to maximize cache.
- Use `.dockerignore` to minimize build context size.
- Combine `RUN` commands where it reduces layers without hurting readability.
- Never run `apt-get upgrade` in Dockerfiles — pin the base image version instead.
