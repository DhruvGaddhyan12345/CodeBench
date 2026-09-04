# CodeBench — Coding-Agent Evaluation & Safety Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Sandbox-blue.svg)](https://www.docker.com/)
[![SWE-bench](https://img.shields.io/badge/SWE--bench-Lite-orange.svg)](https://www.swebench.com/)

CodeBench is a **reproducible evaluation and safety platform for autonomous coding agents**.

## Project Context

CodeBench is designed as a **Coding-Agent Evaluation & Safety Platform** for repository-level software tasks before deployment. Its intended workflow combines ReAct and Plan-Execute agent adapters with isolated Docker execution, controlled resource and network access, six schema-oriented repository/testing tools, patch-based grading, and reproducibility analysis.

### Current implementation status

| Capability | Status and evidence |
| --- | --- |
| ReAct and Plan-Execute workflows | Implemented through the deterministic local agent; Plan-Execute records an explicit plan phase. |
| Six controlled tools | Implemented: repository search, file read, apply patch, shell command, test execution, and task inspection. |
| Docker isolation | Implemented in `DockerSandbox`; network is disabled, the container is non-root, capabilities are dropped, and CPU, memory, timeout, and workspace limits are configured. Requires a running Docker daemon for live execution. |
| Reproducible grading | Implemented with disposable workspaces, repeated runs, trajectories, test results, and flakiness detection. |
| Failure analysis | Implemented for localization, patch generation, timeout, test execution, and flakiness. |
| SWE-bench compatibility | Implemented as a record adapter; it does not download or evaluate SWE-bench automatically. |
| Included benchmark | Five local demo tasks are implemented and runnable. |

The five local demo tasks currently resolve `5/5` under the deterministic demo agent. This is a **demo result**, not a SWE-bench result. A 50-task SWE-bench Lite run and a `12/50` result have **not** been executed in this repository, so they are intentionally not claimed. The benchmark runner accepts arbitrary task directories and `--runs`, making a controlled 50-task evaluation the next measurement step once real task data, a fixed agent configuration, and a working Docker daemon are supplied.

### Intended evaluation claim

The project supports measuring task resolution, execution time, median and average latency, tool calls, trajectories, token usage when an external agent provides it, test outcomes, and failure distributions. It does not fabricate token counts or benchmark scores. Safety results are produced from live probes when Docker is available; otherwise the report records the infrastructure failure.

## Problem and solution

It evaluates repository-level software engineering tasks by placing coding agents behind a controlled tool interface, executing their changes inside isolated environments, grading patches using tests rather than self-reported success, and recording complete execution trajectories for reliability analysis.

CodeBench is an **evaluation platform, not a coding model**.

---

## Why CodeBench?

Autonomous coding agents can modify repositories, execute commands, install dependencies, and run tests. Evaluating these agents directly on a developer's machine creates two problems:

1. **Safety** — agent-generated commands should not have unrestricted access to the host system.
2. **Evaluation** — an agent claiming that a task is complete does not prove that the repository actually works.

CodeBench addresses both problems:

```text
Coding Agent
     │
     ▼
Controlled Tool Interface
     │
     ▼
Isolated Sandbox
     │
     ▼
Repository Workspace
     │
     ├── Search
     ├── Read
     ├── Patch
     ├── Execute
     └── Test
     │
     ▼
Generated Patch
     │
     ▼
Test-Based Grading
     │
     ▼
Trajectory + Metrics
     │
     ▼
Reliability / Failure Analysis
