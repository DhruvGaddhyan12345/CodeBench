from codebench.agents import DemoAgent
from codebench.analysis import classify_failure
from codebench.grading import grade
from codebench.sandbox import DockerSandbox, LocalSandbox


def evaluate_task(task, strategy: str = "react", sandbox: str = "local") -> dict:
    sandbox_type = DockerSandbox if sandbox == "docker" else LocalSandbox
    with sandbox_type(task.repository) as instance:
        root = instance.path if sandbox == "docker" else instance
        executor = instance.run if sandbox == "docker" else None
        run = DemoAgent(strategy).run(task, root, executor)
        result = grade(task, root, executor)
        return {"task_id": task.task_id, "status": result.status,
                "execution_time_seconds": run.duration_seconds, "tool_calls": len(run.trajectory),
                "trajectory": run.trajectory, "token_usage": run.token_usage,
                "failure_category": classify_failure(result.status, run.trajectory),
                "test_result": result.to_dict(), "strategy": strategy,
                "execution_backend": sandbox}


def evaluate_tasks(tasks, strategy: str = "react", sandbox: str = "local") -> dict:
    results = [evaluate_task(task, strategy, sandbox) for task in tasks]
    resolved = sum(item["status"] == "PASS" for item in results)
    times = [item["execution_time_seconds"] for item in results]
    return {"results": results, "summary": {"tasks": len(results), "resolved": resolved,
            "resolution_rate": resolved / len(results) if results else 0,
            "average_execution_time_seconds": sum(times) / len(times) if times else 0,
            "average_tool_calls": sum(item["tool_calls"] for item in results) / len(results) if results else 0}}
