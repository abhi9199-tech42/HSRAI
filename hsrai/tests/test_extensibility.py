import json
import os
import tempfile
from typing import Any, Dict

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import SemanticType
from hsrai.plugins.manager import PluginManager
from hsrai.system.config import ConfigurationManager


class MockCompressionPlugin:
    def __init__(self):
        self.initialized = False
        self.config = {}

    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.initialized = True

    def shutdown(self) -> None:
        self.initialized = False

    def process(self, input_data: Any, source_id: str) -> SemanticPrimitive:
        return SemanticPrimitive(
            id=f"mock_{source_id}",
            concept="mock",
            type=SemanticType.CONCEPT,
            modality="text"
        )

class TestExtensibility:

    def test_plugin_interface_compliance(self):
        """Property 17: Plugin interface compliance"""
        # Verify that MockCompressionPlugin satisfies CompressionPlugin protocol
        plugin = MockCompressionPlugin()
        assert hasattr(plugin, 'initialize')
        assert hasattr(plugin, 'shutdown')
        assert hasattr(plugin, 'process')

        manager = PluginManager()
        manager.register_compression("mock", plugin)

        config = {"plugins": {"compression": {"mock": {"param": 1}}}}
        manager.initialize_all(config)

        assert plugin.initialized
        assert plugin.config == {"param": 1}

        manager.shutdown_all()
        assert not plugin.initialized

    @given(st.dictionaries(keys=st.text(), values=st.text()))
    @settings(deadline=None)
    def test_configuration_validity(self, settings):
        """Property 18: Configuration validity"""
        # Create a temp config file
        # We use delete=False because Windows can't open file twice if it's temp
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            json.dump({
                "environment": "testing",
                "max_concurrent_requests": 5,
                "custom_settings": settings
            }, f)
            f.close()
            config_path = f.name

            manager = ConfigurationManager(config_path)
            manager.load()

            assert manager.config.environment == "testing"
            assert manager.config.max_concurrent_requests == 5

            # Check dynamic loading via reload
            with open(config_path, 'w') as f_write:
                json.dump({
                    "environment": "production",
                    "max_concurrent_requests": 10
                }, f_write)

            manager.reload()
            assert manager.config.environment == "production"

        finally:
            if os.path.exists(f.name):
                os.remove(f.name)

    def test_invalid_configuration(self):
        """Property 18: Configuration validity (Error cases)"""
        f = tempfile.NamedTemporaryFile(mode='w', delete=False)
        try:
            json.dump({
                "environment": "invalid_env",
                "max_concurrent_requests": -1
            }, f)
            f.close()
            config_path = f.name

            manager = ConfigurationManager(config_path)
            with pytest.raises(ValueError):
                manager.load()
        finally:
            if os.path.exists(f.name):
                os.remove(f.name)
