"""registry 모듈 테스트"""

from pybootstrap.models import TemplateInfo, TemplateType
from pybootstrap.registry import TemplateRegistry, get_registry


class TestTemplateRegistry:
    """TemplateRegistry 테스트"""

    def test_builtins_registered(self):
        registry = TemplateRegistry()
        assert registry.has("fastapi")
        assert registry.has("cli")
        assert registry.has("fullstack")

    def test_list_builtin(self):
        registry = TemplateRegistry()
        builtins = registry.list_builtin()
        assert len(builtins) == 3
        names = {t.name for t in builtins}
        assert names == {"fastapi", "cli", "fullstack"}

    def test_get_returns_none_for_unknown(self):
        registry = TemplateRegistry()
        assert registry.get("nonexistent") is None

    def test_register_custom(self):
        registry = TemplateRegistry()
        custom = TemplateInfo(
            name="flask",
            display_name="Flask",
            description="Flask 웹 앱",
            template_type=TemplateType.CUSTOM,
        )
        registry.register(custom)
        assert registry.has("flask")
        assert len(registry.list_custom()) == 1

    def test_get_registry_includes_builtins(self):
        registry = get_registry()
        assert registry.has("fastapi")
        assert registry.has("cli")
        assert registry.has("fullstack")


class TestBuiltinTemplates:
    """내장 템플릿 데이터 검증"""

    def test_fastapi_has_files(self):
        registry = TemplateRegistry()
        tpl = registry.get("fastapi")
        assert tpl is not None
        assert len(tpl.template_files) > 0
        assert len(tpl.base_files) > 0
        assert "fastapi" in str(tpl.dependencies)

    def test_cli_has_click_dependency(self):
        registry = TemplateRegistry()
        tpl = registry.get("cli")
        assert tpl is not None
        deps_str = " ".join(tpl.dependencies)
        assert "click" in deps_str

    def test_fullstack_has_frontend_files(self):
        registry = TemplateRegistry()
        tpl = registry.get("fullstack")
        assert tpl is not None
        destinations = [f.destination for f in tpl.all_files]
        has_frontend = any("frontend" in d for d in destinations)
        has_backend = any("backend" in d for d in destinations)
        assert has_frontend
        assert has_backend