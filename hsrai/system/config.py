from typing import Dict, Any, List, Callable
import json
import os
from dataclasses import dataclass, field

@dataclass
class SystemConfig:
    environment: str = "development"
    debug: bool = False
    max_concurrent_requests: int = 10
    timeout_ms: int = 5000
    plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemConfig':
        # Filter unknown keys to avoid TypeError
        valid_keys = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

class ConfigurationManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: SystemConfig = SystemConfig()
        self.raw_config: Dict[str, Any] = {}
        self.subscribers: List[Callable[[SystemConfig], None]] = []

    def load(self) -> None:
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.raw_config = json.load(f)
            self.validate(self.raw_config)
            self.config = SystemConfig.from_dict(self.raw_config)
            self.notify_subscribers()

    def validate(self, config: Dict[str, Any]) -> None:
        # Basic validation
        if "environment" in config and config["environment"] not in ["development", "production", "testing"]:
            raise ValueError(f"Invalid environment: {config['environment']}")
        if "max_concurrent_requests" in config and config["max_concurrent_requests"] < 1:
            raise ValueError("max_concurrent_requests must be positive")

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw_config.get(key, default)

    def subscribe(self, callback: Callable[[SystemConfig], None]):
        self.subscribers.append(callback)

    def notify_subscribers(self):
        for callback in self.subscribers:
            callback(self.config)
            
    def reload(self):
        self.load()
