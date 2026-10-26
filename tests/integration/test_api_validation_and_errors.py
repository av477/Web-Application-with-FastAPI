# tests/integration/test_api_validation_and_errors.py

"""
Integration tests for the FastAPI endpoints in main.py.

These complement tests/integration/test_fastapi_calculator.py by covering every endpoint
with decimal and negative inputs, invalid request bodies, unexpected internal errors,
and the log records written for each of these cases.
"""

import logging

import pytest
from fastapi.testclient import TestClient

import main
from main import app

ENDPOINTS = ["/add", "/subtract", "/multiply", "/divide"]


@pytest.fixture
def client():
    """TestClient that calls the app in-process, without starting a server."""
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------
# Successful calculations
# ---------------------------------------------

@pytest.mark.parametrize(
    "endpoint, a, b, expected",
    [
        ("/add", 1.5, 2.25, 3.75),
        ("/add", -10, 4, -6),
        ("/subtract", 2.5, 5, -2.5),
        ("/subtract", -3, -3, 0),
        ("/multiply", -2.5, 4, -10),
        ("/multiply", 0, 123.456, 0),
        ("/divide", 7, 2, 3.5),
        ("/divide", -9, 3, -3),
    ],
)
def test_endpoints_with_decimal_and_negative_numbers(client, endpoint, a, b, expected):
    """Every endpoint returns the correct result for decimals and negative numbers."""
    response = client.post(endpoint, json={"a": a, "b": b})

    assert response.status_code == 200
    assert response.json() == {"result": pytest.approx(expected)}


def test_numeric_strings_are_accepted(client):
    """Pydantic converts numeric strings such as "4" into numbers."""
    response = client.post("/multiply", json={"a": "4", "b": "2.5"})

    assert response.status_code == 200
    assert response.json()["result"] == 10


# ---------------------------------------------
# Invalid requests (handled by the RequestValidationError handler)
# ---------------------------------------------

@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_missing_field_returns_400(client, endpoint):
    """Leaving out a required number gives a 400 that names the missing field."""
    response = client.post(endpoint, json={"a": 1})

    assert response.status_code == 400
    assert "b: Field required" in response.json()["error"]


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_non_numeric_value_returns_400(client, endpoint):
    """A value that is not a number gives a 400 that names the bad field."""
    response = client.post(endpoint, json={"a": 1, "b": "abc"})

    assert response.status_code == 400
    assert response.json()["error"].startswith("b:")


@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_null_values_report_both_fields(client, endpoint):
    """When both numbers are invalid, the error message lists both fields."""
    response = client.post(endpoint, json={"a": None, "b": None})

    assert response.status_code == 400
    error = response.json()["error"]
    assert "a:" in error and "b:" in error


def test_empty_body_returns_400(client):
    """A request with no JSON body is rejected with a 400 error response."""
    response = client.post("/add")

    assert response.status_code == 400
    assert "error" in response.json()


def test_get_on_operation_endpoint_is_not_allowed(client):
    """The operation endpoints only accept POST."""
    response = client.get("/add")

    assert response.status_code == 405


# ---------------------------------------------
# Unexpected errors inside the operations
# ---------------------------------------------

@pytest.mark.parametrize(
    "endpoint, function_name",
    [("/add", "add"), ("/subtract", "subtract"), ("/multiply", "multiply")],
)
def test_unexpected_error_returns_400_with_message(client, monkeypatch, endpoint, function_name):
    """If add/subtract/multiply raise, the API returns 400 with the error text."""
    def broken(a, b):
        raise RuntimeError("something went wrong")

    monkeypatch.setattr(main, function_name, broken)

    response = client.post(endpoint, json={"a": 1, "b": 2})

    assert response.status_code == 400
    assert response.json() == {"error": "something went wrong"}


def test_unexpected_divide_error_returns_500(client, monkeypatch):
    """A non-ValueError inside divide is hidden behind a generic 500 response."""
    def broken(a, b):
        raise RuntimeError("internal details")

    monkeypatch.setattr(main, "divide", broken)

    response = client.post("/divide", json={"a": 1, "b": 2})

    assert response.status_code == 500
    assert response.json() == {"error": "Internal Server Error"}


# ---------------------------------------------
# Logging
# ---------------------------------------------

def test_divide_by_zero_is_logged(client, caplog):
    """A division by zero is logged by both the operation and the API layer."""
    caplog.set_level(logging.INFO)

    client.post("/divide", json={"a": 1, "b": 0})

    messages = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
    assert any("divide(1.0, 0.0) failed: division by zero" in m for m in messages)
    assert any("Divide Operation Error: Cannot divide by zero!" in m for m in messages)


def test_validation_error_is_logged(client, caplog):
    """Invalid input is logged at ERROR level with the endpoint path."""
    caplog.set_level(logging.INFO, logger="main")

    client.post("/subtract", json={"a": "x", "b": 1})

    assert "ValidationError on /subtract" in caplog.text


def test_every_request_is_logged_with_status(client, caplog):
    """The request middleware logs method, path and status code for each request."""
    caplog.set_level(logging.INFO, logger="main")

    client.post("/multiply", json={"a": 2, "b": 3})
    client.post("/divide", json={"a": 1, "b": 0})

    assert "POST /multiply completed with status 200" in caplog.text
    assert "POST /divide completed with status 400" in caplog.text


def test_root_page_visit_is_logged(client, caplog):
    """Serving the calculator page writes an INFO record."""
    caplog.set_level(logging.INFO, logger="main")

    response = client.get("/")

    assert response.status_code == 200
    assert "Serving calculator page" in caplog.text
