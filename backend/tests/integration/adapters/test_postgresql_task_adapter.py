from __future__ import annotations

import pytest

# Integration tests run against a real PostgreSQL instance.
# In CI: use Docker service container. In local: docker-compose up.


class TestPostgreSQLTaskAdapter:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_save_and_retrieve_task(self) -> None:
        # TODO: once ORM models and adapter are implemented:
        # - Create real DB session (fixture)
        # - adapter.save(task) → adapter.get_by_id(task.id)
        # - Assert fields match
        pytest.skip("Not implemented yet")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_list_pending_jira_sync(self) -> None:
        # TODO: insert tasks with different sync statuses, assert only PENDING returned
        pytest.skip("Not implemented yet")
