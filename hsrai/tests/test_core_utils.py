import pytest
from hsrai.core.utils import deterministic_id


class TestDeterministicId:
    def test_returns_string(self):
        result = deterministic_id({"key": "value"})
        assert isinstance(result, str)

    def test_same_input_same_output(self):
        data = {"a": 1, "b": "hello"}
        assert deterministic_id(data) == deterministic_id(data)

    def test_different_input_different_output(self):
        assert deterministic_id({"a": 1}) != deterministic_id({"a": 2})

    def test_output_length_is_64(self):
        result = deterministic_id({"x": 10})
        assert len(result) == 64

    def test_empty_dict_input(self):
        result = deterministic_id({})
        assert isinstance(result, str)
        assert len(result) == 64

    def test_key_order_does_not_matter(self):
        assert deterministic_id({"a": 1, "b": 2}) == deterministic_id({"b": 2, "a": 1})
