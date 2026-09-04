import difflib
import subprocess
from pathlib import Path
from typing import Any

from .base import ToolContext, ToolResult


class RepositoryTools:
    """The six controlled operations exposed to an agent."""

    def __init__(self, context: ToolContext):
        self.context = context

    def _path(self, relative: str) -> Path:
        candidate = (Path(self.context.root) / relative).resolve()
        root = Path(self.context.root).resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError("path escapes the repository workspace")
        return candidate

    def repository_search(self, query: str) -> ToolResult:
        def search() -> list[dict[str, Any]]:
            if not query:
                raise ValueError("query must not be empty")
            matches = []
            for path in self.context.root.rglob("*"):
                if path.is_file() and ".git" not in path.parts:
                    try:
                        lines = path.read_text(encoding="utf-8").splitlines()
                    except UnicodeDecodeError:
                        continue
                    for number, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            matches.append({"path": str(path.relative_to(self.context.root)),
                                            "line": number, "text": line})
            return matches
        return self.context.call("repository_search", search, query=query)

    def file_read(self, path: str) -> ToolResult:
        return self.context.call("file_read", lambda: self._path(path).read_text(encoding="utf-8"), path=path)

    def apply_patch(self, path: str, old: str, new: str) -> ToolResult:
        def patch() -> dict[str, str]:
            target = self._path(path)
            original = target.read_text(encoding="utf-8")
            if old not in original:
                raise ValueError("patch context was not found")
            updated = original.replace(old, new, 1)
            target.write_text(updated, encoding="utf-8")
            return {"path": path, "diff": "".join(difflib.unified_diff(
                original.splitlines(True), updated.splitlines(True), fromfile=path, tofile=path))}
        return self.context.call("apply_patch", patch, path=path, old=old, new=new)

    def shell_command(self, command: str, timeout: int = 30) -> ToolResult:
        def run() -> dict[str, Any]:
            if not command.strip():
                raise ValueError("command must not be empty")
            working_directory = self.context.task.working_directory if self.context.task else "."
            if self.context.command_executor:
                return self.context.command_executor(command, timeout, working_directory)
            cwd = self._path(working_directory)
            completed = subprocess.run(command, cwd=cwd, shell=True, text=True,
                                       capture_output=True, timeout=timeout)
            return {"stdout": completed.stdout, "stderr": completed.stderr,
                    "exit_code": completed.returncode}
        return self.context.call("shell_command", run, command=command, timeout=timeout)

    def test_execution(self, command: str | None = None) -> ToolResult:
        return self.shell_command(command or self.context.task.test_command,
                                  timeout=self.context.task.timeout_seconds)

    def task_inspection(self) -> ToolResult:
        return self.context.call("task_inspection", self.context.task.to_dict)
