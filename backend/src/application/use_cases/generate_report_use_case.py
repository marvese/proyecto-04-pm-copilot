from __future__ import annotations

from ...domain.entities.report import Report
from ...domain.ports.confluence_port import ConfluencePort
from ...domain.ports.document_generator_port import DocumentGeneratorPort
from ...domain.ports.llm_port import LLMPort
from ...domain.ports.sprint_repository_port import SprintRepositoryPort
from ...domain.ports.task_repository_port import TaskRepositoryPort
from ..commands.generate_report_command import GenerateReportCommand


class GenerateReportUseCase:
    def __init__(
        self,
        llm_port: LLMPort,
        task_repo: TaskRepositoryPort,
        sprint_repo: SprintRepositoryPort,
        doc_generator: DocumentGeneratorPort,
        confluence_port: ConfluencePort,
    ) -> None:
        self._llm = llm_port
        self._task_repo = task_repo
        self._sprint_repo = sprint_repo
        self._doc_generator = doc_generator
        self._confluence = confluence_port

    async def execute(self, command: GenerateReportCommand) -> Report:
        # TODO: implement
        # 1. Gather project/sprint metrics
        # 2. Build prompt with context
        # 3. Call LLM to generate report content
        # 4. If format=CONFLUENCE: publish via confluence_port
        # 5. Return Report entity
        raise NotImplementedError
