"""Adapter for SWE-bench-style records without downloading the dataset."""

from typing import Any

from .schema import TaskSpec


def from_swebench_record(record: dict[str, Any], repository_root: str) -> TaskSpec:
    """Map a SWE-bench record into CodeBench's local task contract.

    The caller supplies a checked-out repository path. Dataset download and
    patch application remain intentionally outside this adapter.
    """
    task_id = record.get("instance_id") or record.get("task_id")
    if not task_id or not record.get("problem_statement"):
        raise ValueError("SWE-bench record requires instance_id and problem_statement")
    return TaskSpec(task_id=str(task_id), repository=repository_root,
                    description=str(record["problem_statement"]),
                    test_command=str(record.get("test_command", "python -m pytest -q")),
                    base_commit=record.get("base_commit"),
                    timeout_seconds=int(record.get("timeout_seconds", 120)),
                    expected_behavior="Resolve the supplied SWE-bench task")