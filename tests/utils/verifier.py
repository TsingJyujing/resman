import numbers
from typing import Dict, List

import pytest

from utils.verifier import verify_json_fields, FieldError


def test_verify_json_fields():
    verify_json_fields(
        {"a": 1, "b": "2", "c": {}, "d": []},
        ["a", "b", "c", "d"]
    )
    verify_json_fields(
        {"a": 1, "b": "2", "c": {}, "d": []},
        {"a": numbers.Real, "b": str, "c": Dict, "d": List},
    )
    with pytest.raises(FieldError):
        verify_json_fields(
            {"a": 1, "b": "2", "c": {}},
            {"a": numbers.Real, "b": str, "c": Dict, "d": List},
        )
    with pytest.raises(FieldError):
        verify_json_fields(
            {"a": 1, "b": "2", "c": {}},
            {"a": numbers.Real, "b": str, "c": str},
        )
