import subprocess
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, Callable


@dataclass
class ToolResult:
    tool: str
    ok: bool
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {"tool": self.tool, "ok": self.ok, "output": self.output,
                "error": self.error, "duration_ms": round(self.duration_ms, 3)}


@dataclass
class ToolContext:
    task: Any
    root: Any
    command_executor: Callable[[str, int, str], dict[str, Any]] | None = None
    trajectory: list[dict[str, Any]] = field(default_factory=list)

    def call(self, name: str, operation: Callable[[], Any], **inputs: Any) -> ToolResult:
        started = perf_counter()
        try:
            result = ToolResult(name, True, operation())
        except (OSError, ValueError, RuntimeError, TimeoutError, subprocess.TimeoutExpired) as exc:
            result = ToolResult(name, False, error=str(exc))
        result.duration_ms = (perf_counter() - started) * 1000
        self.trajectory.append({"step": len(self.trajectory) + 1, "tool": name,
                                "input": inputs, **result.to_dict()})
        return result
