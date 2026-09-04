import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from codebench.evaluation import evaluate_task
from codebench.analysis import classify_failure
from codebench.reporting import write_json
from codebench.tasks import discover_tasks

parser = argparse.ArgumentParser(); parser.add_argument("--task", required=True); parser.add_argument("--runs", type=int, default=3)
args = parser.parse_args(); root = Path(__file__).parents[1]
task = next(item for item in discover_tasks(root / "benchmarks/tasks") if item.task_id == args.task)
results = [evaluate_task(task) for _ in range(args.runs)]
statuses = [item["status"] for item in results]
data = {"task_id": task.task_id, "runs": results, "outcomes_differ": len(set(statuses)) > 1,
        "failure_category": classify_failure(statuses[-1], results[-1]["trajectory"], statuses)}
write_json(data, root / "reports/benchmark" / f"{task.task_id}_reproducibility.json")
print({"runs": len(results), "outcomes_differ": data["outcomes_differ"]})
