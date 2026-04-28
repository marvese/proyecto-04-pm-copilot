from __future__ import annotations

import pytest


class TestChromaDBAdapter:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_upsert_and_search(self) -> None:
        # TODO: once ChromaDBAdapter is implemented:
        # - Connect to local ChromaDB Docker instance
        # - Upsert a document with a known embedding
        # - Search with the same embedding, assert score ~1.0
        pytest.skip("Not implemented yet")

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_filter_by_project_id(self) -> None:
        # TODO: assert search with filter={project_id: "A"} does not return docs for project "B"
        pytest.skip("Not implemented yet")
