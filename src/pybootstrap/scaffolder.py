"""프로젝트 스캐폴딩 엔진 - Jinja2 렌더링 + 파일 생성"""

from __future__ import annotations

import subprocess
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import BootstrapConfig, get_builtin_templates_dir
from .models import FileEntry, TemplateInfo, TemplateType


class ScaffoldError(Exception):
    """스캐폴딩 중 발생하는 에러"""
    pass


class Scaffolder:
    """Jinja2 기반 프로젝트 스캐폴더"""
    
    def __init__(self, config: BootstrapConfig, template: TemplateInfo):
        self.config = config
        self.template = template
        self.context = self._build_context()
        self.env = self._create_jinja_env()
        self.created_files: list[str] = []
        self.created_dirs: list[str] = []
    
    def _build_context(self) -> dict:
        """Jinja2 렌더링 컨텍스트 구성"""
        # 템플릿 기본 extras → 사용자 config extras 순으로 병합
        ctx = {
            "template_name": self.template.name,
            "dependencies": self.template.dependencies,
            "dev_dependencies": self.template.dev_dependencies,
        }
        # 템플릿 default_extras 먼저 적용
        ctx.update(self.template.default_extras)
        # 사용자 설정으로 덮어쓰기
        ctx.update(self.config.to_template_context())
        return ctx
    
    def _create_jinja_env(self) -> Environment:
        """Jinja2 Environment 생성 (내장 + 커스텀 경로 지원)"""
        search_paths = []
        
        # 커스텀 템플릿이면 해당 디렉토리 우선
        if (
            self.template.template_type == TemplateType.CUSTOM
            and self.template.template_dir
        ):
            search_paths.append(str(self.template.template_dir))
        
        # 내장 템플릿 디렉토리 (base 포함)
        search_paths.append(str(get_builtin_templates_dir()))
        
        return Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=select_autoescape([]),
            keep_trailing_newline=True,
            # Jinja2 기본 블록 태그가 템플릿 내용과 충돌하지 않도록 유지
        )
    
    def _render_path(self, path_template: str) -> str:
        """경로 문자열 내 {{ 변수 }}를 렌더링"""
        if "{{" in path_template:
            tmpl = self.env.from_string(path_template)
            return tmpl.render(self.context)
        return path_template
    
    def _should_create(self, entry: FileEntry) -> bool:
        """조건부 파일 생성 여부 확인"""
        if entry.condition is None:
            return True
        # condition 문자열을 컨텍스트에서 truthy 검사
        value = self.context.get(entry.condition, False)
        return bool(value)
    
    def _render_template(self, source: str) -> str:
        """Jinja2 템플릿 파일을 렌더링"""
        try:
            tmpl = self.env.get_template(source)
            return tmpl.render(self.context)
        except Exception as e:
            raise ScaffoldError(f"템플릿 렌더링 실패: {source}\n → {e}")
    
    def scaffold(self, output_dir: Path) -> ScaffoldResult:
        """프로젝트 스캐폴딩 실행
        
        Args:
            output_dir: 프로젝트를 생성할 디렉토리
        
        Returns:
            ScaffoldResult: 생성 결과
        """
        project_dir = output_dir / self.config.project_name_kebab
        
        # 이미 존재하는 디렉토리 확인
        if project_dir.exists():
            raise ScaffoldError(
                f"디렉토리가 이미 존재합니다: {project_dir}\n"
                f"  → 다른 이름을 사용하거나 기존 디렉토리를 삭제해주세요."
            )
        
        # 1. 프로젝트 루트 디렉토리 생성
        project_dir.mkdir(parents=True)
        self.created_dirs.append(str(project_dir))
        
        # 2. 템플릿에 정의된 하위 디렉토리 생성
        for dir_template in self.template.directories:
            dir_path = project_dir / self._render_path(dir_template)
            dir_path.mkdir(parents=True, exist_ok=True)
            self.created_dirs.append(str(dir_path.relative_to(project_dir)))
        
        # 3. 파일 생성 (base + template)
        for entry in self.template.all_files:
            if not self._should_create(entry):
                continue
            
            dest_rel = self._render_path(entry.destination)
            dest_path = project_dir / dest_rel
            
            # 부모 디렉토리 자동 생성
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 렌더링 + 쓰기
            content = self._render_template(entry.source)
            dest_path.write_text(content, encoding="utf-8")
            self.created_files.append(dest_rel)
        
        # 4. git init (옵션)
        git_initialized = False
        if self.config.use_git:
            git_initialized = self._init_git(project_dir)
        
        return ScaffoldResult(
            project_dir=project_dir,
            template_name=self.template.name,
            created_files=self.created_files.copy(),
            created_dirs=self.created_dirs.copy(),
            git_initialized=git_initialized,
        )
    
    def _init_git(self, project_dir: Path) -> bool:
        """git init 실행"""
        try:
            subprocess.run(
                ["git", "init"],
                cwd=project_dir,
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


class ScaffoldResult:
    """스캐폴딩 결과"""
    
    def __init__(
        self,
        project_dir: Path,
        template_name: str,
        created_files: list[str],
        created_dirs: list[str],
        git_initialized: bool,
    ):
        self.project_dir = project_dir
        self.template_name = template_name
        self.created_files = created_files
        self.created_dirs = created_dirs
        self.git_initialized = git_initialized
    
    @property
    def file_count(self) -> int:
        return len(self.created_files)
    
    @property
    def dir_count(self) -> int:
        return len(self.created_dirs)
    
    def summary(self) -> str:
        return (
            f"프로젝트 생성 완료: {self.project_dir}\n"
            f"  템플릿: {self.template_name}\n"
            f"  파일: {self.file_count}개\n"
            f"  디렉토리: {self.dir_count}개\n"
            f"  Git: {'초기화 완료' if self.git_initialized else '건너뜀'}"
        )