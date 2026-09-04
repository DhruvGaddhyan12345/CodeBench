import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from codebench.sandbox import DockerSandbox, DockerSandboxError


root = Path(__file__).parents[1]
repository = root / "benchmarks/tasks/demo_task_001/repository"
results = []


def record(name: str, passed: bool, diagnostic: str) -> None:
    results.append({"name": name, "status": "PASS" if passed else "FAIL", "diagnostic": diagnostic})


if not DockerSandbox.available():
    record("docker_available", False, "Docker daemon is unavailable; no container safety claims were made")
else:
    try:
        with DockerSandbox(repository) as sandbox:
            network = sandbox.run("python -c \"import urllib.request; urllib.request.urlopen('https://example.com', timeout=2)\"", 5)
            record("network_isolation", network["exit_code"] != 0, str(network))
            host = sandbox.run("test -e /host || test -e /host-filesystem", 5)
            record("host_filesystem_boundary", host["exit_code"] != 0, str(host))
            privilege = sandbox.run("touch /etc/codebench-privilege-test", 5)
            record("privilege_restriction", privilege["exit_code"] != 0, str(privilege))
            identity = sandbox.run("id -u", 5)
            record("non_root_identity", identity["stdout"].strip() == "1000", str(identity))
            workspace = sandbox.run("test -f /workspace/calculator.py && test ! -f /workspace/../host", 5)
            record("repository_boundary", workspace["exit_code"] == 0, str(workspace))
            timeout = sandbox.run("python -c \"import time; time.sleep(10)\"", 1)
            record("process_timeout", bool(timeout.get("timed_out")), str(timeout))
            cpu = sandbox.run("python -c \"while True: pass\"", 2)
            record("cpu_limit", bool(cpu.get("timed_out")) or cpu["exit_code"] != 0, str(cpu))
            memory = sandbox.run("python -c \"x = bytearray(1024 * 1024 * 1024)\"", 5)
            record("memory_limit", memory["exit_code"] != 0, str(memory))
        record("container_cleanup", sandbox.path is not None and not sandbox.path.parent.exists(), "workspace removed after context exit")
    except (DockerSandboxError, OSError) as exc:
        record("docker_execution", False, str(exc))

output = {"scope": "controlled Docker execution boundary demonstration; not formal security research", "results": results}
(root / "reports/safety").mkdir(parents=True, exist_ok=True)
(root / "reports/safety/results.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
print(output)
