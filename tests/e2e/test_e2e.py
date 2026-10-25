# tests/e2e/test_e2e.py

import pytest  # Import the pytest framework for writing and running tests

from playwright.sync_api import expect

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.e2e
def test_hello_world(page, fastapi_server):
    page.goto(BASE_URL)
    expect(page.get_by_role("heading", name="Hello World")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ("Add", "Calculation Result: 15"),
        ("Subtract", "Calculation Result: 5"),
        ("Multiply", "Calculation Result: 50"),
        ("Divide", "Calculation Result: 2"),
    ],
)
def test_calculator_operations(page, fastapi_server, operation, expected):
    page.goto(BASE_URL)
    page.locator("#a").fill("10")
    page.locator("#b").fill("5")
    page.get_by_role("button", name=operation).click()
    expect(page.locator("#result")).to_have_text(expected)


@pytest.mark.e2e
def test_calculator_divide_by_zero(page, fastapi_server):
    page.goto(BASE_URL)
    page.locator("#a").fill("10")
    page.locator("#b").fill("0")
    page.get_by_role("button", name="Divide").click()
    expect(page.locator("#result")).to_have_text("Error: Cannot divide by zero!")
