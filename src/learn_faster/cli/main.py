#!/usr/bin/env python3
"""
Learn FASTER CLI - One-time installer for Claude Code learning system.

Usage:
    uvx learn-faster init
"""

import sys
import shutil
import platform
import inquirer
import json
from pathlib import Path
from typing import Dict, Any


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


BANNER = f"""{Colors.CYAN}
██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗    ███████╗ █████╗ ███████╗████████╗███████╗██████╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
██║     █████╗  ███████║██████╔╝██╔██╗ ██║    █████╗  ███████║███████╗   ██║   █████╗  ██████╔╝
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║    ██╔══╝  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗
███████╗███████╗██║  ██║██║  ██║██║ ╚████║    ██║     ██║  ██║███████║   ██║   ███████╗██║  ██║
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{Colors.RESET}"""


def print_success(msg: str) -> None:
    """Print success message in green."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")


def print_info(msg: str) -> None:
    """Print info message in cyan."""
    print(f"{Colors.CYAN}{msg}{Colors.RESET}")


def print_warning(msg: str) -> None:
    """Print warning message in yellow."""
    print(f"{Colors.YELLOW}!{Colors.RESET} {msg}")


def print_header(msg: str) -> None:
    """Print header message in bold magenta."""
    print(f"{Colors.BOLD}{Colors.MAGENTA}{msg}{Colors.RESET}")


def print_dim(msg: str) -> None:
    """Print dimmed message."""
    print(f"{Colors.DIM}{msg}{Colors.RESET}")


def print_error(msg: str) -> None:
    """Print error message in red."""
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")


def get_templates_dir() -> Path:
    """Get the templates directory from the installed package."""
    return Path(__file__).parent.parent / "templates"


def create_or_update_settings(claude_dir: Path, learning_mode: str = "balanced") -> None:
    """Create or update .claude/settings.local.json."""
    settings_file = claude_dir / "settings.local.json"

    allow_list = [
        "Bash(python3 .learning/scripts/:*)",
        "Bash(ls:*)",
        "Read(.learning/**)",
        "Write(.learning/**)",
        "Write(**/*.md)",
        "Read(**/*.md)"
    ]
    if learning_mode == "reading":
        allow_list.extend([
            "mcp__pdf-mcp__*",
            "Read(./book.pdf)",
            "Read(./course.md)",
            "Read(./video.url)",
            "Bash(yt-dlp:*)",
            "Bash(which yt-dlp:*)"
        ])

    # Default settings for Learn FASTER
    default_settings = {
        "permissions": {
            "allow": allow_list,
            "deny": [
                "Bash(rm:*)",
                "Bash(curl:*)",
                "Read(.env)",
                "Read(.env.*)",
                "Write(.env)",
                "Write(.env.*)"
            ]
        },
        "companyAnnouncements": [
            "🚀 Learn FASTER активен! Используй /learn \"Тема\" чтобы начать обучение",
        ]
    }

    if settings_file.exists():
        # Load existing settings
        with open(settings_file, "r") as f:
            settings = json.load(f)

        # Merge with defaults
        if "permissions" not in settings:
            settings["permissions"] = default_settings["permissions"]
        else:
            # Merge permissions allow list
            if "allow" not in settings["permissions"]:
                settings["permissions"]["allow"] = []

            for perm in default_settings["permissions"]["allow"]:
                if perm not in settings["permissions"]["allow"]:
                    settings["permissions"]["allow"].append(perm)

            # Merge permissions deny list
            if "deny" not in settings["permissions"]:
                settings["permissions"]["deny"] = []

            for perm in default_settings["permissions"]["deny"]:
                if perm not in settings["permissions"]["deny"]:
                    settings["permissions"]["deny"].append(perm)

        # Add company announcements if not present
        if "companyAnnouncements" not in settings:
            settings["companyAnnouncements"] = default_settings["companyAnnouncements"]

        print_success(f"Updated {settings_file}")
    else:
        # Create new settings file
        settings = default_settings
        print_success(f"Created {settings_file}")

    # Write settings
    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=2)


def check_pdf_mcp_installed() -> None:
    """Check if pdf-mcp MCP server is configured in Claude Code.

    Informational only — never blocks init. Used for the 'reading' mode where
    book.pdf-based learning needs pdf-mcp tools (mcp__pdf-mcp__*).
    """
    import subprocess

    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        print_warning("Claude CLI не найден в PATH — проверка pdf-mcp пропущена.")
        return
    except subprocess.TimeoutExpired:
        print_warning("Таймаут при проверке MCP-серверов — пропускаю.")
        return
    except Exception as e:
        print_warning(f"Не удалось проверить MCP-серверы: {e}")
        return

    if result.returncode != 0:
        print_warning("Команда `claude mcp list` вернула ошибку — проверка pdf-mcp пропущена.")
        return

    if "pdf-mcp" in result.stdout.lower():
        print_success("pdf-mcp обнаружен в MCP-конфиге Claude Code")
        return

    print_warning("pdf-mcp MCP-сервер не найден в Claude Code.")
    print_dim("Нужен только для обучения по PDF-книгам. Для course.md или ручного ввода — не обязателен.")
    print_dim("Установка:")
    print(f"  {Colors.CYAN}pip install pdf-mcp{Colors.RESET}")
    print(f"  {Colors.CYAN}claude mcp add pdf-mcp -- pdf-mcp{Colors.RESET}")
    print()


def check_yt_dlp_installed() -> None:
    """Check if yt-dlp CLI is on PATH.

    Informational only — never blocks init. Used for the 'reading' mode where
    YouTube videos (video.url) need yt-dlp to download transcripts.
    """
    import subprocess
    from datetime import datetime, timedelta

    try:
        result = subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except FileNotFoundError:
        print_warning("yt-dlp не найден в PATH.")
        print_dim("Нужен только для обучения по YouTube-видео (video.url). Для course.md / book.pdf / ручного ввода — не обязателен.")
        print_dim("Установка:")
        print(f"  {Colors.CYAN}brew install yt-dlp{Colors.RESET}        # macOS")
        print(f"  {Colors.CYAN}uv tool install yt-dlp{Colors.RESET}     # cross-platform")
        print(f"  {Colors.CYAN}pipx install yt-dlp{Colors.RESET}        # alternative")
        print()
        return
    except subprocess.TimeoutExpired:
        print_warning("Таймаут при проверке yt-dlp — пропускаю.")
        return
    except Exception as e:
        print_warning(f"Не удалось проверить yt-dlp: {e}")
        return

    if result.returncode != 0:
        print_warning("Команда `yt-dlp --version` вернула ошибку — проверка пропущена.")
        return

    version = result.stdout.strip()
    print_success(f"yt-dlp найден (версия {version})")

    # Warn if older than 6 months — YouTube часто ломает старые версии
    try:
        version_date = datetime.strptime(version, "%Y.%m.%d")
        if datetime.now() - version_date > timedelta(days=180):
            print_warning(f"yt-dlp старше 6 месяцев — YouTube часто ломает старые версии. Обнови: `brew upgrade yt-dlp` или `uv tool upgrade yt-dlp`.")
    except ValueError:
        pass


def check_initialization() -> bool:
    """Check if project has been initialized."""
    config_path = Path.cwd() / ".learning" / "config.json"
    if not config_path.exists():
        return False

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("initialized", False)
    except:
        return False


def init_project() -> None:
    """Initialize Learn FASTER in the current project."""
    

    cwd = Path.cwd()
    templates_dir = get_templates_dir()

    print(BANNER)
    print_header("\nИнициализация Learn FASTER в текущем проекте...\n")

    # Ask for learning mode selection
    

    learning_mode_question = [
        inquirer.List(
            'mode',
            message="Выбери режим обучения",
            choices=[
                ('Сбалансированный — Микс теории, практики и применения', 'balanced'),
                ('Экзаменационный  — Печатные экзамены, тесты, подготовка к сертификации', 'exam'),
                ('Теоретический    — Глубокое концептуальное понимание', 'theory'),
                ('Практический     — Сразу строить проекты, учиться на деле', 'practical'),
                ('Программирование — Учиться через создание проектов', 'programming'),
                ('Изучение материала — Прохождение курса/книги шаг за шагом, конспекты, активное чтение', 'reading'),
            ],
            default='balanced',
        ),
    ]

    mode_answer = inquirer.prompt(learning_mode_question)
    learning_mode = mode_answer['mode'] if mode_answer else 'balanced'

    mode_names = {
        "exam": "Экзаменационный",
        "theory": "Теоретический",
        "practical": "Практический",
        "balanced": "Сбалансированный",
        "programming": "Программирование",
        "reading": "Изучение материала"
    }
    print_success(f"Выбрано: {mode_names[learning_mode]}\n")

    if learning_mode == "reading":
        check_pdf_mcp_installed()
        check_yt_dlp_installed()

    # Ask about macOS Reminders (only on macOS)
    macos_reminders = False
    if platform.system() == "Darwin":
        response = input(f"{Colors.CYAN}Включить напоминания macOS для повторений? (д/н):{Colors.RESET} ").strip().lower()
        macos_reminders = response in ['y', 'yes', 'д', 'да']

    # Create .claude directory structure
    claude_dir = cwd / ".claude"
    claude_dir.mkdir(exist_ok=True)

    # Copy mode-specific agents and commands
    mode_templates_dir = templates_dir / "modes" / learning_mode

    # Copy agents for selected mode
    agents_dest = claude_dir / "agents"
    agents_dest.mkdir(exist_ok=True)
    agents_src = mode_templates_dir / "agents"

    if agents_src.exists():
        for file in agents_src.glob("*.md"):
            shutil.copy2(file, agents_dest / file.name)
            print_success(f"Copied agent: {file.name}")

    # Copy commands for selected mode
    commands_dest = claude_dir / "commands"
    commands_dest.mkdir(exist_ok=True)
    commands_src = mode_templates_dir / "commands"

    if commands_src.exists():
        for file in commands_src.glob("*.md"):
            shutil.copy2(file, commands_dest / file.name)
            print_success(f"Copied command: {file.name}")

    # Create/update settings.local.json
    create_or_update_settings(claude_dir, learning_mode)

    # Create .learning directory structure
    learning_dir = cwd / ".learning"
    learning_dir.mkdir(exist_ok=True)

    # Create config.json with initialization flag
    config = {
        "initialized": True,
        "learning_mode": learning_mode,
        "macos_reminders_enabled": macos_reminders
    }
    config_path = learning_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print_success(f"Создан config.json (Режим: {mode_names[learning_mode]}, Напоминания macOS: {'вкл' if macos_reminders else 'выкл'})")

    # Copy scripts
    scripts_dest = learning_dir / "scripts"
    scripts_dest.mkdir(exist_ok=True)
    scripts_src = templates_dir / "scripts"
    if scripts_src.exists():
        for file in scripts_src.glob("*.py"):
            shutil.copy2(file, scripts_dest / file.name)
            print_success(f"Copied script: {file.name}")

    # Copy references
    references_dest = learning_dir / "references"
    references_dest.mkdir(exist_ok=True)
    references_src = templates_dir / "references"
    if references_src.exists():
        for file in references_src.glob("*.md"):
            shutil.copy2(file, references_dest / file.name)
            print_success(f"Copied reference: {file.name}")

    # Copy instructions.md to project root as CLAUDE.md
    instructions_src = templates_dir / "instructions.md"
    claude_md_dest = cwd / "CLAUDE.md"
    if instructions_src.exists() and not claude_md_dest.exists():
        shutil.copy2(instructions_src, claude_md_dest)
        print_success("Copied instructions to CLAUDE.md in project root")
    elif claude_md_dest.exists():
        print_warning("CLAUDE.md already exists, skipping")

    print(f"\n{Colors.GREEN}{Colors.BOLD}Инициализация завершена!{Colors.RESET}\n")

    print_header("Доступные команды в Claude Code:")
    print(f"  {Colors.CYAN}/learn [тема]{Colors.RESET}     — Начать или продолжить обучение")
    print(f"  {Colors.CYAN}/review{Colors.RESET}           — Сессия интервального повторения")
    print(f"  {Colors.CYAN}/progress{Colors.RESET}         — Подробный отчёт о прогрессе")
    print()


def launch_coach(auto_review: bool = False) -> None:
    """Launch Claude Code with learn-faster system prompt."""
    import subprocess

    # Get the learning mode from config
    config_path = Path.cwd() / ".learning" / "config.json"
    learning_mode = "balanced"  # default
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                learning_mode = config.get("learning_mode", "balanced")
        except:
            pass

    # Get the path to the system prompt template
    templates_dir = Path(__file__).parent.parent / "templates"
    system_prompt_path = templates_dir / "modes" / learning_mode / "system_prompts" / "learn-faster.md"

    if not system_prompt_path.exists():
        print_error(f"Ошибка: системный промпт для режима '{learning_mode}' не найден")
        print_dim(f"Ожидался по пути: {system_prompt_path}")
        sys.exit(1)

    # Read the system prompt content (skip frontmatter)
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Skip frontmatter (between --- lines)
    in_frontmatter = False
    content_lines = []
    for line in lines:
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                in_frontmatter = False
                continue
        if not in_frontmatter:
            content_lines.append(line)

    system_prompt = "".join(content_lines).strip()

    # Launch Claude Code with the system prompt
    print_info("Запуск Claude Code в режиме обучения...")
    print_dim("(Используется системный промпт FASTER)\n")

    # Build command with optional /review prefix
    cmd = ["claude", "--system-prompt", system_prompt]
    if auto_review:
        cmd.extend(["/review"])

    try:
        subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print_error("Ошибка: команда 'claude' не найдена")
        print_dim("Убедись, что Claude Code CLI установлен и доступен в PATH")
        print_dim("Установка: https://claude.ai/download")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    # Check for explicit commands
    if len(sys.argv) >= 2:
        command = sys.argv[1]

        if command == "init":
            init_project()
            return
        elif command == "version":
            from learn_faster import __version__
            print(f"learn-faster version {__version__}")
            return
        elif command in ["help", "--help", "-h"]:
            print("Learn FASTER — Ускоренное обучение с фреймворком FASTER\n")
            print("Использование:")
            print("  learn-faster           Авто-инициализация и запуск Claude Code в режиме обучения")
            print("  learn-faster init      Принудительная реинициализация")
            print("  learn-faster version   Показать версию")
            print()
            print("Подробнее: https://github.com/cheukyin175/learn-faster-kit")
            return
        else:
            print_error(f"Неизвестная команда: {command}")
            print_dim("Запусти 'learn-faster --help' для справки")
            sys.exit(1)

    # Default behavior: check init, then launch
    if not check_initialization():
        print_info("Первый запуск. Инициализация...")
        print()
        init_project()
        print()
        print_header("Запуск Claude Code с фреймворком FASTER...")
        print()
        launch_coach(auto_review=False)
    else:
        print_info("Запуск Claude Code в режиме обучения...")
        print_dim("(Начинаем с /review для проверки запланированных повторений)\n")
        launch_coach(auto_review=True)


if __name__ == "__main__":
    main()
