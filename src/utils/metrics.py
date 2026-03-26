"""Monitoring and metrics tracking"""

import threading
from typing import Dict, Any, List
from datetime import datetime
import statistics


class MetricsCollector:
    """Thread-safe metrics collector for RAG system"""

    def __init__(self):
        self._lock = threading.Lock()
        self.query_latencies: List[float] = []
        self.query_count = 0
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def record_query(self, latency_ms: float, success: bool = True):
        """Record query metrics"""
        with self._lock:
            self.query_count += 1
            self.query_latencies.append(latency_ms)
            if not success:
                self.error_count += 1

    def record_cache_hit(self):
        """Record cache hit"""
        with self._lock:
            self.cache_hits += 1

    def record_cache_miss(self):
        """Record cache miss"""
        with self._lock:
            self.cache_misses += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics"""
        with self._lock:
            if not self.query_latencies:
                return {
                    "query_count": 0,
                    "error_count": 0,
                    "avg_latency_ms": 0,
                    "p95_latency_ms": 0,
                    "p99_latency_ms": 0,
                    "cache_hit_rate": 0,
                }

            sorted_latencies = sorted(self.query_latencies)
            n = len(sorted_latencies)

            total_cache = self.cache_hits + self.cache_misses
            cache_hit_rate = self.cache_hits / total_cache if total_cache > 0 else 0

            p95_idx = min(int(n * 0.95), n - 1)
            p99_idx = min(int(n * 0.99), n - 1)

            return {
                "query_count": self.query_count,
                "error_count": self.error_count,
                "success_rate": (
                    (self.query_count - self.error_count) / self.query_count
                    if self.query_count > 0
                    else 0
                ),
                "avg_latency_ms": statistics.mean(self.query_latencies),
                "p95_latency_ms": sorted_latencies[p95_idx],
                "p99_latency_ms": sorted_latencies[p99_idx],
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "cache_hit_rate": cache_hit_rate,
            }

    def reset(self):
        """Reset all metrics"""
        with self._lock:
            self.query_latencies.clear()
            self.query_count = 0
            self.error_count = 0
            self.cache_hits = 0
            self.cache_misses = 0


# Global metrics collector
_metrics = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector"""
    return _metrics
