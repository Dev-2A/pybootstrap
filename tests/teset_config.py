"""config 모듈 테스트"""

from pybootstrap.config import BootstrapConfig


class TestBootstrapConfig:
    """BootstrapConfig 테스트"""

    def test_default_values(self):
        config = BootstrapConfig()
        assert config.project_name == ""
        assert config.template_name == "fastapi"
        assert config.python_version == "3.11"
        assert config.use_docker is True
        assert config.use_git is True

    def test_project_slug_hyphen(self):
        config = BootstrapConfig(project_name="my-cool-api")
        assert config.project_slug == "my_cool_api"

    def test_project_slug_space(self):
        config = BootstrapConfig(project_name="my cool api")
        assert config.project_slug == "my_cool_api"

    def test_project_name_kebab(self):
        config = BootstrapConfig(project_name="my_cool_api")
        assert config.project_name_kebab == "my-cool-api"

    def test_to_template_context(self):
        config = BootstrapConfig(
            project_name="test-project",
            author="Dev-2A",
            description="테스트 프로젝트",
        )
        ctx = config.to_template_context()

        assert ctx["project_name"] == "test-project"
        assert ctx["project_slug"] == "test_project"
        assert ctx["project_name_kebab"] == "test-project"
        assert ctx["author"] == "Dev-2A"
        assert ctx["description"] == "테스트 프로젝트"
        assert ctx["use_docker"] is True

    def test_extras_merged(self):
        config = BootstrapConfig(
            project_name="test",
            extras={"custom_key": "custom_value"},
        )
        ctx = config.to_template_context()
        assert ctx["custom_key"] == "custom_value"