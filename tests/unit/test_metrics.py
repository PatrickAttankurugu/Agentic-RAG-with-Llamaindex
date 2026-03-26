"""Unit tests for the MetricsCollector."""

import threading
import pytest

from src.utils.metrics import MetricsCollector, get_metrics_collector


class TestMetricsCollector:
    def test_initial_state(self):
        mc = MetricsCollector()
        metrics = mc.get_metrics()
        assert metrics["query_count"] == 0
        assert metrics["error_count"] == 0
        assert metrics["avg_latency_ms"] == 0
        assert metrics["cache_hit_rate"] == 0

    def test_record_query_success(self):
        mc = MetricsCollector()
        mc.record_query(100.0, success=True)
        mc.record_query(200.0, success=True)

        metrics = mc.get_metrics()
        assert metrics["query_count"] == 2
        assert metrics["error_count"] == 0
        assert metrics["avg_latency_ms"] == 150.0

    def test_record_query_failure(self):
        mc = MetricsCollector()
        mc.record_query(50.0, success=False)

        metrics = mc.get_metrics()
        assert metrics["query_count"] == 1
        assert metrics["error_count"] == 1
        assert metrics["success_rate"] == 0.0

    def test_success_rate(self):
        mc = MetricsCollector()
        mc.record_query(10.0, success=True)
        mc.record_query(10.0, success=True)
        mc.record_query(10.0, success=False)

        metrics = mc.get_metrics()
        assert abs(metrics["success_rate"] - 2 / 3) < 0.001

    def test_cache_hit_rate(self):
        mc = MetricsCollector()
        mc.record_query(10.0)  # need at least one query for full metrics
        mc.record_cache_hit()
        mc.record_cache_hit()
        mc.record_cache_miss()

        metrics = mc.get_metrics()
        assert abs(metrics["cache_hit_rate"] - 2 / 3) < 0.001
        assert metrics["cache_hits"] == 2
        assert metrics["cache_misses"] == 1

    def test_percentiles_single_value(self):
        mc = MetricsCollector()
        mc.record_query(42.0)

        metrics = mc.get_metrics()
        assert metrics["p95_latency_ms"] == 42.0
        assert metrics["p99_latency_ms"] == 42.0

    def test_percentiles_multiple_values(self):
        mc = MetricsCollector()
        for i in range(100):
            mc.record_query(float(i))

        metrics = mc.get_metrics()
        assert metrics["p95_latency_ms"] == 95.0
        assert metrics["p99_latency_ms"] == 99.0

    def test_reset(self):
        mc = MetricsCollector()
        mc.record_query(100.0)
        mc.record_cache_hit()
        mc.reset()

        metrics = mc.get_metrics()
        assert metrics["query_count"] == 0
        assert metrics["cache_hit_rate"] == 0

    def test_thread_safety(self):
        mc = MetricsCollector()
        errors = []

        def record_queries():
            try:
                for _ in range(100):
                    mc.record_query(10.0)
                    mc.record_cache_hit()
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record_queries) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        metrics = mc.get_metrics()
        assert metrics["query_count"] == 1000
        assert metrics["cache_hits"] == 1000


class TestGetMetricsCollector:
    def test_returns_singleton(self):
        mc1 = get_metrics_collector()
        mc2 = get_metrics_collector()
        assert mc1 is mc2
