# CodeBench — Coding-Agent Evaluation & Safety Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Sandbox-blue.svg)](https://www.docker.com/)
[![SWE-bench](https://img.shields.io/badge/SWE--bench-Lite-orange.svg)](https://www.swebench.com/)

CodeBench is a **reproducible evaluation and safety platform for autonomous coding agents**.

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
