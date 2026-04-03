"""템플릿 레지스트리 - 내장/커스텀 템플릿 관리"""

from __future__ import annotations

import json
from pathlib import Path

from .config import get_builtin_templates_dir, get_custom_templates_dir
from .models import FileEntry, TemplateInfo, TemplateType


# ─── 공통 base 파일 정의 ─────────────────────────────────────

BASE_FILES: list[FileEntry] = [
    FileEntry(
        source="base/gitignore.j2",
        destination=".gitignore",
    ),
    FileEntry(
        source="base/README.md.j2",
        destination="README.md",
    ),
    FileEntry(
        source="base/requirements.txt.j2",
        destination="requirements.txt",
    ),
    FileEntry(
        source="base/pyproject.toml.j2",
        destination="pyproject.toml",
    ),
    FileEntry(
        source="base/Dockerfile.j2",
        destination="Dockerfile",
        condition="use_docker",
    ),
]


# ─── 내장 템플릿 정의 ────────────────────────────────────────

def _fastapi_template() -> TemplateInfo:
    """FastAPI 템플릿"""
    return TemplateInfo(
        name="fastapi",
        display_name="⚡ FastAPI",
        description="FastAPI REST API 프로젝트",
        template_type=TemplateType.BUILTIN,
        base_files=BASE_FILES.copy(),
        template_files=[
            FileEntry(
                source="fastapi/main.py.j2",
                destination="src/{{ project_slug }}/main.py",
            ),
            FileEntry(
                source="fastapi/__init__.py.j2",
                destination="src/{{ project_slug }}/__init__.py",
            ),
            FileEntry(
                source="fastapi/routers/__init__.py.j2",
                destination="src/{{ project_slug }}/routers/__init__.py",
            ),
            FileEntry(
                source="fastapi/routers/health.py.j2",
                destination="src/{{ project_slug }}/routers/health.py",
            ),
            FileEntry(
                source="fastapi/schemas.py.j2",
                destination="src/{{ project_slug }}/schemas.py",
            ),
            FileEntry(
                source="fastapi/config.py.j2",
                destination="src/{{ project_slug }}/config.py",
            ),
        ],
        directories=[
            "src/{{ project_slug }}",
            "src/{{ project_slug }}/routers",
            "tests",
        ],
        dependencies=[
            "fastapi>=0.110.0",
            "uvicorn[standard]>=0.29.0",
            "pydantic>=2.0.0",
            "pydantic-settings>=2.0.0",
        ],
        dev_dependencies=[
            "pytest>=8.0.0",
            "httpx>=0.27.0",
        ],
    )


def _cli_template() -> TemplateInfo:
    """Click CLI 템플릿"""
    return TemplateInfo(
        name="cli",
        display_name="🖥️ CLI (Click)",
        description="Click 기반 커맨드라인 도구",
        template_type=TemplateType.BUILTIN,
        base_files=BASE_FILES.copy(),
        template_files=[
            FileEntry(
                source="cli/__init__.py.j2",
                destination="src/{{ project_slug }}/__init__.py",
            ),
            FileEntry(
                source="cli/cli.py.j2",
                destination="src/{{ project_slug }}/cli.py",
            ),
            FileEntry(
                source="cli/core.py.j2",
                destination="src/{{ project_slug }}/core.py",
            ),
        ],
        directories=[
            "src/{{ project_slug }}",
            "tests",
        ],
        dependencies=[
            "click>=8.1.0",
        ],
        dev_dependencies=[
            "pytest>=8.0.0",
        ],
        default_extras={
            "entry_point": "{{ project_slug }}.cli:main",
        },
    )


def _fullstack_template() -> TemplateInfo:
    """React + FastAPI 풀스택 템플릿"""
    return TemplateInfo(
        name="fullstack",
        display_name="🌐 Fullstack (React + FastAPI)",
        description="React 프론트엔드 + FastAPI 백엔드",
        template_type=TemplateType.BUILTIN,
        base_files=[
            # fullstack은 자체 gitignore/README를 사용
            FileEntry(
                source="fullstack/gitignore.j2",
                destination=".gitignore",
            ),
            FileEntry(
                source="fullstack/README.md.j2",
                destination="README.md",
            ),
        ],
        template_files=[
            # Backend
            FileEntry(
                source="fullstack/backend/requirements.txt.j2",
                destination="backend/requirements.txt",
            ),
            FileEntry(
                source="fullstack/backend/main.py.j2",
                destination="backend/main.py",
            ),
            FileEntry(
                source="fullstack/backend/__init__.py.j2",
                destination="backend/__init__.py",
            ),
            FileEntry(
                source="fullstack/backend/Dockerfile.j2",
                destination="backend/Dockerfile",
                condition="use_docker",
            ),
            # Frontend
            FileEntry(
                source="fullstack/frontend/package.json.j2",
                destination="frontend/package.json",
            ),
            FileEntry(
                source="fullstack/frontend/vite.config.js.j2",
                destination="frontend/vite.config.js",
            ),
            FileEntry(
                source="fullstack/frontend/index.html.j2",
                destination="frontend/index.html",
            ),
            FileEntry(
                source="fullstack/frontend/src/App.jsx.j2",
                destination="frontend/src/main.jsx",
            ),
            FileEntry(
                source="fullstack/frontend/Dockerfile.j2",
                destination="frontend/Dockerfile",
                condition="use_docker",
            ),
            # Docker Compose
            FileEntry(
                source="fullstack/docker-compose.yml.j2",
                destination="docker-compose.yml",
                condition="use_docker",
            ),
        ],
        directories=[
            "backend",
            "frontend",
            "frontend/src",
        ],
        dependencies=[
            "fastapi>=0.110.0",
            "uvicorn[standard]>=0.29.0",
        ],
    )


# ─── 레지스트리 ──────────────────────────────────────────────

class TemplateRegistry:
    """내장 + 커스텀 템플릿을 통합 관리하는 레지스트리"""
    
    def __init__(self):
        self._templates: dict[str, TemplateInfo] = {}
        self._register_builtins()
    
    def _register_builtins(self):
        """내장 템플릿 등록"""
        for factory in [_fastapi_template, _cli_template, _fullstack_template]:
            tpl = factory()
            self._templates[tpl.name] = tpl
    
    def register(self, template: TemplateInfo):
        """커스텀 템플릿 등록"""
        self._templates[template.name] = template
    
    def get(self, name: str) -> TemplateInfo | None:
        """이름으로 템플릿 조회"""
        return self._templates.get(name)
    
    def list_all(self) -> list[TemplateInfo]:
        """등록된 모든 템플릿 반환"""
        return list(self._templates.values())
    
    def list_builtin(self) -> list[TemplateInfo]:
        """내장 템플릿만 반환"""
        return [t for t in self._templates.values() if t.template_type == TemplateType.BUILTIN]
    
    def list_custom(self) -> list[TemplateInfo]:
        """커스텀 템플릿만 반환"""
        return [t for t in self._templates.values() if t.template_type == TemplateType.CUSTOM]
    
    def has(self, name: str) -> bool:
        """템플릿 존재 여부 확인"""
        return name in self._templates
    
    def load_custom_templates(self):
        """~/.pybootstrap/templates/ 에서 커스텀 템플릿 로드"""
        custom_dir = get_custom_templates_dir()
        
        for meta_file in custom_dir.glob("*/template.json"):
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                template_dir = meta_file.parent
                
                files = [
                    FileEntry(
                        source=f["source"],
                        destination=f["destination"],
                        condition=f.get("condition"),
                    )
                    for f in meta.get("files", [])
                ]
                
                tpl = TemplateInfo(
                    name=meta["name"],
                    display_name=meta.get("display_name", meta["name"]),
                    description=meta.get("description", "커스텀 템플릿"),
                    template_type=TemplateType.CUSTOM,
                    base_files=BASE_FILES.copy() if meta.get("use_base", True) else [],
                    template_files=files,
                    directories=meta.get("directories", []),
                    template_dir=template_dir,
                    dependencies=meta.get("dependencies", []),
                    dev_dependencies=meta.get("dev_dependencies", []),
                    default_extras=meta.get("default_extras", {}),
                )
                self.register(tpl)
            except (json.JSONDecodeError, KeyError) as e:
                # 잘못된 커스텀 템플릿은 조용히 무시
                continue


def get_registry() -> TemplateRegistry:
    """글로벌 레지스트리 인스턴스 반환 (커스텀 템플릿 포함)"""
    registry = TemplateRegistry()
    registry.load_custom_templates()
    return registry