"""
Benchmark suite for evaluating RAG agent quality and performance.

Usage:
    from src.evaluation.benchmarks import BenchmarkSuite
    suite = BenchmarkSuite.from_json("benchmarks/sample_benchmark.json")
    results = suite.run(rag_service)
    suite.save_results(results, "results.json")
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.models.schemas import QueryRequest
from src.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class BenchmarkCase:
    """A single question-answer benchmark case."""
    question: str
    expected_keywords: List[str] = field(default_factory=list)
    category: str = "general"


@dataclass
class BenchmarkResult:
    """Result of running a single benchmark case."""
    question: str
    answer: str
    latency_ms: float
    keyword_hits: int
    keyword_total: int
    keyword_precision: float
    category: str
    error: Optional[str] = None


@dataclass
class SuiteResults:
    """Aggregate results from a full benchmark run."""
    total_cases: int
    passed: int
    failed: int
    errors: int
    avg_latency_ms: float
    p95_latency_ms: float
    avg_keyword_precision: float
    results: List[Dict[str, Any]] = field(default_factory=list)


class BenchmarkSuite:
    """Runs a set of Q&A benchmark cases against a RAG service."""

    def __init__(self, cases: List[BenchmarkCase]):
        self.cases = cases

    @classmethod
    def from_json(cls, path: str) -> BenchmarkSuite:
        """Load benchmark cases from a JSON file.

        Expected format:
        {
            "cases": [
                {"question": "...", "expected_keywords": ["..."], "category": "..."}
            ]
        }
        """
        data = json.loads(Path(path).read_text())
        cases = [BenchmarkCase(**c) for c in data["cases"]]
        logger.info(f"Loaded {len(cases)} benchmark cases from {path}")
        return cls(cases)

    def run(self, rag_service: Any) -> SuiteResults:
        """Run all benchmark cases against the given RAG service.

        Args:
            rag_service: An initialized RAGService with an active agent.

        Returns:
            SuiteResults with per-case and aggregate metrics.
        """
        results: List[BenchmarkResult] = []

        for case in self.cases:
            result = self._run_case(rag_service, case)
            results.append(result)
            status = "PASS" if result.error is None else "ERROR"
            logger.info(
                f"[{status}] {case.question[:60]}... "
                f"({result.latency_ms:.0f}ms, precision={result.keyword_precision:.2f})"
            )

        return self._aggregate(results)

    def _run_case(self, rag_service: Any, case: BenchmarkCase) -> BenchmarkResult:
        """Run a single benchmark case."""
        try:
            start = time.time()
            response = rag_service.query(QueryRequest(query=case.question))
            latency_ms = (time.time() - start) * 1000

            answer_lower = response.answer.lower()
            hits = sum(1 for kw in case.expected_keywords if kw.lower() in answer_lower)
            total = len(case.expected_keywords)
            precision = hits / total if total > 0 else 1.0

            return BenchmarkResult(
                question=case.question,
                answer=response.answer,
                latency_ms=latency_ms,
                keyword_hits=hits,
                keyword_total=total,
                keyword_precision=precision,
                category=case.category,
            )
        except Exception as e:
            return BenchmarkResult(
                question=case.question,
                answer="",
                latency_ms=0.0,
                keyword_hits=0,
                keyword_total=len(case.expected_keywords),
                keyword_precision=0.0,
                category=case.category,
                error=str(e),
            )

    def _aggregate(self, results: List[BenchmarkResult]) -> SuiteResults:
        """Compute aggregate metrics from individual results."""
        errors = [r for r in results if r.error is not None]
        passed = [r for r in results if r.error is None]

        latencies = sorted([r.latency_ms for r in passed]) if passed else [0.0]
        precisions = [r.keyword_precision for r in passed] if passed else [0.0]

        n = len(latencies)
        p95_idx = min(int(n * 0.95), n - 1)

        return SuiteResults(
            total_cases=len(results),
            passed=len(passed),
            failed=sum(1 for r in passed if r.keyword_precision < 0.5),
            errors=len(errors),
            avg_latency_ms=sum(latencies) / len(latencies),
            p95_latency_ms=latencies[p95_idx],
            avg_keyword_precision=sum(precisions) / len(precisions),
            results=[asdict(r) for r in results],
        )

    @staticmethod
    def save_results(results: SuiteResults, path: str) -> None:
        """Save benchmark results to a JSON file."""
        Path(path).write_text(json.dumps(asdict(results), indent=2))
        logger.info(f"Results saved to {path}")
