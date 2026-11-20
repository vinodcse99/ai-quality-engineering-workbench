import sys
from pathlib import Path


def test_python_version():
    assert sys.version_info >= (3, 12)


def test_project_root_exists():
    project_root = Path(__file__).resolve().parents[1]
    assert (project_root / "README.md").exists()


def test_workbench_package_exists():
    project_root = Path(__file__).resolve().parents[1]
    assert (project_root / "src" / "workbench" / "__init__.py").exists()
