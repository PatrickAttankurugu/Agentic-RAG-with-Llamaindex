"""Unit tests for the benchmark suite."""

import json
import pytest
from unittest.mock import MagicMock
from pathlib import Path

from src.evaluation.benchmarks import BenchmarkSuite, BenchmarkCase, SuiteResults
from src.models.schemas import QueryResponse


class TestBenchmarkSuite:
    def _make_mock_service(self, answers: dict):
        """Create a mock RAG service that returns predefined answers."""
        service = MagicMock()

        def mock_query(request):
            answer_text = answers.get(request.query, "no answer")
            return QueryResponse(
                query=request.query,
                answer=answer_text,
                latency_ms=50.0,
            )

        service.query.side_effect = mock_query
        return service

    def test_run_with_matching_keywords(self):
        cases = [
            BenchmarkCase(
                question="What is RAG?",
                expected_keywords=["retrieval", "generation"],
            )
        ]
        service = self._make_mock_service(
            {"What is RAG?": "Retrieval-augmented generation combines retrieval and generation."}
        )

        suite = BenchmarkSuite(cases)
        results = suite.run(service)

        assert results.total_cases == 1
        assert results.passed == 1
        assert results.errors == 0
        assert results.avg_keyword_precision == 1.0

    def test_partial_keyword_match(self):
        cases = [
            BenchmarkCase(
                question="What is RAG?",
                expected_keywords=["retrieval", "quantum"],
            )
        ]
        service = self._make_mock_service(
            {"What is RAG?": "Retrieval-augmented generation."}
        )

        suite = BenchmarkSuite(cases)
        results = suite.run(service)

        assert results.total_cases == 1
        assert results.avg_keyword_precision == 0.5

    def test_error_handling(self):
        cases = [BenchmarkCase(question="fail")]
        service = MagicMock()
        service.query.side_effect = RuntimeError("boom")

        suite = BenchmarkSuite(cases)
        results = suite.run(service)

        assert results.total_cases == 1
        assert results.errors == 1
        assert results.passed == 0

    def test_from_json(self, tmp_path):
        data = {
            "cases": [
                {"question": "Q1", "expected_keywords": ["kw1"], "category": "test"},
                {"question": "Q2", "expected_keywords": []},
            ]
        }
        path = tmp_path / "bench.json"
        path.write_text(json.dumps(data))

        suite = BenchmarkSuite.from_json(str(path))
        assert len(suite.cases) == 2
        assert suite.cases[0].category == "test"
        assert suite.cases[1].category == "general"

    def test_save_results(self, tmp_path):
        results = SuiteResults(
            total_cases=1,
            passed=1,
            failed=0,
            errors=0,
            avg_latency_ms=50.0,
            p95_latency_ms=50.0,
            avg_keyword_precision=1.0,
        )
        path = tmp_path / "results.json"
        BenchmarkSuite.save_results(results, str(path))

        loaded = json.loads(path.read_text())
        assert loaded["total_cases"] == 1
        assert loaded["avg_keyword_precision"] == 1.0
