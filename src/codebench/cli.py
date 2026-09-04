import argparse
from pathlib import Path

from codebench.evaluation import evaluate_tasks
from codebench.reporting import write_html, write_json
from codebench.sandbox import DockerSandboxError
from codebench.tasks import discover_tasks


def main() -> None:
    parser = argparse.ArgumentParser(prog="codebench", description="Evaluate coding agents safely and reproducibly.")
    sub = parser.add_subparsers(dest="command", required=True)
    task = sub.add_parser("task"); task.add_argument("action", choices=["list"]); task.add_argument("--tasks", default="benchmarks/tasks")
    run = sub.add_parser("run"); run.add_argument("--task", required=True); run.add_argument("--strategy", default="react"); run.add_argument("--sandbox", choices=["local", "docker"], default="local")
    evaluate = sub.add_parser("evaluate"); evaluate.add_argument("--tasks", default="benchmarks/tasks"); evaluate.add_argument("--output", default="reports/evaluations"); evaluate.add_argument("--sandbox", choices=["local", "docker"], default="local")
    args = parser.parse_args()
    try:
        if args.command == "task":
            for item in discover_tasks(args.tasks): print(f"{item.task_id}: {item.description}")
        elif args.command == "run":
            item = next(task for task in discover_tasks("benchmarks/tasks") if task.task_id == args.task)
            print(evaluate_tasks([item], args.strategy, args.sandbox)["results"][0])
        else:
            data = evaluate_tasks(discover_tasks(args.tasks), sandbox=args.sandbox)
            write_json(data, Path(args.output) / "task_results.json")
            write_html(data, Path(args.output) / "evaluation_report.html")
            print(data["summary"])
    except DockerSandboxError as exc:
        parser.exit(2, f"codebench: {exc}\n")


if __name__ == "__main__":
    main()
