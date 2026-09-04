from dataclasses import dataclass
from time import perf_counter
from typing import Any

from codebench.tools import RepositoryTools, ToolContext


@dataclass
class AgentRun:
    status: str
    strategy: str
    duration_seconds: float
    trajectory: list[dict[str, Any]]
    token_usage: None = None


class DemoAgent:
    """Deterministic local adapter for demo tasks; this is not a coding model."""

    def __init__(self, strategy: str = "react"):
        if strategy not in {"react", "plan-execute"}:
            raise ValueError("strategy must be react or plan-execute")
        self.strategy = strategy

    def run(self, task: Any, root: Any, command_executor=None) -> AgentRun:
        started = perf_counter()
        context = ToolContext(task, root, command_executor)
        tools = RepositoryTools(context)
        tools.task_inspection()
        if self.strategy == "plan-execute":
            context.trajectory.append({"step": len(context.trajectory) + 1, "tool": "plan",
                                       "input": {"task_id": task.task_id},
                                       "output": {"steps": ["localize", "read", "patch", "test"]},
                                       "ok": True, "error": None, "duration_ms": 0.0})
        for hint in task.agent_hints:
            tools.repository_search(hint["old"][:40])
            tools.file_read(hint["path"])
            tools.apply_patch(hint["path"], hint["old"], hint["new"])
        return AgentRun("completed", self.strategy, perf_counter() - started, context.trajectory)
