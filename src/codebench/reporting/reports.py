import html
import json
from pathlib import Path


def write_json(data: dict, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return destination


def write_html(data: dict, path: str | Path) -> Path:
    summary = data.get("summary", {})
    rows = "".join(f"<tr><td>{html.escape(item['task_id'])}</td><td>{item['status']}</td><td>{item['tool_calls']}</td><td>{item['failure_category'] or ''}</td></tr>" for item in data.get("results", []))
    body = f"<h1>CodeBench Evaluation</h1><p>Resolved: {summary.get('resolved', 0)}/{summary.get('tasks', 0)} ({summary.get('resolution_rate', 0):.0%})</p><table><tr><th>Task</th><th>Status</th><th>Tool calls</th><th>Failure</th></tr>{rows}</table>"
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("<!doctype html><meta charset='utf-8'><style>body{font:16px sans-serif;max-width:900px;margin:40px auto}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:8px}</style>" + body, encoding="utf-8")
    return destination
