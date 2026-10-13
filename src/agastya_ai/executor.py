"""AGASTYA API test execution and response assertions."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote, urlsplit

import httpx

from agastya_ai.models import TestPlan, TestScenario

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def validate_target(base_url: str) -> str:
    """Allow HTTP requests only to explicitly local hosts."""
    if not isinstance(base_url, str):
        raise TypeError("base_url must be a string.")

    if not base_url or base_url != base_url.strip():
        raise ValueError("Provide a valid base URL.")

    try:
        parsed = urlsplit(base_url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"Invalid target URL: {exc}") from exc

    if parsed.scheme.lower() != "http":
        raise ValueError("Only local HTTP targets are supported.")

    if hostname not in LOCAL_HOSTS:
        raise ValueError("AGASTYA v0.1 only permits localhost, 127.0.0.1, or ::1.")

    if parsed.username or parsed.password:
        raise ValueError("Credentials are not allowed in the target URL.")

    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Provide only the base origin, e.g. http://127.0.0.1:8000.")

    if port is None or not 1 <= port <= 65535:
        raise ValueError("Provide a valid port.")

    return base_url.rstrip("/")


def build_path(scenario: TestScenario) -> str:
    """Replace route placeholders with URL-encoded parameter values."""
    path = scenario.path

    placeholders = set(re.findall(r"{([^{}]+)}", path))
    supplied = set(scenario.path_params)

    if placeholders != supplied:
        raise ValueError(
            f"Required path parameters: {sorted(placeholders)}; "
            f"received: {sorted(supplied)}."
        )

    for name in placeholders:
        value = quote(str(scenario.path_params[name]), safe="")
        path = path.replace("{" + name + "}", value)

    if "{" in path or "}" in path:
        raise ValueError("The path contains an unresolved parameter.")

    if not path.startswith("/") or path.startswith("//"):
        raise ValueError("Scenario path must be a relative API path.")

    return path


def compare_json_subset(
    actual: Any,
    expected: dict[str, Any],
    prefix: str = "$",
) -> list[str]:
    """
    Check that expected JSON fields exist and have expected values.

    Extra response fields are allowed. Nested JSON objects are
    compared recursively.
    """
    if not isinstance(actual, dict):
        message = f"{prefix}: expected a JSON object, received {type(actual).__name__}."
        return [message]

    errors: list[str] = []

    for key, expected_value in expected.items():
        location = f"{prefix}.{key}"

        if key not in actual:
            errors.append(f"{location}: field is missing.")
            continue

        actual_value = actual[key]

        if isinstance(expected_value, dict):
            errors.extend(
                compare_json_subset(
                    actual_value,
                    expected_value,
                    location,
                )
            )
        elif actual_value != expected_value:
            errors.append(
                f"{location}: expected {expected_value!r}, received {actual_value!r}."
            )

    return errors


def execute_plan(
    plan: TestPlan,
    base_url: str,
    *,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """
    Execute a saved test plan against a local API.

    Each test passes only if its HTTP status matches the expectation
    and any configured JSON response assertions also pass.
    """
    base_url = validate_target(base_url)

    if not 0 < timeout <= 60:
        raise ValueError("Timeout must be greater than 0 and at most 60.")

    results: list[dict[str, Any]] = []

    with httpx.Client(
        base_url=base_url,
        timeout=timeout,
        follow_redirects=False,
        trust_env=False,
        headers={"User-Agent": "AGASTYA/0.1"},
    ) as client:
        for scenario in plan.scenarios:
            result: dict[str, Any] = {
                "name": scenario.name,
                "method": scenario.method,
                "path": scenario.path,
                "expected_status": scenario.expected_status,
                "actual_status": None,
                "passed": False,
                "body_assertions_passed": (
                    None if scenario.expected_json is None else False
                ),
                "body_errors": [],
                "error": None,
                "response_preview": None,
            }

            try:
                path = build_path(scenario)

                response = client.request(
                    method=scenario.method,
                    url=path,
                    params=scenario.query_params or None,
                    json=scenario.json_body,
                )

                result["actual_status"] = response.status_code

                status_matches = response.status_code == scenario.expected_status

                body_errors: list[str] = []

                if scenario.expected_json is not None:
                    try:
                        actual_json = response.json()
                        body_errors = compare_json_subset(
                            actual_json,
                            scenario.expected_json,
                        )
                    except ValueError:
                        body_errors = ["Response body is not valid JSON."]

                    result["body_assertions_passed"] = not body_errors

                result["body_errors"] = body_errors
                result["passed"] = status_matches and not body_errors

                if not status_matches:
                    result["error"] = (
                        f"Expected HTTP {scenario.expected_status}, "
                        f"received HTTP {response.status_code}."
                    )
                elif body_errors:
                    result["error"] = "; ".join(body_errors)

                result["response_preview"] = response.text[:500]

            except (ValueError, TypeError, httpx.HTTPError) as exc:
                result["error"] = f"{type(exc).__name__}: {exc}"

            results.append(result)

    passed = sum(1 for result in results if result["passed"])

    return {
        "application": plan.application,
        "base_url": base_url,
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }
