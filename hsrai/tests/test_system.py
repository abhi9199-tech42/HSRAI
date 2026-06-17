import pytest
import asyncio
from hsrai.system.controller import SystemController, SystemConfig

class TestSystemReliability:
    
    @pytest.fixture
    def anyio_backend(self):
        return 'asyncio'
    
    @pytest.mark.anyio
    async def test_concurrent_request_isolation(self):
        """Property 15: Concurrent request isolation"""
        controller = SystemController()
        
        # Define tasks
        input_1 = "Request One"
        input_2 = "Request Two"
        
        task1 = controller.process_request(input_1, request_id="req1")
        task2 = controller.process_request(input_2, request_id="req2")
        
        # Run concurrently
        result1, result2 = await asyncio.gather(task1, task2)
        
        # Verify isolation
        assert result1.metadata["request_id"] == "req1"
        assert result2.metadata["request_id"] == "req2"
        assert "Request One" in result1.content
        assert "Request Two" in result2.content

    @pytest.mark.anyio
    async def test_error_recovery_stability(self):
        """Property 16: Error recovery stability"""
        # Set a very short timeout to force timeout error
        config = SystemConfig(timeout_ms=1) 
        controller = SystemController(config)
        
        # This simulates a slow operation (relative to timeout)
        # Note: The actual processing might be fast, but 1ms is very strict.
        # If it's too fast, we might pass. Let's mock if needed, but try real first.
        
        result = await controller.process_request("Heavy computation", request_id="timeout_req")
        
        # Should return error response, not raise exception
        assert result.metadata.get("error") is True
        assert "timed out" in result.content or "Error" in result.content
        
        # System should still be usable (if we increase timeout)
        controller.config.timeout_ms = 5000
        result_ok = await controller.process_request("Normal request")
        assert not result_ok.metadata.get("error")

    @pytest.mark.anyio
    async def test_graceful_degradation(self):
        """Verify system handles load gracefully"""
        # Limit concurrency to 1
        config = SystemConfig(max_concurrent_requests=1)
        controller = SystemController(config)
        
        # Launch 3 requests. They should execute sequentially or queue.
        # We just want to ensure they all complete eventually.
        tasks = [
            controller.process_request(f"Req {i}", request_id=f"id_{i}")
            for i in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for res in results:
            assert not res.metadata.get("error")
