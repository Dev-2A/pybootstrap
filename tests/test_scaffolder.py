"""scaffolder 모듈 테스트"""

import shutil
from pathlib import Path

import pytest

from pybootstrap.config import BootstrapConfig
from pybootstrap.registry import TemplateRegistry
from pybootstrap.scaffolder import ScaffoldError, Scaffolder


@pytest.fixture
def tmp_output(tmp_path):
    """임시 출력 디렉토리"""
    return tmp_path


@pytest.fixture
def registry():
    return TemplateRegistry()


class TestScaffolderFastAPI:
    """FastAPI 템플릿 스캐폴딩 테스트"""

    def test_creates_project_dir(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-api",
            template_name="fastapi",
            description="테스트 API",
            use_git=False,
        )
        template = registry.get("fastapi")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        assert result.project_dir.exists()
        assert result.project_dir.name == "my-api"

    def test_creates_expected_files(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-api",
            template_name="fastapi",
            use_git=False,
        )
        template = registry.get("fastapi")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        project = result.project_dir
        assert (project / "README.md").exists()
        assert (project / ".gitignore").exists()
        assert (project / "requirements.txt").exists()
        assert (project / "pyproject.toml").exists()
        assert (project / "Dockerfile").exists()
        assert (project / "src" / "my_api" / "main.py").exists()
        assert (project / "src" / "my_api" / "__init__.py").exists()

    def test_no_docker(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-api",
            template_name="fastapi",
            use_docker=False,
            use_git=False,
        )
        template = registry.get("fastapi")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        assert not (result.project_dir / "Dockerfile").exists()

    def test_readme_contains_project_name(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="awesome-api",
            template_name="fastapi",
            description="멋진 API",
            use_git=False,
        )
        template = registry.get("fastapi")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        readme = (result.project_dir / "README.md").read_text(encoding="utf-8")
        assert "awesome-api" in readme
        assert "멋진 API" in readme

    def test_duplicate_dir_raises_error(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-api",
            template_name="fastapi",
            use_git=False,
        )
        template = registry.get("fastapi")

        # 첫 번째 생성
        scaffolder = Scaffolder(config, template)
        scaffolder.scaffold(tmp_output)

        # 두 번째 시도 → 에러
        scaffolder2 = Scaffolder(config, template)
        with pytest.raises(ScaffoldError, match="이미 존재"):
            scaffolder2.scaffold(tmp_output)


class TestScaffolderCLI:
    """CLI 템플릿 스캐폴딩 테스트"""

    def test_creates_cli_files(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-tool",
            template_name="cli",
            use_git=False,
        )
        template = registry.get("cli")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        project = result.project_dir
        assert (project / "src" / "my_tool" / "cli.py").exists()
        assert (project / "src" / "my_tool" / "core.py").exists()
        assert (project / "src" / "my_tool" / "__init__.py").exists()

    def test_requirements_has_click(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-tool",
            template_name="cli",
            use_git=False,
        )
        template = registry.get("cli")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        reqs = (result.project_dir / "requirements.txt").read_text(encoding="utf-8")
        assert "click" in reqs


class TestScaffolderFullstack:
    """Fullstack 템플릿 스캐폴딩 테스트"""

    def test_creates_both_dirs(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-app",
            template_name="fullstack",
            use_git=False,
        )
        template = registry.get("fullstack")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        project = result.project_dir
        assert (project / "backend" / "main.py").exists()
        assert (project / "frontend" / "package.json").exists()
        assert (project / "frontend" / "src" / "App.jsx").exists()

    def test_docker_compose_created(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="my-app",
            template_name="fullstack",
            use_docker=True,
            use_git=False,
        )
        template = registry.get("fullstack")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        assert (result.project_dir / "docker-compose.yml").exists()
        assert (result.project_dir / "backend" / "Dockerfile").exists()
        assert (result.project_dir / "frontend" / "Dockerfile").exists()


class TestScaffoldResult:
    """ScaffoldResult 테스트"""

    def test_file_count(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="counter-test",
            template_name="fastapi",
            use_git=False,
        )
        template = registry.get("fastapi")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        assert result.file_count > 0
        assert result.dir_count > 0

    def test_summary(self, tmp_output, registry):
        config = BootstrapConfig(
            project_name="summary-test",
            template_name="cli",
            use_git=False,
        )
        template = registry.get("cli")
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(tmp_output)

        summary = result.summary()
        assert "summary-test" in summary
        assert "cli" in summary