import json
from pathlib import Path

import pytest

from codebench.analysis import classify_failure
from codebench.evaluation import evaluate_tasks
from codebench.reporting import write_html, write_json
from codebench.sandbox import DockerSandboxConfig, LocalSandbox
from codebench.tasks import discover_tasks
from codebench.tools import RepositoryTools, ToolContext


ROOT = Path(__file__).parents[1]


def test_task_discovery_and_validation():
    tasks = discover_tasks(ROOT / "benchmarks/tasks")
    assert len(tasks) == 5
    with pytest.raises(ValueError):
        tasks[0].from_dict({"task_id": "missing"})


def test_tools_enforce_workspace_boundary(tmp_path):
    (tmp_path / "source.txt").write_text("needle", encoding="utf-8")
    tools = RepositoryTools(ToolContext(None, tmp_path))
    assert tools.repository_search("needle").output[0]["path"] == "source.txt"
    assert not tools.file_read("../outside").ok


def test_tools_use_injected_command_executor(tmp_path):
    task = type("Task", (), {"working_directory": "."})()
    context = ToolContext(task, tmp_path, lambda command, timeout, working_directory: {
        "stdout": command, "stderr": "", "exit_code": 0, "timed_out": False})
    result = RepositoryTools(context).shell_command("echo isolated")
    assert result.ok
    assert result.output["stdout"] == "echo isolated"


def test_demo_evaluation_and_failure_categories():
    result = evaluate_tasks(discover_tasks(ROOT / "benchmarks/tasks"))
    assert result["summary"]["resolved"] == 5
    assert all(item["status"] == "PASS" for item in result["results"])
    assert classify_failure("FAIL", [{"tool": "file_read"}]) == "Localization failure"
    assert classify_failure("TIMEOUT", []) == "Timeout"


def test_reports_and_docker_limits(tmp_path):
    data = {"summary": {"tasks": 0, "resolved": 0, "resolution_rate": 0}, "results": []}
    json_path = write_json(data, tmp_path / "report.json")
    html_path = write_html(data, tmp_path / "report.html")
    assert json.loads(json_path.read_text()) == data
    assert "CodeBench Evaluation" in html_path.read_text()
    config = DockerSandboxConfig(cpu_limit=2, memory_limit_mb=256)
    assert config.runtime_kwargs()["network_disabled"] is True
    assert config.runtime_kwargs()["nano_cpus"] == 2_000_000_000


def test_local_sandbox_does_not_modify_source(tmp_path):
    source = tmp_path / "repo"
    source.mkdir(); (source / "x.txt").write_text("original", encoding="utf-8")
    with LocalSandbox(source) as workspace:
        (workspace / "x.txt").write_text("changed", encoding="utf-8")
    assert (source / "x.txt").read_text(encoding="utf-8") == "original"