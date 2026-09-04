import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from codebench.evaluation import evaluate_tasks
from codebench.reporting import write_html, write_json
from codebench.tasks import discover_tasks

parser = argparse.ArgumentParser()
parser.add_argument("--sandbox", choices=["local", "docker"], default="local")
args = parser.parse_args()
root = Path(__file__).parents[1]
data = evaluate_tasks(discover_tasks(root / "benchmarks" / "tasks"), sandbox=args.sandbox)
write_json(data, root / "reports/evaluations/task_results.json")
write_html(data, root / "reports/evaluations/evaluation_report.html")
print(data["summary"])
