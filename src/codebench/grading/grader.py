from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

from codebench.tools import RepositoryTools, ToolContext


@dataclass
class GradeResult:
    status: str
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def grade(task: Any, root: Any, command_executor=None) -> GradeResult:
    started = perf_counter()
    result = RepositoryTools(ToolContext(task, root, command_executor)).test_execution()
    if not result.ok:
        status = "TIMEOUT" if "timed out" in (result.error or "").lower() else "EXECUTION_ERROR"
        return GradeResult(status, None, "", result.error or "", perf_counter() - started)
    output = result.output
    if output.get("timed_out"):
        return GradeResult("TIMEOUT", None, output["stdout"], output["stderr"], perf_counter() - started)
    status = "PASS" if output["exit_code"] == 0 else "FAIL"
    return GradeResult(status, output["exit_code"], output["stdout"], output["stderr"],
                       perf_counter() - started)
