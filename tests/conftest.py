# tests/e2e/conftest.py

import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope='session')
def fastapi_server():
    project_root = Path(__file__).resolve().parents[1]
    fastapi_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=project_root,
    )
    server_url = f"{BASE_URL}/"
    timeout = 30
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            if fastapi_process.poll() is not None:
                raise RuntimeError(
                    f"FastAPI server exited with status {fastapi_process.returncode}."
                )
            try:
                response = requests.get(server_url, timeout=1)
                if response.status_code == 200:
                    break
            except requests.ConnectionError:
                time.sleep(0.25)
        else:
            raise RuntimeError("FastAPI server failed to start within 30 seconds.")

        yield
    finally:
        if fastapi_process.poll() is None:
            fastapi_process.terminate()
            try:
                fastapi_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                fastapi_process.kill()
                fastapi_process.wait()

@pytest.fixture(scope="session")
def playwright_instance_fixture():
    """
    Fixture to manage Playwright's lifecycle.
    """
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance_fixture):
    browser = playwright_instance_fixture.chromium.launch(headless=True)
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def page(browser):
    page = browser.new_page()
    yield page
    page.close()
