# tests/e2e/test_e2e_user_flows.py

"""
End-to-end tests that drive the calculator page in a real (headless) Chromium browser.

They complement tests/e2e/test_e2e.py by simulating more user interactions: decimal and
negative input, empty fields, and several calculations in a row on the same page. The
fastapi_server, browser and page fixtures come from tests/conftest.py.
"""

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"


def calculate(page: Page, a: str, b: str, operation: str) -> None:
    """Type two numbers into the form and click an operation button, like a user would."""
    page.locator("#a").fill(a)
    page.locator("#b").fill(b)
    page.get_by_role("button", name=operation).click()


@pytest.mark.e2e
def test_page_shows_calculator_form(page, fastapi_server):
    """The page loads with its title, heading, both inputs and all four buttons."""
    page.goto(BASE_URL)

    expect(page).to_have_title("Hello World & Calculator Demo")
    expect(page.get_by_role("heading", name="Calculator")).to_be_visible()
    expect(page.get_by_placeholder("First number")).to_be_visible()
    expect(page.get_by_placeholder("Second number")).to_be_visible()
    for name in ["Add", "Subtract", "Multiply", "Divide"]:
        expect(page.get_by_role("button", name=name)).to_be_enabled()
    expect(page.locator("#result")).to_have_text("")


@pytest.mark.e2e
@pytest.mark.parametrize(
    "a, b, operation, expected",
    [
        ("1.5", "2.25", "Add", "Calculation Result: 3.75"),
        ("-10", "4", "Add", "Calculation Result: -6"),
        ("2.5", "5", "Subtract", "Calculation Result: -2.5"),
        ("-2.5", "4", "Multiply", "Calculation Result: -10"),
        ("7", "2", "Divide", "Calculation Result: 3.5"),
        ("-9", "3", "Divide", "Calculation Result: -3"),
    ],
    ids=["add_decimals", "add_negative", "subtract_to_negative",
         "multiply_negative_decimal", "divide_non_integer", "divide_negative"],
)
def test_decimal_and_negative_input(page, fastapi_server, a, b, operation, expected):
    """Users can enter decimals and negative numbers and see the correct result."""
    page.goto(BASE_URL)

    calculate(page, a, b, operation)

    expect(page.locator("#result")).to_have_text(expected)


@pytest.mark.e2e
def test_empty_second_number_shows_error(page, fastapi_server):
    """Clicking an operation with the second field empty shows an error for b."""
    page.goto(BASE_URL)

    calculate(page, "5", "", "Add")

    result = page.locator("#result")
    expect(result).to_contain_text("Error:")
    expect(result).to_contain_text("b:")


@pytest.mark.e2e
def test_both_fields_empty_shows_error_for_both(page, fastapi_server):
    """With both fields empty, the error mentions both a and b."""
    page.goto(BASE_URL)

    page.get_by_role("button", name="Multiply").click()

    result = page.locator("#result")
    expect(result).to_contain_text("Error:")
    expect(result).to_contain_text("a:")
    expect(result).to_contain_text("b:")


@pytest.mark.e2e
def test_successive_calculations_update_the_result(page, fastapi_server):
    """Each new calculation replaces the previous result on the same page."""
    page.goto(BASE_URL)
    result = page.locator("#result")

    calculate(page, "6", "3", "Add")
    expect(result).to_have_text("Calculation Result: 9")

    page.get_by_role("button", name="Multiply").click()
    expect(result).to_have_text("Calculation Result: 18")

    calculate(page, "8", "4", "Divide")
    expect(result).to_have_text("Calculation Result: 2")


@pytest.mark.e2e
def test_recovers_after_divide_by_zero(page, fastapi_server):
    """After a division-by-zero error, fixing the input gives a normal result again."""
    page.goto(BASE_URL)
    result = page.locator("#result")

    calculate(page, "10", "0", "Divide")
    expect(result).to_have_text("Error: Cannot divide by zero!")

    page.locator("#b").fill("4")
    page.get_by_role("button", name="Divide").click()
    expect(result).to_have_text("Calculation Result: 2.5")
