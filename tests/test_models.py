"""models 모듈 테스트"""

from pybootstrap.models import FileEntry, TemplateInfo, TemplateType


class TestFileEntry:
    """FileEntry 테스트"""

    def test_basic(self):
        entry = FileEntry(source="base/README.md.j2", destination="README.md")
        assert entry.source == "base/README.md.j2"
        assert entry.destination == "README.md"
        assert entry.condition is None

    def test_with_condition(self):
        entry = FileEntry(
            source="base/Dockerfile.j2",
            destination="Dockerfile",
            condition="use_docker",
        )
        assert entry.condition == "use_docker"


class TestTemplateInfo:
    """TemplateInfo 테스트"""

    def test_all_files(self):
        tpl = TemplateInfo(
            name="test",
            display_name="Test",
            description="테스트",
            base_files=[
                FileEntry(source="a.j2", destination="a"),
            ],
            template_files=[
                FileEntry(source="b.j2", destination="b"),
                FileEntry(source="c.j2", destination="c"),
            ],
        )
        assert len(tpl.all_files) == 3

    def test_summary(self):
        tpl = TemplateInfo(
            name="test",
            display_name="🧪 Test",
            description="테스트 템플릿",
            dependencies=["click", "rich"],
        )
        summary = tpl.summary()
        assert "🧪 Test" in summary
        assert "테스트 템플릿" in summary

    def test_template_type_default(self):
        tpl = TemplateInfo(name="t", display_name="T", description="d")
        assert tpl.template_type == TemplateType.BUILTIN