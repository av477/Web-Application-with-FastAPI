# FastAPI Calculator

A web-based calculator built with FastAPI. The application serves a browser interface and provides JSON API endpoints for addition, subtraction, multiplication, and division. The project includes unit, API integration, and Playwright end-to-end tests, plus a GitHub Actions workflow for testing, container scanning, and deployment.

## Features

- Calculator web page served from a Jinja2 template.
- REST-style JSON endpoints for the four basic arithmetic operations.
- Input validation and descriptive error responses, including division-by-zero handling.
- Request and operation logging to the console and a rotating log file.
- Automated test coverage for calculation logic, API behavior, and browser workflows.
- Docker packaging and GitHub Actions CI/CD.

## Requirements

- Python 3.10 or later
- Git
- Chromium browser for local Playwright end-to-end tests
- Docker Desktop or Docker Engine (optional, for container use)

## Run locally

Clone the repository and move into the project directory:

```bash
git clone https://github.com/av477/Web-Application-with-FastAPI.git
cd Web-Application-with-FastAPI
```

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install the requirements and start the application:

```bash
python -m pip install -r requirements.txt
python main.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser. Interactive API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API

Each operation accepts a JSON request with numeric `a` and `b` fields and returns a JSON result.

| Method | Endpoint | Operation |
|---|---|---|
| `POST` | `/add` | `a + b` |
| `POST` | `/subtract` | `a - b` |
| `POST` | `/multiply` | `a * b` |
| `POST` | `/divide` | `a / b` |

Example:

```bash
curl -X POST http://127.0.0.1:8000/add \
  -H "Content-Type: application/json" \
  -d "{\"a\": 10, \"b\": 5}"
```

Successful response:

```json
{"result": 15.0}
```

Invalid input and division by zero return an error response with an `error` field.

## Run tests

Install the Playwright Chromium browser before running the browser tests:

```bash
python -m playwright install chromium
```

Run the complete test suite:

```bash
python -m pytest
```

Or run a specific test layer:

```bash
python -m pytest tests/unit
python -m pytest tests/integration
python -m pytest tests/e2e
```

Pytest is configured to report coverage for `app/` and `main.py` in the terminal and to write an HTML report to `htmlcov/index.html`.

## Logging

The application logs requests, calculation operations, and errors to the console and to a rotating file. By default, the file is `logs/app.log`; it rotates at approximately 1 MB and retains three previous log files.

| Environment variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Minimum log level, such as `DEBUG`, `INFO`, `WARNING`, or `ERROR`. |
| `LOG_FILE` | `logs/app.log` | Path to the application log file. |

For example, set `LOG_LEVEL=DEBUG` before starting the application to see debug-level operation logs.

## Docker

Build the image from the repository root:

```bash
docker build -t fastapi-calculator .
```

Run the container and publish port 8000:

```bash
docker run --rm -p 8000:8000 fastapi-calculator
```

The app is then available at [http://localhost:8000](http://localhost:8000).

## GitHub Actions

The workflow in `.github/workflows/test.yml` runs unit, integration, and end-to-end tests, builds and scans the Docker image with Trivy, and deploys the image on pushes to `main` after the preceding jobs pass.

To enable deployment, configure `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` as secrets for the GitHub `production` environment. The account must have permission to publish to the configured Docker Hub image repository. The workflow publishes `av477/601_module8:latest` and a tag containing the commit SHA.

## Project layout

```text
app/
  logging_config.py       Logging configuration
  operations/             Calculator operations
templates/
  index.html              Calculator page
tests/
  unit/                   Unit tests
  integration/            API tests
  e2e/                    Playwright browser tests
.github/workflows/
  test.yml                CI, container scanning, and deployment workflow
main.py                   FastAPI application and API routes
Dockerfile                Container build instructions
requirements.txt          Python dependencies
```
