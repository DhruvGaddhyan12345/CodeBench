from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    repository: str
    description: str
    test_command: str
    timeout_seconds: int = 120
    base_commit: str | None = None
    working_directory: str = "."
    expected_behavior: str = ""
    agent_hints: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: Path | None = None) -> "TaskSpec":
        required = ("task_id", "repository", "description", "test_command")
        missing = [key for key in required if not data.get(key)]
        if missing:
            location = f" in {source}" if source else ""
            raise ValueError(f"Missing required task fields{location}: {', '.join(missing)}")
        timeout = int(data.get("timeout_seconds", 120))
        if timeout <= 0:
            raise ValueError("timeout_seconds must be positive")
        return cls(task_id=str(data["task_id"]), repository=str(data["repository"]),
                   description=str(data["description"]), test_command=str(data["test_command"]),
                   timeout_seconds=timeout, base_commit=data.get("base_commit"),
                   working_directory=str(data.get("working_directory", ".")),
                   expected_behavior=str(data.get("expected_behavior", "")),
                   agent_hints=list(data.get("agent_hints", [])))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
