# CodeBench - Coding-Agent Evaluation & Safety Platform

CodeBench is a local evaluation harness for autonomous coding agents, not a coding model. It provides a controlled tool interface, disposable repository workspaces, test-based grading, reproducible runs, and failure analysis.

## Problem and solution

Agent-generated commands and patches should not run directly on a developer's machine, and an agent's claim of success is not evidence. CodeBench copies each repository into a disposable workspace, exposes six observable operations, runs the task tests, and records the result and trajectory.

```text
Coding Agent -> Tool Interface -> Sandbox -> Repository -> Patch -> Tests -> Report
```

## Components

The task manager validates task metadata. The tool interface provides `repository_search`, `file_read`, `apply_patch`, `shell_command`, `test_execution`, and `task_inspection`. The sandbox has a local disposable backend plus Docker runtime configuration. The deterministic demo agent exercises the same tools an external agent can later implement. The grader trusts test outcomes, while the trajectory and failure analyzer explain behavior rather than only returning `FAILED`.

## Safety model

Docker runs use a fresh container with disabled networking, a non-root user, CPU and memory limits, an isolated workspace, dropped capabilities, and a wall-clock timeout. `DockerSandbox` invokes the Docker CLI and routes shell/test commands through that container. Use `--sandbox docker` to select it. The default demo uses `LocalSandbox` for portability when Docker is unavailable; it is process/filesystem isolation for a copied workspace, not a perfect security boundary. `scripts/run_safety_tests.py` exercises the live boundary when the daemon is available and reports infrastructure failures otherwise.

## Installation and quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python scripts/run_demo.py
python -m pytest
```

The demo creates `reports/evaluations/task_results.json` and `evaluation_report.html`. The included five tasks are local demonstrations, not SWE-bench results. List tasks with `python -m codebench.cli task list`, or run a benchmark with `python scripts/run_benchmark.py --tasks benchmarks/tasks --runs 3`.

## Metrics and reproducibility

Reports contain resolution status, measured execution time, tool calls, full structured trajectory, test output, strategy, and token usage as `null` when unavailable. `scripts/repeat_evaluation.py --task demo-001 --runs 3` records each outcome and flags differing statuses as flakiness. No benchmark numbers are hard-coded.

## Failure categories

Failures are classified as Localization failure, Patch-generation failure, Timeout, Test-execution failure, or Flakiness. Classification remains conservative and returns no category for a passing task.

## SWE-bench compatibility and limitations

`TaskSpec` contains the concepts needed to adapt an SWE-bench Lite record: task ID, repository, base commit, problem statement, test command, and result. The repository does not download or claim to evaluate SWE-bench. A production deployment would need stronger container hardening, a Docker lifecycle backend, real LLM adapters, patch capture from Git, and broader benchmark coverage.
