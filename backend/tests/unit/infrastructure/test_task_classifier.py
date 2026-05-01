from __future__ import annotations

import pytest

from src.infrastructure.llm_router.task_classifier import TaskClassifier
from src.domain.ports.llm_port import LLMTaskType


class TestTaskClassifier:
    def setup_method(self) -> None:
        self.clf = TaskClassifier()

    def test_explicit_type_overrides_heuristic(self) -> None:
        result = self.clf.classify("classify this", explicit_type=LLMTaskType.REASONING)
        assert result == LLMTaskType.REASONING

    def test_reasoning_keyword_maps_to_reasoning(self) -> None:
        for kw in ("estimate", "analyze", "explain", "reason", "plan", "review"):
            result = self.clf.classify(f"please {kw} this task")
            assert result == LLMTaskType.REASONING, f"keyword '{kw}' should map to REASONING"

    def test_simple_keyword_maps_to_classification(self) -> None:
        for kw in ("classify", "extract", "status", "list"):
            result = self.clf.classify(f"please {kw} this")
            assert result == LLMTaskType.CLASSIFICATION, f"keyword '{kw}' should map to CLASSIFICATION"

    def test_unknown_prompt_defaults_to_simple_qa(self) -> None:
        result = self.clf.classify("what is the project?")
        assert result == LLMTaskType.SIMPLE_QA

    def test_case_insensitive_matching(self) -> None:
        assert self.clf.classify("ESTIMATE this") == LLMTaskType.REASONING
        assert self.clf.classify("CLASSIFY that") == LLMTaskType.CLASSIFICATION

    def test_empty_prompt_defaults_to_simple_qa(self) -> None:
        assert self.clf.classify("") == LLMTaskType.SIMPLE_QA
