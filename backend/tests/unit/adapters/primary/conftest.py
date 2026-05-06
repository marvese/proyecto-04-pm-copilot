from __future__ import annotations

import pytest

from src.adapters.primary.api.auth_router import require_auth
from src.infrastructure.main import app


@pytest.fixture()
def bypass_auth():
    """Override require_auth so tests don't need a real JWT."""
    app.dependency_overrides[require_auth] = lambda: {"sub": "test-user", "email": "test@test.com"}
    yield
    app.dependency_overrides.pop(require_auth, None)
