from __future__ import annotations

from ...domain.ports.llm_port import LLMTaskType


REASONING_KEYWORDS = frozenset({"estimate", "analyze", "explain", "reason", "plan", "review"})
SIMPLE_KEYWORDS = frozenset({"classify", "extract", "yes", "no", "status", "list"})


class TaskClassifier:
    """Determines the LLMTaskType from a prompt to enable cost-optimized routing."""

    def classify(self, prompt: str, explicit_type: LLMTaskType | None = None) -> LLMTaskType:
        if explicit_type is not None:
            return explicit_type

        # TODO: implement heuristic + optional LLM-assisted classification
        # Simple keyword matching for now; replace with lightweight LLM call if needed
        lower = prompt.lower()
        if any(kw in lower for kw in REASONING_KEYWORDS):
            return LLMTaskType.REASONING
        if any(kw in lower for kw in SIMPLE_KEYWORDS):
            return LLMTaskType.CLASSIFICATION
        return LLMTaskType.SIMPLE_QA
