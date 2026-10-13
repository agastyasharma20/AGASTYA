<div align="center">

# AGASTYA

### AI-assisted API testing for Python developers

Turn an OpenAPI JSON specification into a validated API test plan, execute approved scenarios against a local application, and save a structured JSON report.

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange)](https://github.com/agastyasharma20/AGASTYA)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[Getting Started](#-getting-started) · [Quickstart](#-quickstart) · [CLI Reference](#-cli-reference) · [Security](#-security-and-safe-usage) · [Roadmap](#-roadmap)

</div>

---

> **Project status: Alpha · v0.1.0**
>
> AGASTYA is an early-stage developer tool. Review generated test plans before executing them, and use only disposable local test applications. It is not a substitute for a comprehensive testing or security program.

## ✨ Why AGASTYA?

API testing often starts with manually writing requests and assertions. AGASTYA experiments with an AI-assisted workflow that helps developers move from an API contract to a reviewable set of test scenarios.

AGASTYA uses **Groq** to propose scenarios from an OpenAPI JSON specification, validates the generated plan locally against supported parts of that specification, and can execute the saved plan against a local HTTP API.

### What it does today

- **AI-assisted test planning** — generate a requested number of scenarios around a testing goal.
- **OpenAPI-aware validation** — check documented routes, HTTP methods, path parameters, query parameters, request-body usage, response status codes, and supported JSON response fields.
- **Structured plans** — validate test-plan data using Pydantic models.
- **HTTP execution** — issue supported HTTP requests through HTTPX.
- **Response assertions** — check expected HTTP status codes and optional JSON-field subsets.
- **Machine-readable reports** — write scenario-level outcomes and diagnostic details to JSON.
- **Local-target restriction** — the initial executor accepts local HTTP targets only.
- **Mutation opt-in** — require an explicit `--allow-mutations` flag when a plan includes `POST`, `PUT`, `PATCH`, or `DELETE` requests.

## 🧭 How it works

```text
OpenAPI JSON specification + testing goal
                  │
                  ▼
        Groq proposes test scenarios
                  │
                  ▼
     Pydantic and OpenAPI-aware checks
                  │
                  ▼
          Saved test plan (.json)
                  │
           Human review
                  │
                  ▼
     Execute against a local HTTP API
                  │
                  ▼
      JSON report with pass/fail details
```

Planning and execution are separate steps. **Generating a plan does not execute any tests.** Review the generated JSON before running it.

## 🧰 Technology stack

| Component | Role |
|---|---|
| Python 3.11+ | Runtime |
| Groq | LLM-backed test-plan generation |
| Pydantic | Structured model validation |
| HTTPX | HTTP request execution |
| `python-dotenv` | Local environment configuration |
| pytest | Automated tests |
| Ruff | Linting |
| FastAPI + Uvicorn | Optional demo API |

## 🚀 Getting started

### Prerequisites

- Python **3.11 or newer**
- Git
- A [Groq API key](https://console.groq.com/keys)
- An OpenAPI specification in JSON format for the API you want to test

### 1. Clone the repository

```bash
git clone https://github.com/agastyasharma20/AGASTYA.git
cd AGASTYA
```

### 2. Create and activate a virtual environment

**Windows — Command Prompt**

```cmd
py -m venv .venv
.venv\Scripts\activate
```

**Windows — PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install AGASTYA and development/demo extras

From the repository root, run:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[groq,dev,demo]"
```

This installs AGASTYA in editable mode, the Groq integration, development tools, and dependencies for the included FastAPI demo. The project is currently distributed as source; use the repository installation above unless a published package release is available.

### 4. Configure Groq

Copy the example environment file:

**Windows — Command Prompt**

```cmd
copy .env.example .env
notepad .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Set your key in `.env`:

```dotenv
AGASTYA_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Replace the example value with your real API key. Keep `.env` private and never commit it. The project currently implements the Groq provider; other provider variables in an example environment file are not a guarantee of provider support.

### 5. Verify the installation and LLM connection

```bash
agastya --help
agastya check-llm
```

A successful connection check should return:

```text
AGASTYA_CONNECTION_OK
```

If the shell cannot find `agastya`, verify that the virtual environment is activated and that installation completed successfully.

## ⚡ Quickstart

This walkthrough uses the sample FastAPI application included in the repository.

### Terminal 1: Start the demo API

With the virtual environment active and the project dependencies installed, run this from the repository root:

```bash
python -m uvicorn examples.demo_api:app --host 127.0.0.1 --port 8000 --reload
```

Keep this terminal running. The demo API provides `/health`, `/items`, and `/items/{item_id}` routes.

### Terminal 2: Generate a read-only test plan

Open a second terminal, navigate to the repository, and activate `.venv` again. Then run:

```bash
agastya plan \
  --spec examples/openapi.json \
  --goal "Test read-only GET workflows, including a missing item ID" \
  --count 3 \
  --output agastya-plan.json
```

The command requests three scenarios, validates the returned plan against supported parts of the supplied specification, and saves it to `agastya-plan.json`.

**Review `agastya-plan.json` before proceeding.** Confirm the routes, parameters, expected status codes, and scenario rationale are appropriate for the demo API.

### Execute the reviewed plan

```bash
agastya run \
  --plan agastya-plan.json \
  --base-url http://127.0.0.1:8000 \
  --output agastya-run.json
```

AGASTYA prints a pass/fail summary and writes detailed results to `agastya-run.json`.

> **Windows Command Prompt note:** The multiline commands above use Bash-style `\` line continuation. In CMD, put each command on one line, for example:
>
> ```cmd
> agastya plan --spec examples/openapi.json --goal "Test read-only GET workflows, including a missing item ID" --count 3 --output agastya-plan.json
> ```

## 🖥️ CLI reference

### Check the Groq connection

```bash
agastya check-llm
```

### Generate a plan

```bash
agastya plan --spec examples/openapi.json --goal "Find functional and edge-case scenarios" --count 5 --output agastya-plan.json
```

| Option | Required | Description |
|---|---:|---|
| `--spec` | Yes | Path to an OpenAPI JSON file |
| `--goal` | No | Testing objective; defaults to a functional/edge-case goal |
| `--count` | No | Number of scenarios to request; supported range is 1–10, default 5 |
| `--output` | No | Output path; default `agastya-plan.json` |

### Run a saved plan

```bash
agastya run --plan agastya-plan.json --base-url http://127.0.0.1:8000 --output agastya-run.json
```

| Option | Required | Description |
|---|---:|---|
| `--plan` | Yes | Path to a previously generated plan JSON file |
| `--base-url` | Yes | Local HTTP origin, such as `http://127.0.0.1:8000` |
| `--output` | No | Report path; default `agastya-run.json` |
| `--allow-mutations` | No | Explicitly permits `POST`, `PUT`, `PATCH`, and `DELETE` requests |

### Allow state-changing requests only when appropriate

If a plan contains a mutating method, AGASTYA refuses to execute it unless you explicitly opt in. After reviewing the plan, and only against a **disposable local test environment**, you can run:

```bash
agastya run --plan agastya-plan.json --base-url http://127.0.0.1:8000 --allow-mutations --output agastya-run.json
```

The flag is an opt-in, not a safety guarantee. State-changing requests can still modify or delete data in the target application.

## 📄 Understanding the JSON report

The execution report contains an application name, normalized base URL, total scenario count, pass/fail totals, and a result object for each scenario. Per-scenario details include:

- Scenario name, HTTP method, and route
- Expected and actual HTTP status codes
- Whether the scenario passed
- Whether optional body assertions passed
- JSON assertion errors or request/validation errors
- A response preview limited to the first 500 characters

A scenario passes when its actual HTTP status matches the expected status and any configured JSON subset assertions pass. When `expected_json` is configured, AGASTYA checks that the specified fields exist and match the expected values; extra fields in the response are allowed.

A nonzero exit code is returned when the execution report contains failed scenarios, making the command easier to integrate into scripts.

## 🔐 Security and safe usage

AGASTYA's current safeguards reduce some risks, but do not make arbitrary test plans risk-free.

- **Local targets only:** the executor accepts HTTP requests only to `localhost`, `127.0.0.1`, or `::1`, with an explicit port.
- **Mutations require opt-in:** plans containing `POST`, `PUT`, `PATCH`, or `DELETE` require `--allow-mutations`.
- **Review before execution:** generated test scenarios are proposals. Inspect the plan before running it.
- **Use disposable data:** avoid running mutating scenarios against applications or databases containing valuable data.
- **Protect credentials:** keep API keys in `.env`; do not commit secrets, tokens, private data, or production credentials.
- **Sanitize specifications:** the relevant OpenAPI content is sent to Groq for planning. Do not submit confidential schema details or sensitive examples unless you are authorized to share them with that service.
- **Treat reports as potentially sensitive:** response previews may include data returned by your test API. Review reports before sharing them.

AGASTYA is **not** a vulnerability scanner, penetration-testing framework, or guarantee of application correctness. Passing tests means the configured assertions passed; it does not prove that the application is bug-free or secure.

## 🧪 Development

Install the project with its development and demo extras:

```bash
python -m pip install -e ".[groq,dev,demo]"
```

Run tests:

```bash
pytest -q
```

Run Ruff:

```bash
ruff check src tests
```

Compile the package source:

```bash
python -m compileall -q src/agastya_ai
```

Build and validate distribution archives (optional):

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

## 🗂️ Project structure

```text
AGASTYA/
├── examples/
│   ├── demo_api.py       # Sample FastAPI application
│   └── openapi.json      # OpenAPI JSON specification for the demo
├── src/
│   └── agastya_ai/
│       ├── cli.py        # Command-line interface
│       ├── executor.py   # Local HTTP execution and assertions
│       ├── models.py     # Pydantic test-plan models
│       ├── planner.py    # Groq planning and specification validation
│       └── providers.py  # Groq integration
├── tests/                # Automated tests
├── .env.example          # Environment configuration template
├── pyproject.toml        # Packaging and tool configuration
├── LICENSE
└── README.md
```

## 🛣️ Roadmap

The following are **potential future directions**, not current features:

- Broader OpenAPI coverage and validation
- Additional ways to define and organize test scenarios
- More extensive assertion types and report formats
- Regression-test history and reusable bug-reproduction cases
- Business-rule testing and controlled synthetic test data
- Optional concurrency or load-testing capabilities
- Additional LLM providers

Roadmap items may change based on feedback, feasibility, and project priorities.

## 🤝 Contributing

Contributions are welcome, especially focused bug reports, minimal reproduction cases, documentation improvements, and additional automated tests.

1. Fork the repository and create a focused branch.
2. Make your change and add or update tests where appropriate.
3. Run `pytest -q` and `ruff check src tests`.
4. Open a pull request describing the problem, implementation, and validation performed.

Please do not include API keys, confidential OpenAPI specifications, real customer data, or sensitive response payloads in issues, tests, or pull requests.

## 📜 License

AGASTYA is released under the [MIT License](LICENSE).

---

<div align="center">

Built for developers who want a more deliberate path from API contract to test execution.

**[Explore the repository](https://github.com/agastyasharma20/AGASTYA) · [Report an issue](https://github.com/agastyasharma20/AGASTYA/issues)**

</div>
