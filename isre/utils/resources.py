import time
import psutil # Assuming psutil is available or we mock it
import os

class ResourceMonitor:
    """
    Monitors system resources to support graceful degradation.
    Requirement 7.4, 7.5.
    """
    
    def __init__(self, memory_threshold_mb: float = 1000.0):
        self.memory_threshold = memory_threshold_mb
        self.process = psutil.Process(os.getpid())

    def get_memory_usage(self) -> float:
        """Returns memory usage in MB."""
        return self.process.memory_info().rss / (1024 * 1024)

    def is_resource_constrained(self) -> bool:
        return self.get_memory_usage() > self.memory_threshold

    def get_status(self) -> dict:
        return {
            "timestamp": time.time(),
            "memory_mb": self.get_memory_usage(),
            "constrained": self.is_resource_constrained()
        }
