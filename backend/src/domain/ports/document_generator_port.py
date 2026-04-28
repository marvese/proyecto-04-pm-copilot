from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.report import Report, ReportFormat


class DocumentGeneratorPort(ABC):
    @abstractmethod
    async def generate(self, report: Report, format: ReportFormat) -> bytes:
        """Converts a Report to the requested binary format."""
        ...
