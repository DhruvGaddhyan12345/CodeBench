import json
from pathlib import Path

from .schema import TaskSpec


def load_task(path: str | Path) -> TaskSpec:
    source = Path(path)
    with source.open(encoding="utf-8") as handle:
        return TaskSpec.from_dict(json.load(handle), source)


def discover_tasks(root: str | Path) -> list[TaskSpec]:
    return [load_task(path) for path in sorted(Path(root).glob("*/task.json"))]
