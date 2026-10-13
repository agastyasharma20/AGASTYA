\# AGASTYA



\*\*AI-assisted API testing for Python developers.\*\*



AGASTYA uses Groq to generate API test scenarios from OpenAPI specifications, validates the generated plans, executes approved tests against local applications, and produces JSON reports.



\## Features



\- AI-assisted API test planning using Groq.

\- Structured test scenarios validated with Pydantic.

\- OpenAPI route and documented-response-code validation.

\- HTTP test execution using HTTPX.

\- Optional expected JSON response assertions.

\- Detailed JSON execution reports.

\- Local-target restrictions in the initial execution engine.



\## Requirements



\- Python 3.11 or newer.

\- A Groq API key.

\- An OpenAPI JSON specification for the API you want to test.



\## Installation



```bash

pip install "agastya-ai\[groq]"

```



\## Configuration



Create a `.env` file in your project directory:



```dotenv

GROQ\_API\_KEY=your\_groq\_api\_key

GROQ\_MODEL=openai/gpt-oss-20b

AGASTYA\_PROVIDER=groq

```



Obtain an API key from \[Groq Console](https://console.groq.com/keys).



Never commit `.env` or share your API key publicly.



\## Generate a test plan



```bash

agastya plan --spec openapi.json --goal "Test the API's main workflows" --count 5 --output agastya-plan.json

```



\## Execute the plan



Start your local API, then run:



```bash

agastya run --plan agastya-plan.json --base-url http://127.0.0.1:8000 --output agastya-run.json

```



For plans containing POST, PUT, PATCH or DELETE operations, review the plan and use `--allow-mutations` only against a disposable local test environment:



```bash

agastya run --plan agastya-plan.json --base-url http://127.0.0.1:8000 --allow-mutations --output agastya-run.json

```



\## How it works



1\. Read the API specification.

2\. Ask Groq to propose test scenarios.

3\. Validate supported aspects of the plan locally.

4\. Execute the scenarios against an authorized local API.

5\. Save the execution results as JSON.



\## Current limitations



AGASTYA is an early-stage project. It does not yet provide comprehensive OpenAPI validation, automatic discovery of all business-logic defects, large-scale virtual-user simulation, or guaranteed detection of security vulnerabilities.



A passing test means that the configured assertions passed; it does not prove that an application is bug-free.



The initial executor is restricted to local HTTP targets.



\## Development



Install development dependencies:



```bash

pip install -e ".\[groq,dev,demo]"

```



Run automated tests:



```bash

pytest -q

```



Check code quality:



```bash

ruff check .

```



\## Contributing



Bug reports, reproducible examples and improvements to test coverage are welcome.



\## License

See the `LICENSE` file.