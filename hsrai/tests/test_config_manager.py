import json
import os
import tempfile

import pytest

from hsrai.system.config import ConfigurationManager, SystemConfig


class TestSystemConfig:
    def test_default_environment(self):
        config = SystemConfig()
        assert config.environment == "development"

    def test_default_debug(self):
        config = SystemConfig()
        assert config.debug is False

    def test_default_max_concurrent_requests(self):
        config = SystemConfig()
        assert config.max_concurrent_requests == 10

    def test_default_timeout_ms(self):
        config = SystemConfig()
        assert config.timeout_ms == 5000

    def test_default_plugins(self):
        config = SystemConfig()
        assert config.plugins == {}

    def test_from_dict_custom_values(self):
        config = SystemConfig.from_dict({
            "environment": "production",
            "debug": True,
            "max_concurrent_requests": 50,
        })
        assert config.environment == "production"
        assert config.debug is True
        assert config.max_concurrent_requests == 50

    def test_from_dict_ignores_unknown_keys(self):
        config = SystemConfig.from_dict({"environment": "testing", "unknown_key": "value"})
        assert config.environment == "testing"


class TestConfigurationManager:
    def test_load_from_valid_file(self):
        data = {"environment": "production", "debug": True}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            mgr = ConfigurationManager(path)
            mgr.load()
            assert mgr.config.environment == "production"
            assert mgr.config.debug is True
        finally:
            os.unlink(path)

    def test_load_from_missing_file_raises(self):
        mgr = ConfigurationManager("nonexistent_config_path.json")
        with pytest.raises(FileNotFoundError):
            mgr.load()

    def test_load_invalid_environment_raises(self):
        data = {"environment": "invalid_env"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            mgr = ConfigurationManager(path)
            with pytest.raises(ValueError, match="Invalid environment"):
                mgr.load()
        finally:
            os.unlink(path)

    def test_load_invalid_max_concurrent_raises(self):
        data = {"max_concurrent_requests": 0}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            mgr = ConfigurationManager(path)
            with pytest.raises(ValueError, match="max_concurrent_requests must be positive"):
                mgr.load()
        finally:
            os.unlink(path)

    def test_get_returns_default_for_missing_key(self):
        mgr = ConfigurationManager("nonexistent.json")
        assert mgr.get("missing_key", "fallback") == "fallback"

    def test_subscribe_callback_called(self):
        data = {"environment": "testing"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            mgr = ConfigurationManager(path)
            called_with = []
            mgr.subscribe(lambda cfg: called_with.append(cfg))
            mgr.load()
            assert len(called_with) == 1
            assert called_with[0].environment == "testing"
        finally:
            os.unlink(path)

    def test_reload(self):
        data = {"environment": "testing"}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            mgr = ConfigurationManager(path)
            mgr.load()
            assert mgr.config.environment == "testing"
            # Overwrite file
            with open(path, "w") as f2:
                json.dump({"environment": "production"}, f2)
            mgr.reload()
            assert mgr.config.environment == "production"
        finally:
            os.unlink(path)
