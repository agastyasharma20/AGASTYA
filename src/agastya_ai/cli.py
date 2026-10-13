import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from agastya_ai.executor import (
    MUTATING_METHODS,
    execute_plan,
)
from agastya_ai.models import TestPlan
from agastya_ai.planner import generate_test_plan
from agastya_ai.providers import create_provider


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="agastya",
        description="AGASTYA — AI-assisted software testing",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )

    commands.add_parser(
        "check-llm",
        help="Check the Groq connection",
    )

    plan_cmd = commands.add_parser(
        "plan",
        help="Generate an API test plan",
    )
    plan_cmd.add_argument("--spec", required=True)
    plan_cmd.add_argument(
        "--goal",
        default="Find functional and edge-case scenarios.",
    )
    plan_cmd.add_argument("--count", type=int, default=5)
    plan_cmd.add_argument(
        "--output",
        default="agastya-plan.json",
    )

    run_cmd = commands.add_parser(
        "run",
        help="Execute a saved plan against a local API",
    )
    run_cmd.add_argument("--plan", required=True)
    run_cmd.add_argument("--base-url", required=True)
    run_cmd.add_argument(
        "--output",
        default="agastya-run.json",
    )
    run_cmd.add_argument(
        "--allow-mutations",
        action="store_true",
        help="Permit POST, PUT, PATCH, and DELETE requests",
    )

    args = parser.parse_args()

    try:
        if args.command == "run":
            plan_file = Path(args.plan)
            output_file = Path(args.output)

            plan = TestPlan.model_validate_json(plan_file.read_text(encoding="utf-8"))

            needs_mutation_permission = any(
                item.method in MUTATING_METHODS for item in plan.scenarios
            )

            if needs_mutation_permission and not args.allow_mutations:
                raise ValueError(
                    "This plan contains state-changing requests. "
                    "Review the plan and explicitly add "
                    "--allow-mutations when using a disposable "
                    "local test application."
                )

            report = execute_plan(
                plan,
                args.base_url,
            )

            output_file.write_text(
                json.dumps(report, indent=2),
                encoding="utf-8",
            )

            print("\nAGASTYA — Execution Report")
            print(f"Application: {report['application']}")
            print(f"Target: {report['base_url']}")
            print(f"Total scenarios: {report['total']}")
            print(f"Passed: {report['passed']}")
            print(f"Failed: {report['failed']}")

            for result in report["results"]:
                status = "PASS" if result["passed"] else "FAIL"
                actual = result["actual_status"]
                actual_text = str(actual) if actual is not None else "NO RESPONSE"

                print(
                    f"[{status}] {result['method']} "
                    f"{result['path']} "
                    f"(expected {result['expected_status']}, "
                    f"actual {actual_text})"
                )

                if result["error"]:
                    print(f"       {result['error']}")

            print(f"\nReport saved to: {output_file.resolve()}")

            # A failing test run returns a non-zero exit code.
            if report["failed"] > 0:
                raise SystemExit(1)

            return

        provider = create_provider()

        if args.command == "check-llm":
            print(
                provider.generate_text(
                    "You are a diagnostics assistant.",
                    "Reply exactly with AGASTYA_CONNECTION_OK",
                )
            )
            return

        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))

        plan = generate_test_plan(
            provider=provider,
            openapi_spec=spec,
            goal=args.goal,
            count=args.count,
        )

        Path(args.output).write_text(
            plan.model_dump_json(indent=2),
            encoding="utf-8",
        )

        print("\nAGASTYA — Test Plan Generated")
        print(f"Application: {plan.application}")
        print(f"Scenarios: {len(plan.scenarios)}")
        print(f"Saved to: {Path(args.output).resolve()}")
        print("Note: These scenarios have not been executed.")

    except SystemExit:
        raise
    except Exception as exc:
        raise SystemExit(f"AGASTYA error: {exc}") from exc


if __name__ == "__main__":
    main()
