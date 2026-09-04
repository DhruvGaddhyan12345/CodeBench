import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DockerSandboxConfig:
    image: str = "codebench-sandbox:latest"
    cpu_limit: float = 1.0
    memory_limit_mb: int = 512
    timeout_seconds: int = 120
    network_disabled: bool = True
    user: str = "1000:1000"
    dockerfile: str = "docker/Dockerfile.sandbox"

    def runtime_kwargs(self) -> dict[str, object]:
        return {"network_disabled": self.network_disabled, "nano_cpus": int(self.cpu_limit * 1e9),
                "mem_limit": f"{self.memory_limit_mb}m", "user": self.user, "remove": True}


class DockerSandboxError(RuntimeError):
    """Raised when a Docker-backed evaluation cannot be started."""


class DockerSandbox:
    """Run commands against a disposable repository copy in a constrained container."""

    def __init__(self, repository: str | Path, config: DockerSandboxConfig | None = None):
        self.repository = Path(repository).resolve()
        self.config = config or DockerSandboxConfig()
        self.path: Path | None = None

    @staticmethod
    def available() -> bool:
        try:
            return subprocess.run(["docker", "info"], capture_output=True, timeout=15).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False

    def __enter__(self) -> "DockerSandbox":
        if not self.repository.is_dir():
            raise FileNotFoundError(f"repository does not exist: {self.repository}")
        if not self.available():
            raise DockerSandboxError("Docker daemon is unavailable; start Docker Desktop and retry")
        self.path = Path(tempfile.mkdtemp(prefix="codebench-docker-")) / "workspace"
        shutil.copytree(self.repository, self.path)
        self._ensure_image()
        return self

    def _ensure_image(self) -> None:
        inspected = subprocess.run(["docker", "image", "inspect", self.config.image],
                                   capture_output=True, text=True)
        if inspected.returncode == 0:
            return
        dockerfile = Path(self.config.dockerfile)
        if not dockerfile.exists():
            raise DockerSandboxError(f"Docker image {self.config.image!r} is missing and {dockerfile} was not found")
        built = subprocess.run(["docker", "build", "-t", self.config.image,
                                "-f", str(dockerfile), "."], capture_output=True, text=True)
        if built.returncode != 0:
            raise DockerSandboxError(built.stderr.strip() or "Docker image build failed")

    def run(self, command: str, timeout: int = 30, working_directory: str = ".") -> dict[str, object]:
        if not self.path:
            raise DockerSandboxError("DockerSandbox must be entered before running commands")
        relative_directory = Path(working_directory)
        if relative_directory.is_absolute() or ".." in relative_directory.parts:
            raise DockerSandboxError("working directory escapes the repository workspace")
        workdir = (Path("/workspace") / relative_directory).as_posix()
        args = ["docker", "run", "--rm", "--network", "none", "--cpus", str(self.config.cpu_limit),
                "--memory", f"{self.config.memory_limit_mb}m", "--user", self.config.user,
                "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "-v", f"{self.path.resolve()}:/workspace", "-w", workdir,
                self.config.image, "sh", "-lc", command]
        try:
            completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            return {"stdout": exc.stdout or "", "stderr": "command timed out", "exit_code": None,
                    "timed_out": True}
        return {"stdout": completed.stdout, "stderr": completed.stderr,
                "exit_code": completed.returncode, "timed_out": False}

    def __exit__(self, *_: object) -> None:
        if self.path:
            shutil.rmtree(self.path.parent, ignore_errors=True)
