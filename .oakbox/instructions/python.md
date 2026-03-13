# Python Conventions & Style Guide

## Runtime & Package Management

- **Python version:** 3.12 (enforced via `.python-version`)
- **Package manager:** [uv](https://github.com/astral-sh/uv)
- **Lock file:** `uv.lock` — always commit this file
- **Virtual env:** `.venv/` at project root (created by `uv sync`)

### Common commands

```bash
uv sync                  # Install all dependencies from uv.lock
uv add <package>         # Add a production dependency
uv add --dev <package>   # Add a development dependency
uv remove <package>      # Remove a dependency
uv run <command>         # Run a command inside the venv
uv run python <script>   # Run a script
```

> Never use `pip install` directly. All dependency changes go through `uv`.

---

## Project Layout

```
src/
  backend/
    __init__.py
    main.py              # Application entry point
    api/                  # Route handlers (one module per resource)
      __init__.py
      routes_<resource>.py
    models/               # SQLAlchemy / Pydantic models
      __init__.py
    services/             # Business logic (no framework imports)
      __init__.py
    repositories/         # Database access layer
      __init__.py
    schemas/              # Pydantic request/response schemas
      __init__.py
    config.py             # Settings via pydantic-settings
    dependencies.py       # Dependency injection helpers
tests/
  backend/
    conftest.py
    test_<module>.py
pyproject.toml
uv.lock
.python-version
```

---

## Code Style

### Formatting & Linting

- **Formatter:** `ruff format` (line length 88)
- **Linter:** `ruff check` with the following rule sets enabled:

```toml
# pyproject.toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = [
  "E",    # pycodestyle errors
  "W",    # pycodestyle warnings
  "F",    # pyflakes
  "I",    # isort
  "N",    # pep8-naming
  "UP",   # pyupgrade
  "B",    # flake8-bugbear
  "SIM",  # flake8-simplify
  "TCH",  # flake8-type-checking
  "RUF",  # ruff-specific rules
]
```

### Naming Conventions

| Construct        | Convention            | Example                    |
|------------------|-----------------------|----------------------------|
| Module           | `snake_case`          | `user_service.py`          |
| Class            | `PascalCase`          | `UserService`              |
| Function/method  | `snake_case`          | `get_active_users()`       |
| Variable         | `snake_case`          | `user_count`               |
| Constant         | `UPPER_SNAKE_CASE`    | `MAX_RETRY_COUNT`          |
| Type alias       | `PascalCase`          | `UserId = int`             |
| Private          | `_leading_underscore` | `_internal_helper()`       |
| Protected        | `_leading_underscore` | `_validate()`              |

### Type Annotations

- All function signatures **must** have type annotations for parameters and return values.
- Use built-in generics (`list[str]`, `dict[str, int]`) — not `typing.List`, `typing.Dict`.
- Use `X | None` — not `Optional[X]`.
- Use `type` keyword for simple type aliases: `type UserId = int`.

```python
def get_user(user_id: int) -> User | None:
    ...
```

### Imports

- Sort with `ruff` (isort-compatible).
- Order: stdlib → third-party → local. One blank line between groups.
- Absolute imports only. No relative imports.

```python
import os
from collections.abc import Sequence

from fastapi import Depends, HTTPException

from backend.models.user import User
from backend.services.user_service import UserService
```

### String Formatting

- Use f-strings for interpolation.
- Use `"""triple quotes"""` for docstrings.
- No single-vs-double preference enforced — `ruff format` normalizes to double quotes.

### Error Handling

- Catch specific exceptions, never bare `except:`.
- Use custom exception classes that inherit from a project-level base exception.
- Let unexpected errors propagate — do not silently swallow.

```python
class OakBoxError(Exception):
    """Base exception for all OakBox errors."""

class UserNotFoundError(OakBoxError):
    """Raised when a user lookup fails."""
```

### Dataclasses & Pydantic

- Use **Pydantic `BaseModel`** for API schemas (request/response bodies).
- Use **`dataclasses.dataclass`** or **`attrs`** for internal value objects not crossing API boundaries.
- Use `model_config = ConfigDict(strict=True)` on Pydantic models.

---

## Testing

- **Framework:** `pytest`
- **Runner:** `uv run pytest`
- **Fixtures directory:** `tests/conftest.py` (shared), per-module `conftest.py` allowed.
- **Naming:** test files `test_<module>.py`, test functions `test_<behavior>`.
- **Markers:** use `@pytest.mark.slow` for integration tests.
- **Coverage:** `pytest-cov`, target ≥ 80%.

```bash
uv run pytest                       # Run all tests
uv run pytest tests/backend/        # Run backend tests
uv run pytest -k "test_user"        # Run matching tests
uv run pytest --cov=src/backend     # With coverage
```

### Test structure (Arrange-Act-Assert)

```python
def test_create_user_returns_user_with_id(db_session):
    # Arrange
    payload = CreateUserRequest(name="Alice", email="alice@example.com")
    service = UserService(session=db_session)

    # Act
    user = service.create(payload)

    # Assert
    assert user.id is not None
    assert user.name == "Alice"
```

---

## Database

- **ORM:** SQLAlchemy 2.x with async engine.
- **Migrations:** Alembic (`uv run alembic upgrade head`).
- **Models:** mapped classes using `DeclarativeBase` and `Mapped[]` annotations.

---

## Configuration

All runtime config via environment variables, loaded through `pydantic-settings`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    log_level: str = "INFO"

    model_config = ConfigDict(env_prefix="OAKBOX_")
```

---

## Logging

- Use `structlog` for structured JSON logging.
- Never use `print()` in production code.
- Log levels: `DEBUG` for tracing, `INFO` for events, `WARNING` for recoverable issues, `ERROR` for failures.
