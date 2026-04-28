from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import AsyncIterator, Optional


class LLMTaskType(str, Enum):
    REASONING = "reasoning"
    GENERATION_LONG = "generation_long"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    SIMPLE_QA = "simple_qa"


@dataclass
class LLMRequest:
    prompt: str
    task_type: LLMTaskType
    system: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.7
    json_mode: bool = False


@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int


class LLMPort(ABC):
    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Single-shot completion."""
        ...

    @abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncIterator[str]:
        """Streaming completion — yields tokens."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Returns True if provider is reachable."""
        ...
