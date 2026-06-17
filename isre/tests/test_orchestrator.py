import pytest
from unittest.mock import patch, MagicMock
from isre.pipeline.orchestrator import ISREPipeline


class TestISREPipeline:
    def test_init(self):
        pipeline = ISREPipeline()
        assert pipeline.compression is not None
        assert pipeline.graph_builder is not None
        assert pipeline.reasoning_gen is not None
        assert pipeline.selector is not None
        assert pipeline.knowledge_engine is not None
        assert pipeline.trace_log == []

    def test_process_returns_output(self):
        pipeline = ISREPipeline()
        result = pipeline.process("hello world", modality="text")
        assert isinstance(result, dict)
        assert "request_id" in result
        assert "outputs" in result

    def test_process_empty_string(self):
        pipeline = ISREPipeline()
        result = pipeline.process("", modality="text")
        assert isinstance(result, dict)
        assert "request_id" in result

    def test_trace_log_populated(self):
        pipeline = ISREPipeline()
        result = pipeline.process("test input", modality="text")
        request_id = result["request_id"]
        trace = pipeline.get_trace(request_id)
        assert len(trace) > 0
        stages = [entry["stage"] for entry in trace]
        assert "start" in stages

    def test_clear(self):
        pipeline = ISREPipeline()
        pipeline.process("test", modality="text")
        assert len(pipeline.trace_log) > 0
        pipeline.clear()
        assert pipeline.trace_log == []

    def test_get_trace_unknown_id(self):
        pipeline = ISREPipeline()
        trace = pipeline.get_trace("nonexistent")
        assert trace == []
