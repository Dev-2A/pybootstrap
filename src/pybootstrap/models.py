"""템플릿 데이터 모델"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class TemplateType(str, Enum):
    """템플릿 유형"""
    
    BUILTIN = "builtin"
    CUSTOM = "custom"


@dataclass
class FileEntry:
    """생성할 파일 하나의 정보"""
    
    # 템플릿 소스 파일 (상대 경로, .j2 확장자 포함)
    source: str
    # 생성될 파일의 대상 경로 (프로젝트 루트 기준 상대 경로)
    destination: str
    # 조건부 생성 (예: use_docker=True일 때만)
    condition: str | None = None


@dataclass
class TemplateInfo:
    """템플릿 메타 정보"""
    
    name: str
    display_name: str
    description: str
    template_type: TemplateType = TemplateType.BUILTIN
    # 이 템플릿이 사용하는 base 파일 목록
    base_files: list[FileEntry] = field(default_factory=list)
    # 이 템플릿 고유의 파일 목록
    template_files: list[FileEntry] = field(default_factory=list)
    # 이 템플릿에서 생성할 디렉토리 목록 (프로젝트 루트 기준)
    directories: list[str] = field(default_factory=list)
    # 템플릿 디렉토리 경로 (커스텀 템플릿용)
    template_dir: Path | None = None
    # 추가 의존성 (requirements.txt에 추가될 패키지)
    dependencies: list[str] = field(default_factory=list)
    # 추가 개발 의존성
    dev_dependencies: list[str] = field(default_factory=list)
    # 기본 extras 값 (Jinja2 컨텍스트에 병합)
    default_extras: dict = field(default_factory=dict)
    
    @property
    def all_files(self) -> list[FileEntry]:
        """base + template 파일을 합쳐 반환"""
        return self.base_files + self.template_files
    
    def summary(self) -> str:
        """템플릿 요약 문자열"""
        total = len(self.all_files)
        dirs = len(self.directories)
        deps = len(self.dependencies)
        return (
            f"{self.display_name} - {self.description}\n"
            f"  파일 {total}개 · 디렉토리 {dirs}개 · 의존성 {deps}개"
        )