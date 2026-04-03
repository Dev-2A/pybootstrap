"""Rich 기반 콘솔 출력 모듈"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .config import BootstrapConfig
from .models import TemplateInfo, TemplateType
from .scaffolder import ScaffoldResult

console = Console()


# ─── create 명령어 출력 ──────────────────────────────────────

def display_creating(config: BootstrapConfig, template: TemplateInfo):
    """프로젝트 생성 시작 메시지"""
    console.print()
    console.print(
        Panel(
            f"[bold cyan]{config.project_name_kebab}[/bold cyan]\n"
            f"[dim]템플릿: {template.display_name}[/dim]",
            title="🐍 PyBootstrap",
            subtitle=f"v{_get_version()}",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    with console.status("[bold green]프로젝트를 생성하는 중...") as status:
        # 실제 생성은 cli.py에서 하므로, 여기서는 시작 표시만
        pass


def display_result(result: ScaffoldResult):
    """생성 결과 요약 패널"""
    git_status = "✅ 초기화 완료" if result.git_initialized else "⏭️ 건너뜀"

    console.print()
    console.print(
        Panel(
            f"[bold green]✅ 프로젝트 생성 완료![/bold green]\n\n"
            f"  📁 경로      [cyan]{result.project_dir}[/cyan]\n"
            f"  🎨 템플릿    {result.template_name}\n"
            f"  📄 파일      {result.file_count}개\n"
            f"  📂 디렉토리  {result.dir_count}개\n"
            f"  🔀 Git       {git_status}",
            border_style="green",
            padding=(1, 2),
        )
    )


def display_tree(result: ScaffoldResult):
    """생성된 파일 트리 표시"""
    tree = Tree(
        f"📁 [bold cyan]{result.project_dir.name}[/bold cyan]",
        guide_style="dim",
    )

    # 파일 목록을 트리 구조로 변환
    nodes: dict[str, Tree] = {}

    for file_path in sorted(result.created_files):
        parts = file_path.replace("\\", "/").split("/")
        current_node = tree

        for i, part in enumerate(parts):
            key = "/".join(parts[: i + 1])
            is_file = i == len(parts) - 1

            if key not in nodes:
                if is_file:
                    icon = _get_file_icon(part)
                    nodes[key] = current_node.add(f"{icon} {part}")
                else:
                    nodes[key] = current_node.add(
                        f"📂 [bold]{part}[/bold]"
                    )

            current_node = nodes[key]

    console.print()
    console.print(tree)


# ─── list 명령어 출력 ────────────────────────────────────────

def display_template_list(templates: list[TemplateInfo], title: str):
    """템플릿 목록 테이블"""
    table = Table(
        title=f"\n📋 {title}",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 1),
    )

    table.add_column("이름", style="bold", min_width=12)
    table.add_column("표시명", min_width=20)
    table.add_column("설명", min_width=30)
    table.add_column("파일", justify="center", min_width=6)
    table.add_column("의존성", justify="center", min_width=6)
    table.add_column("유형", justify="center", min_width=8)

    for tpl in templates:
        badge = "[green]내장[/green]" if tpl.template_type == TemplateType.BUILTIN else "[yellow]커스텀[/yellow]"
        table.add_row(
            tpl.name,
            tpl.display_name,
            tpl.description,
            str(len(tpl.all_files)),
            str(len(tpl.dependencies)),
            badge,
        )

    console.print(table)
    console.print()

    # 사용법 힌트
    console.print(
        "  💡 [dim]상세 정보:[/dim] bootstrap info [bold]<템플릿 이름>[/bold]"
    )
    console.print(
        "  💡 [dim]프로젝트 생성:[/dim] bootstrap create [bold]<프로젝트명>[/bold] -t [bold]<템플릿>[/bold]"
    )
    console.print()


# ─── info 명령어 출력 ────────────────────────────────────────

def display_template_info(template: TemplateInfo):
    """템플릿 상세 정보"""
    badge = "📦 내장" if template.template_type == TemplateType.BUILTIN else "🔧 커스텀"

    console.print()
    console.print(
        Panel(
            f"[bold]{template.display_name}[/bold]\n"
            f"[dim]{template.description}[/dim]\n\n"
            f"  이름  [cyan]{template.name}[/cyan]\n"
            f"  유형  {badge}",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    # 생성 파일 목록
    file_tree = Tree("📂 [bold]생성 파일[/bold]", guide_style="dim")
    for entry in template.all_files:
        cond = f" [dim](조건: {entry.condition})[/dim]" if entry.condition else ""
        icon = _get_file_icon(entry.destination.split("/")[-1])
        file_tree.add(f"{icon} {entry.destination}{cond}")

    console.print(file_tree)

    # 의존성
    if template.dependencies:
        console.print()
        dep_text = Text("📦 의존성: ", style="bold")
        dep_text.append(", ".join(template.dependencies), style="cyan")
        console.print(dep_text)

    if template.dev_dependencies:
        dev_text = Text("🔧 개발 의존성: ", style="bold")
        dev_text.append(", ".join(template.dev_dependencies), style="yellow")
        console.print(dev_text)

    # 사용 예시
    console.print()
    console.print(
        Panel(
            f"[bold]bootstrap create my-project -t {template.name}[/bold]",
            title="사용 예시",
            border_style="green",
            padding=(0, 2),
        )
    )
    console.print()


# ─── 유틸리티 ────────────────────────────────────────────────

def _get_file_icon(filename: str) -> str:
    """파일 확장자에 따른 아이콘 반환"""
    icons = {
        ".py": "🐍",
        ".toml": "⚙️",
        ".txt": "📄",
        ".md": "📝",
        ".yml": "📋",
        ".yaml": "📋",
        ".json": "📊",
        ".js": "🟨",
        ".jsx": "⚛️",
        ".ts": "🔷",
        ".tsx": "⚛️",
        ".html": "🌐",
        ".css": "🎨",
        ".gitignore": "🙈",
        "Dockerfile": "🐳",
        "LICENSE": "📜",
    }

    if filename == "Dockerfile":
        return "🐳"
    if filename == ".gitignore":
        return "🙈"

    for ext, icon in icons.items():
        if filename.endswith(ext):
            return icon

    return "📄"


def _get_version() -> str:
    """패키지 버전 반환"""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "0.1.0"