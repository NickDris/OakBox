# Project Context

This file describes the current state of the OakBox project. Agents should read
this before starting work to understand the system as a whole.

## Tech Stack

- **Backend:** Python 3.12
- **Frontend:** React with TypeScript
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **Testing:** pytest (Python), Vitest/Jest (React)
- **Linting:** ruff (Python), ESLint + TypeScript strict (React)

## Project Structure

- `src/` — application source code (backend & frontend)
- `tests/` — test suite
- `docker/` — Dockerfiles and compose configuration
- `docs/` — generated documentation
- `.oakbox/` — agent scaffolding (prompts, status, memory, workflows)

## Conventions

- Python: type hints everywhere, ruff formatting, async where beneficial
- React: functional components, hooks only, no `any` types
- Docker: multi-stage builds, non-root containers
- APIs: RESTful by default, consider GraphQL for complex query needs
- Env config: all secrets/config via environment variables, never hardcoded

## Current State

The project is freshly scaffolded. No application code exists yet. The agent
pipeline is set up and ready to process feature requests.
