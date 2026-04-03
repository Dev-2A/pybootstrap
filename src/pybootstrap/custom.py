"""커스텀 템플릿 생성/관리 모듈"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .config import get_custom_templates_dir
from .models import FileEntry, TemplateInfo, TemplateType


class CustomTemplateError(Exception):
    """커스텀 템플릿 관련 에러"""
    pass


def init_custom_template(
    name: str,
    display_name: str = "",
    description: str = "",
) -> Path:
    """빈 커스텀 템플릿 스켈레톤을 생성
    
    Args:
        name: 템플릿 이름 (디렉토리명)
        display_name: 표시 이름
        description: 설명
    
    Returns:
        생성된 템플릿 디렉토리 경로
    """
    custom_dir = get_custom_templates_dir()
    template_dir = custom_dir / name
    
    if template_dir.exists():
        raise CustomTemplateError(
            f"커스텀 템플릿 '{name}'이 이미 존재합니다: {template_dir}"
        )
    
    template_dir.mkdir(parents=True)
    
    # template.json 메타 파일 생성
    meta = {
        "name": name,
        "display_name": display_name or f"🔧 {name}",
        "description": description or f"{name} 커스텀 템플릿",
        "use_base": True,
        "files": [
            {
                "source": f"{name}/__init__.py.j2",
                "destination": "src/{{{{ project_slug }}}}/__init__.py",
            },
            {
                "source": f"{name}/main.py.j2",
                "destination": "src/{{{{ project_slug }}}}/main.py",
            },
        ],
        "directories": [
            "src/{{ project_slug }}",
            "tests",
        ],
        "dependencies": [],
        "dev_dependencies": [
            "pytest>=8.0.0",
        ],
        "default_extras": {},
    }
    
    meta_path = template_dir / "template.json"
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    # 샘플 j2 파일 생성
    tpl_files_dir = template_dir / name
    tpl_files_dir.mkdir()
    
    init_j2 = tpl_files_dir / "__init__.py.j2"
    init_j2.write_text(
        '"""{{ project_name}}"""\n\n__version__="0.1.0"\n',
        encoding="utf-8",
    )
    
    main_j2 = tpl_files_dir / "main.py.j2"
    main_j2.write_text(
        '"""{{ project_name }} — 메인 모듈"""\n\n\n'
        'def main():\n'
        '    """메인 함수"""\n'
        '    print("Hello from {{ project_name }}!")\n\n\n'
        'if __name__ == "__main__":\n'
        '    main()\n',
        encoding="utf-8",
    )
    
    return template_dir


def import_as_template(
    source_dir: Path,
    name: str,
    display_name: str = "",
    description: str = "",
    extensions: tuple[str, ...] = (".py", ".toml", ".txt", ".md", ".yml", ".yaml", ".json", ".cfg"),
) -> Path:
    """기존 프로젝트 디렉토리를 커스텀 템플릿으로 변환
    
    Args:
        source_dir: 소스 프로젝트 디렉토리
        name: 템플릿 이름
        display_name: 표시 이름
        description: 설명
        extensions: 포함할 파일 확장자
    
    Returns:
        생성된 템플릿 디렉토리 경로
    """
    if not source_dir.is_dir():
        raise CustomTemplateError(f"디렉토리를 찾을  수 없습니다: {source_dir}")
    
    custom_dir = get_custom_templates_dir()
    template_dir = custom_dir / name
    
    if template_dir.exists():
        raise CustomTemplateError(
            f"커스텀 템플릿 '{name}'이 이미 존재합니다: {template_dir}"
        )
    
    template_dir.mkdir(parents=True)
    tpl_files_dir = template_dir / name
    tpl_files_dir.mkdir()
    
    # 소스 디렉토리에서 파일 수집
    files_meta: list[dict] = []
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "node_modules", ".idea", ".vscode"}
    
    for file_path in sorted(source_dir.rglob("*")):
        # 건너뛸 디렉토리 체크
        if any(skip in file_path.parts for skip in skip_dirs):
            continue
        
        if not file_path.is_file():
            continue
        
        # 확장자 필터
        if file_path.suffix not in extensions and file_path.name not in ("Dockerfile", ".gitignore", "Makefile"):
            continue
        
        rel_path = file_path.relative_to(source_dir)
        j2_name = str(rel_path).replace("\\", "/") + ".j2"
        dest_j2 = tpl_files_dir / j2_name
        
        # 디렉토리 생성
        dest_j2.parent.mkdir(parents=True, exist_ok=True)
        
        # 파일 내용을 .j2로 복사 (그대로 - 사용자가 나중에 {{ 변수 }} 추가)
        try:
            content = file_path.read_text(encoding="utf-8")
            dest_j2.write_text(content, encoding="utf-8")
        except UnicodeDecodeError:
            continue
        
        files_meta.append({
            "source": f"{name}/{j2_name}",
            "destination": str(rel_path).replace("\\", "/"),
        })
    
    # template.json 생성
    # 디렉토리 목록 추출
    directories = set()
    for fm in files_meta:
        dest = fm["destination"]
        parts = dest.replace("\\", "/").split("/")
        for i in range(1, len(parts)):
            directories.add("/".join(parts[:i]))
    
    meta = {
        "name": name,
        "display_name": display_name or f"🔧 {name}",
        "description": description or f"{name} (imported from {source_dir.name})",
        "use_base": False,
        "files": files_meta,
        "directories": sorted(directories),
        "dependencies": [],
        "dev_dependencies": [],
        "default_extras": {},
    }
    
    meta_path = template_dir / "template.json"
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    return template_dir


def delete_custom_template(name: str) -> bool:
    """커스텀 템플릿 삭제
    
    Args:
        name: 삭제할 템플릿 이름
    
    Returns:
        삭제 성공 여부
    """
    custom_dir = get_custom_templates_dir()
    template_dir = custom_dir / name
    
    if not template_dir.exists():
        return False
    
    shutil.rmtree(template_dir)
    return True


def list_custom_template_dirs() -> list[Path]:
    """설치된 커스텀 템플릿 디렉토리 목록"""
    custom_dir = get_custom_templates_dir()
    return [
        d for d in sorted(custom_dir.iterdir())
        if d.is_dir() and (d / "template.json").exists()
    ]