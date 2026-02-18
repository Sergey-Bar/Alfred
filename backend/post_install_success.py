#!/usr/bin/env python3
"""
[AI GENERATED]
Model: GitHub Copilot (GPT-5 mini)
Logic: Adds a small CLI post-install animation that shows an animated progress bar then a success checkmark/banner.
Why: Provide a friendly, visible completion UX after users finish installing or running setup steps.
Root Cause: Installers and quickstart flows often feel dry; a brief celebratory UX improves first-run experience.
Context: Lightweight, dependency-free fallback using ANSI escapes. If `colorama` is installed it will be used on Windows for reliable color output.
Model Suitability: GPT-5 mini is appropriate for small utility scripts and UX copy; for advanced cross-platform installers consider a dedicated packaging tool.
"""

import sys
import time
import shutil
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel

console = Console()

try:
    # colorama is optional but makes colors reliable on Windows
    from colorama import init as _colorama_init, Fore, Style

    _colorama_init()
    _HAS_COLORAMA = True
except Exception:
    _HAS_COLORAMA = False

    class Fore:
        GREEN = "\033[32m"
        CYAN = "\033[36m"
        RESET = "\033[0m"

    class Style:
        BRIGHT = "\033[1m"
        RESET_ALL = "\033[0m"


def rich_progress_bar(duration=2.0):
    """Enhanced progress bar using rich."""
    total_steps = 100
    with Progress() as progress:
        task = progress.add_task("[cyan]Installing ALFRED...", total=total_steps)
        for _ in range(total_steps):
            progress.update(task, advance=1)
            time.sleep(duration / total_steps)


def rich_success_banner():
    """Enhanced success banner using rich."""
    banner = """
    █████╗ ██╗     ███████╗██████╗ ███████╗██████╗        
   ██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝██╔══██╗       
   ███████║██║     █████╗  ██████╔╝█████╗  ██║  ██║       
   ██╔══██║██║     ██╔══╝  ██╔══██╗██╔══╝  ██║  ██║       
   ██║  ██║███████╗██║     ██║  ██║███████╗██████╔╝       
   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═════╝        
   ██╗███████╗     █████╗ ██╗     ██╗██╗   ██╗███████╗██╗ 
   ██║██╔════╝    ██╔══██╗██║     ██║██║   ██║██╔════╝██║ 
   ██║███████╗    ███████║██║     ██║██║   ██║█████╗  ██║ 
   ██║╚════██║    ██╔══██║██║     ██║╚██╗ ██╔╝██╔══╝  ╚═╝ 
   ██║███████║    ██║  ██║███████╗██║ ╚████╔╝ ███████╗██╗ 
   ╚═╝╚══════╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝  ╚══════╝╚═╝ 
    """
    console.print(
        Panel(
            banner,
            title="[green]✔ Installation Complete!",
            subtitle="[cyan]Next Steps:",
            expand=False,
        )
    )
    console.print("[bold green] - Start the server: [cyan]uvicorn app.main:app --reload")
    console.print("[bold green] - Visit the dashboard: [cyan]https://alfred.ai")


def main():
    try:
        rich_progress_bar(duration=2.0)
        rich_success_banner()
    except KeyboardInterrupt:
        console.print("[red]\nAborted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
