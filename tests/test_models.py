from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from agastya_ai.executor import (
    build_path,
    compare_json_subset,
    validate_target,
)
from agastya_ai.models import TestScenario as ScenarioModel


def test_valid_scenario_is_accepted():
    scenario = ScenarioModel(
        name="Retrieve an item",
        method="GET",
        path="/items/{item_id}",
        path_params={"item_id": 1},
        expected_status=200,
        rationale="Check item retrieval.",
    )

    assert scenario.method == "GET"
    assert scenario.expected_status == 200


def test_absolute_url_is_rejected():
    with pytest.raises(ValidationError):
        ScenarioModel(
            name="Invalid route",
            method="GET",
            path="https://example.com",
            expected_status=200,
            rationale="An absolute URL is not an API path.",
        )


def test_path_parameters_are_substituted():
    scenario = SimpleNamespace(
        path="/items/{item_id}",
        path_params={"item_id": 42},
    )

    assert build_path(scenario) == "/items/42"


def test_json_subset_matches():
    actual = {
        "status": "ok",
        "database": "connected",
    }

    assert (
        compare_json_subset(
            actual,
            {"status": "ok"},
        )
        == []
    )


def test_json_subset_detects_wrong_value():
    errors = compare_json_subset(
        {"status": "error"},
        {"status": "ok"},
    )

    assert errors
    assert "status" in errors[0]


def test_local_target_is_accepted():
    assert validate_target("http://127.0.0.1:8000") == "http://127.0.0.1:8000"


def test_external_target_is_rejected():
    with pytest.raises(ValueError):
        validate_target("http://example.com:8000")
