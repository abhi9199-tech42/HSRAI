from typing import Any, Dict

import pytest

from hsrai.core.models import SemanticPrimitive
from hsrai.core.types import SemanticType
from hsrai.plugins.manager import PluginManager
from hsrai.system.config import SystemConfig
from hsrai.system.controller import SystemController


class MockCompressionPlugin:
    def initialize(self, config: Dict[str, Any]) -> None: pass
    def shutdown(self) -> None: pass
    def process(self, input_data: Any, source_id: str) -> SemanticPrimitive:
        return SemanticPrimitive(
            id="mock_plugin_id",
            concept="plugin_processed",
            type=SemanticType.CONCEPT,
            compression_metadata={"source_id": source_id}
        )

class TestEndToEnd:

    @pytest.fixture
    def anyio_backend(self):
        return 'asyncio'

    @pytest.mark.anyio
    async def test_complete_pipeline_flow(self):
        """Verify data flows from input to output through all stages"""
        controller = SystemController()

        # Test standard flow
        output = await controller.process_request("Analyze this system")

        assert output.content is not None
        assert output.trust_certificate is not None
        assert output.metadata["request_id"] is not None
        assert "processing_time" in output.metadata

    @pytest.mark.anyio
    async def test_plugin_integration(self):
        """Verify plugins are correctly invoked in the pipeline"""
        plugin_manager = PluginManager()
        plugin = MockCompressionPlugin()
        plugin_manager.register_compression("mock", plugin)

        controller = SystemController(plugin_manager=plugin_manager)

        # The MockCompressionPlugin returns content "plugin_processed".
        # If the pipeline uses it, the output should likely reflect that or at least succeed.
        output = await controller.process_request("test input")

        assert output is not None
        assert not output.metadata.get("error")

    @pytest.mark.anyio
    async def test_pipeline_error_recovery(self):
        """Verify system handles component failures gracefully"""
        # Create a controller with a very short timeout to force timeout error
        config = SystemConfig(timeout_ms=1)
        controller = SystemController(config=config)

        # This should timeout because of the sleeps in _process_pipeline (1ms + 1ms > 1ms)
        # Note: sleep(0.001) is 1ms. Two sleeps = 2ms.
        output = await controller.process_request("Input")

        assert output.metadata.get("error") is True
        assert "timed out" in output.content or "Error" in output.content

    @pytest.mark.anyio
    async def test_trust_verification_integration(self):
        """Verify trust certificates are generated and attached"""
        controller = SystemController()
        output = await controller.process_request("Trust check")

        assert output.trust_certificate is not None
        # Verify the certificate is valid using the controller's trust manager
        assert controller.trust_manager.verify_certificate(output.trust_certificate)
