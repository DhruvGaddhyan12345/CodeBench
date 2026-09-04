import shutil
import tempfile
from pathlib import Path


class LocalSandbox:
    """Disposable copy used for deterministic runs and environments without Docker."""

    def __init__(self, repository: str | Path):
        self.repository = Path(repository).resolve()
        self.path: Path | None = None

    def __enter__(self) -> Path:
        if not self.repository.is_dir():
            raise FileNotFoundError(f"repository does not exist: {self.repository}")
        self.path = Path(tempfile.mkdtemp(prefix="codebench-")) / "workspace"
        shutil.copytree(self.repository, self.path)
        return self.path

    def __exit__(self, *_: object) -> None:
        if self.path:
            shutil.rmtree(self.path.parent, ignore_errors=True)
