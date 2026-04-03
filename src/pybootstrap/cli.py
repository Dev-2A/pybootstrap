"""PyBootstrap CLJI - Click 기반 커맨드라인 인터페이스"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__
from .config import BootstrapConfig
from .registry import get_registry
from .scaffolder import ScaffoldError, Scaffolder


@click.group()
@click.version_option(version=__version__, prog_name="pybootstrap")
def main():
    """🐍 PyBootstrap — Python 프로젝트 부트스트래퍼 CLI

    한 줄 명령어로 Python 프로젝트 스캐폴딩을 자동화합니다.

    \b
    예시:
      bootstrap create my-api --template fastapi
      bootstrap create my-tool --template cli
      bootstrap list
    """
    pass


# ─── create ──────────────────────────────────────────────────

@main.command()
@click.argument("project_name")
@click.option(
    "-t", "--template",
    "template_name",
    default="fastapi",
    help="사용할 템플릿 (기본: fastapi)",
)
@click.option(
    "-d", "--description",
    default="",
    help="프로젝트 설명",
)
@click.option(
    "-a", "--author",
    default="",
    help="작성자 이름",
)
@click.option(
    "--python-version",
    default="3.11",
    help="Python 버전 (기본: 3.11)",
)
@click.option(
    "--no-docker",
    is_flag=True,
    default=False,
    help="Dockerfile 생성 건너뛰기",
)
@click.option(
    "--no-git",
    is_flag=True,
    default=False,
    help="git init 건너뛰기",
)
@click.option(
    "-o", "--output",
    "output_dir",
    default=".",
    help="프로젝트를 생성할 상위 디렉토리 (기본: 현재 디렉토리)",
)
def create(
    project_name: str,
    template_name: str,
    description: str,
    author: str,
    python_version: str,
    no_docker: bool,
    no_git: bool,
    output_dir: str,
):
    """새 Python 프로젝트를 생성합니다.
    
    PROJECT_NAME: 생성할 프로젝트 이름 (예: my-api, my-tool)
    """
    # 레지스트리에서 템플릿 조회
    registry = get_registry()
    template = registry.get(template_name)
    
    if template is None:
        available = ", ".join(t.name for t in registry.list_all())
        click.echo(f"❌ 템플릿 '{template_name}'을 찾을 수 없습니다.", err=True)
        click.echo(f"   사용 가능한 템플릿: {available}", err=True)
        sys.exit(1)
    
    # 설정 구성
    config = BootstrapConfig(
        project_name=project_name,
        template_name=template_name,
        author=author,
        description=description,
        python_version=python_version,
        use_docker=not no_docker,
        use_git=not no_git,
    )
    
    # Rich 사용 가능하면 Rich 출력, 아니면 기본 출력
    try:
        from .display import display_creating, display_result, display_tree
        use_rich = True
    except ImportError:
        use_rich = False
    
    if use_rich:
        display_creating(config, template)
    else:
        click.echo(f"🐍 프로젝트 생성 중: {project_name}")
        click.echo(f"   템플릿: {template.display_name}")
    
    # 스캐폴딩 실행
    try:
        scaffolder = Scaffolder(config, template)
        result = scaffolder.scaffold(Path(output_dir))
    except ScaffoldError as e:
        click.echo(f"\n❌ {e}", err=True)
        sys.exit(1)
    
    # 결과 출력
    if use_rich:
        display_result(result)
        display_tree(result)
    else:
        click.echo(f"\n✅ {result.summary()}")
        click.echo(f"\n📂 생성된 파일 ({result.file_count}개):")
        for f in result.created_files:
            click.echo(f"   {f}")
    
    # 다음 단계 안내
    click.echo("")
    click.echo("🚀 시작하기:")
    click.echo(f"   cd {config.project_name_kebab}")
    
    if template_name == "fastapi":
        click.echo("   python -m venv .venv")
        click.echo("   .venv\\Scripts\\activate")
        click.echo("   pip install -r requirements.txt")
        click.echo("   uvicorn src.{}.main:app --reload".format(config.project_slug))
    elif template_name == "cli":
        click.echo("   python -m venv .venv")
        click.echo("   .venv\\Scripts\\activate")
        click.echo("   pip install -e .")
        click.echo(f"   {config.project_slug} --help")
    elif template_name == "fullstack":
        click.echo("   # 백엔드")
        click.echo("   cd backend && python -m venv .venv && .venv\\Scripts\\activate")
        click.echo("   pip install -r requirements.txt && uvicorn main:app --reload")
        click.echo("   # 프론트엔드 (새 터미널)")
        click.echo("   cd frontend && npm install && npm run dev")


# ─── list ────────────────────────────────────────────────────

@main.command("list")
@click.option(
    "--builtin", "filter_type",
    flag_value="builtin",
    help="내장 템플릿만 표시",
)
@click.option(
    "--custom", "filter_type",
    flag_value="custom",
    help="커스텀 템플릿만 표시",
)
def list_templates(filter_type: str | None):
    """사용 가능한 템플릿 목록을 표시합니다."""
    registry = get_registry()

    if filter_type == "builtin":
        templates = registry.list_builtin()
        title = "내장 템플릿"
    elif filter_type == "custom":
        templates = registry.list_custom()
        title = "커스텀 템플릿"
    else:
        templates = registry.list_all()
        title = "전체 템플릿"

    if not templates:
        click.echo(f"ℹ️  등록된 {title}이 없습니다.")
        return

    try:
        from .display import display_template_list
        display_template_list(templates, title)
    except ImportError:
        click.echo(f"\n📋 {title} ({len(templates)}개)\n")
        for tpl in templates:
            badge = "📦" if tpl.template_type.value == "builtin" else "🔧"
            click.echo(f"  {badge} {tpl.name}")
            click.echo(f"     {tpl.display_name} — {tpl.description}")
            click.echo(f"     파일 {len(tpl.all_files)}개 · 의존성 {len(tpl.dependencies)}개")
            click.echo("")


# ─── info ────────────────────────────────────────────────────

@main.command()
@click.argument("template_name")
def info(template_name: str):
    """특정 템플릿의 상세 정보를 표시합니다.

    TEMPLATE_NAME: 조회할 템플릿 이름 (예: fastapi, cli, fullstack)
    """
    registry = get_registry()
    template = registry.get(template_name)

    if template is None:
        available = ", ".join(t.name for t in registry.list_all())
        click.echo(f"❌ 템플릿 '{template_name}'을 찾을 수 없습니다.", err=True)
        click.echo(f"   사용 가능한 템플릿: {available}", err=True)
        sys.exit(1)

    try:
        from .display import display_template_info
        display_template_info(template)
    except ImportError:
        click.echo(f"\n{template.display_name}")
        click.echo(f"  이름: {template.name}")
        click.echo(f"  설명: {template.description}")
        click.echo(f"  유형: {template.template_type.value}")
        click.echo(f"\n  📂 생성 파일 ({len(template.all_files)}개):")
        for f in template.all_files:
            cond = f" (조건: {f.condition})" if f.condition else ""
            click.echo(f"    → {f.destination}{cond}")
        click.echo(f"\n  📦 의존성 ({len(template.dependencies)}개):")
        for dep in template.dependencies:
            click.echo(f"    {dep}")
        if template.dev_dependencies:
            click.echo(f"\n  🔧 개발 의존성 ({len(template.dev_dependencies)}개):")
            for dep in template.dev_dependencies:
                click.echo(f"    {dep}")


# ─── init-template ───────────────────────────────────────────

@main.command("init-template")
@click.argument("name")
@click.option("-d", "--description", default="", help="템플릿 설명")
@click.option("--display-name", default="", help="표시 이름")
def init_template(name: str, description: str, display_name: str):
    """빈 커스텀 템플릿 스켈레톤을 생성합니다.

    NAME: 템플릿 이름 (예: flask, django)
    """
    from .custom import CustomTemplateError, init_custom_template

    try:
        template_dir = init_custom_template(
            name=name,
            display_name=display_name,
            description=description,
        )
    except CustomTemplateError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)

    click.echo(f"✅ 커스텀 템플릿 '{name}' 스켈레톤 생성 완료!")
    click.echo(f"   📁 경로: {template_dir}")
    click.echo("")
    click.echo("   다음 단계:")
    click.echo(f"   1. {template_dir} 안의 .j2 파일들을 수정하세요")
    click.echo(f"   2. template.json에서 파일 목록과 의존성을 편집하세요")
    click.echo(f"   3. bootstrap create my-project -t {name}")


# ─── import ──────────────────────────────────────────────────

@main.command("import")
@click.argument("source_dir", type=click.Path(exists=True))
@click.argument("name")
@click.option("-d", "--description", default="", help="템플릿 설명")
@click.option("--display-name", default="", help="표시 이름")
def import_template(source_dir: str, name: str, description: str, display_name: str):
    """기존 프로젝트 디렉토리를 커스텀 템플릿으로 변환합니다.

    \b
    SOURCE_DIR: 소스 프로젝트 디렉토리 경로
    NAME: 생성할 템플릿 이름
    """
    from pathlib import Path as _Path

    from .custom import CustomTemplateError, import_as_template

    try:
        template_dir = import_as_template(
            source_dir=_Path(source_dir),
            name=name,
            display_name=display_name,
            description=description,
        )
    except CustomTemplateError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)

    click.echo(f"✅ 프로젝트를 커스텀 템플릿 '{name}'으로 변환 완료!")
    click.echo(f"   📁 경로: {template_dir}")
    click.echo("")
    click.echo("   다음 단계:")
    click.echo(f"   1. {template_dir / 'template.json'}을 확인하세요")
    click.echo("   2. .j2 파일에 {{ project_name }} 등 변수를 추가하세요")
    click.echo(f"   3. bootstrap create my-project -t {name}")


# ─── remove-template ─────────────────────────────────────────

@main.command("remove-template")
@click.argument("name")
@click.confirmation_option(prompt="정말 삭제하시겠습니까?")
def remove_template(name: str):
    """커스텀 템플릿을 삭제합니다.

    NAME: 삭제할 커스텀 템플릿 이름
    """
    from .custom import delete_custom_template
    from .registry import get_registry

    # 내장 템플릿은 삭제 불가
    registry = get_registry()
    template = registry.get(name)
    if template and template.template_type.value == "builtin":
        click.echo(f"❌ 내장 템플릿 '{name}'은 삭제할 수 없습니다.", err=True)
        sys.exit(1)

    if delete_custom_template(name):
        click.echo(f"🗑️  커스텀 템플릿 '{name}'을 삭제했습니다.")
    else:
        click.echo(f"❌ 커스텀 템플릿 '{name}'을 찾을 수 없습니다.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()