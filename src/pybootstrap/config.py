"""PyBootstrap 설정 관리 모듈"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# 커스텀 템플릿 저장 경로 (사용자 홈 디렉토리)
DEFAULT_CUSTOM_TEMPLATES_DIR = Path.home() / ".pybootstrap" / "templates"

# 내장 템플릿 디렉토리
BUILTIN_TEMPLATES_DIR = Path(__file__).parent / "templates"


@dataclass
class BootstrapConfig:
    """프로젝트 생성 시 사용되는 설정"""
    
    project_name: str = ""
    template_name: str = "fastapi"
    author: str = ""
    description: str = ""
    python_version: str = "3.11"
    use_docker: bool = True
    use_git: bool = True
    extras: dict = field(default_factory=dict)
    
    @property
    def project_slug(self) -> str:
        """프로젝트 이름을 슬러그 형태로 변환 (하이픈 → 언더스코어)"""
        return self.project_name.replace("-", "_").replace(" ", "_").lower()
    
    @property
    def project_name_kebab(self) -> str:
        """프로젝트 이름을 케밥 케이스로 변환"""
        return self.project_name.replace("_", "-").replace(" ", "-").lower()
    
    def to_template_context(self) -> dict:
        """Jinja2 템플릿에 전달할 컨텍스트 딕셔너리 생성"""
        return {
            "project_name": self.project_name,
            "project_slug": self.project_slug,
            "project_name_kebab": self.project_name_kebab,
            "author": self.author,
            "description": self.description,
            "python_version": self.python_version,
            "use_docker": self.use_docker,
            "use_git": self.use_git,
            **self.extras,
        }


def get_custom_templates_dir() -> Path:
    """커스텀 템플릿 디렉토리 경로 반환 (없으면 생성)"""
    path = DEFAULT_CUSTOM_TEMPLATES_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_builtin_templates_dir() -> Path:
    """내장 템플릿 디렉토리 경로 반환"""
    return BUILTIN_TEMPLATES_DIR