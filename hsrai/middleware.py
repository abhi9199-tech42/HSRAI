"""Production middleware: authentication, rate limiting, metrics."""

import asyncio
import logging
import time
from collections import defaultdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class APIKeyAuth:
    """API key authentication middleware."""

    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        self.api_keys = api_keys or {}

    def add_key(self, key: str, label: str = "default"):
        self.api_keys[key] = label

    def __call__(self, key: Optional[str]) -> bool:
        if not self.api_keys:
            return True
        if key is None:
            return False
        return key in self.api_keys


class RateLimiter:
    """Token bucket rate limiter per client."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60, max_clients: int = 10000):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_clients = max_clients
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes

    async def check(self, client_id: str) -> bool:
        async with self._lock:
            now = time.time()
            cutoff = now - self.window_seconds
            self._requests[client_id] = [
                t for t in self._requests[client_id] if t > cutoff
            ]
            if len(self._requests[client_id]) >= self.max_requests:
                return False
            self._requests[client_id].append(now)
            await self._maybe_cleanup(now)
            return True

    async def _maybe_cleanup(self, now: float):
        """Periodically clean up inactive clients to prevent memory leak."""
        if now - self._last_cleanup < self._cleanup_interval:
            return
        if len(self._requests) <= self.max_clients:
            self._last_cleanup = now
            return

        cutoff = now - self.window_seconds
        # Remove clients with no recent requests
        to_remove = [
            client_id for client_id, timestamps in self._requests.items()
            if not any(t > cutoff for t in timestamps)
        ]
        for client_id in to_remove:
            del self._requests[client_id]

        # If still too many, remove oldest
        if len(self._requests) > self.max_clients:
            sorted_clients = sorted(
                self._requests.items(),
                key=lambda kv: max(kv[1]) if kv[1] else 0
            )
            to_remove = len(self._requests) - self.max_clients
            for client_id, _ in sorted_clients[:to_remove]:
                del self._requests[client_id]

        self._last_cleanup = now

    def get_remaining(self, client_id: str) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        recent = [t for t in self._requests.get(client_id, []) if t > cutoff]
        return max(0, self.max_requests - len(recent))


class MetricsCollector:
    """Simple in-memory Prometheus-style metrics."""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        self.request_times: list = []
        self.certificates_issued = 0

    def record_request(self, duration: float, success: bool = True):
        self.request_count += 1
        self.total_processing_time += duration
        self.request_times.append(duration)
        if len(self.request_times) > 10000:
            self.request_times = self.request_times[-5000:]
        if not success:
            self.error_count += 1

    def record_certificate(self):
        self.certificates_issued += 1

    def get_metrics(self) -> dict:
        avg_time = (
            self.total_processing_time / self.request_count
            if self.request_count > 0
            else 0.0
        )
        p99 = 0.0
        if self.request_times:
            sorted_times = sorted(self.request_times)
            idx = int(len(sorted_times) * 0.99)
            p99 = sorted_times[min(idx, len(sorted_times) - 1)]
        return {
            "requests_total": self.request_count,
            "errors_total": self.error_count,
            "avg_processing_time": round(avg_time, 4),
            "p99_processing_time": round(p99, 4),
            "certificates_issued": self.certificates_issued,
        }

    def prometheus_text(self) -> str:
        m = self.get_metrics()
        lines = [
            "# HELP hsrai_requests_total Total number of requests",
            "# TYPE hsrai_requests_total counter",
            f"hsrai_requests_total {m['requests_total']}",
            "# HELP hsrai_errors_total Total number of errors",
            "# TYPE hsrai_errors_total counter",
            f"hsrai_errors_total {m['errors_total']}",
            "# HELP hsrai_processing_time_seconds Average processing time",
            "# TYPE hsrai_processing_time_seconds gauge",
            f"hsrai_processing_time_seconds {m['avg_processing_time']}",
            "# HELP hsrai_p99_processing_time_seconds P99 processing time",
            "# TYPE hsrai_p99_processing_time_seconds gauge",
            f"hsrai_p99_processing_time_seconds {m['p99_processing_time']}",
            "# HELP hsrai_certificates_issued Total certificates issued",
            "# TYPE hsrai_certificates_issued counter",
            f"hsrai_certificates_issued {m['certificates_issued']}",
        ]
        return "\n".join(lines) + "\n"
