"""Guard rails for root-level Docker Compose (see docs/issues/e2e-api-tests/sub-1)."""

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_docker_compose_lives_at_repo_root_not_in_backend() -> None:
    root = _repo_root()
    assert (root / "docker-compose.yml").is_file()
    assert (root / "docker-compose.test.yml").is_file()
    assert not (root / "backend" / "docker-compose.yml").exists()


def test_makefile_at_repo_root() -> None:
    assert (_repo_root() / "Makefile").is_file()
