import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from codebench.evaluation import evaluate_tasks
from codebench.reporting import write_json
from codebench.tasks import discover_tasks

parser = argparse.ArgumentParser()
parser.add_argument("--tasks", default="benchmarks/tasks")
parser.add_argument("--strategy", default="react", choices=["react", "plan-execute"])
parser.add_argument("--sandbox", default="local", choices=["local", "docker"])
parser.add_argument("--runs", type=int, default=1)
parser.add_argument("--output", default="reports/benchmark/results.json")
args = parser.parse_args()
root = Path(__file__).parents[1]
tasks = discover_tasks(root / args.tasks)
reports = [evaluate_tasks(tasks, args.strategy, args.sandbox) for _ in range(args.runs)]
write_json({"runs": reports, "strategy": args.strategy, "sandbox": args.sandbox}, root / args.output)
print(reports[-1]["summary"])
