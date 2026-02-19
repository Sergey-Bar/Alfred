#!/usr/bin/env python3
"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Alfred CLI tool for developers and automation.
             Provides command-line access to all Alfred features.
Root Cause:  Sprint task T187 — CLI tool for developers.
Context:     Enables CI/CD integration and terminal workflows.
Suitability: L2 — Standard CLI patterns with click.
──────────────────────────────────────────────────────────────
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

console = Console()

# Configuration
DEFAULT_API_URL = "http://localhost:8000"
CONFIG_FILE = os.path.expanduser("~/.alfred/config.json")


def get_config() -> dict:
    """Load configuration from file or environment."""
    config = {
        "api_url": os.environ.get("ALFRED_API_URL", DEFAULT_API_URL),
        "api_key": os.environ.get("ALFRED_API_KEY", ""),
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception:
            pass
    
    return config


def save_config(config: dict) -> None:
    """Save configuration to file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_client() -> httpx.Client:
    """Create an HTTP client with auth headers."""
    config = get_config()
    if not config.get("api_key"):
        console.print("[red]Error: API key not configured. Run 'alfred configure' first.[/red]")
        sys.exit(1)
    
    return httpx.Client(
        base_url=config["api_url"],
        headers={
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "User-Agent": "alfred-cli/1.0.0",
        },
        timeout=60.0,
    )


def handle_error(response: httpx.Response) -> None:
    """Handle API errors."""
    try:
        data = response.json()
        message = data.get("detail", data.get("message", "Unknown error"))
    except Exception:
        message = response.text
    
    console.print(f"[red]Error ({response.status_code}): {message}[/red]")
    sys.exit(1)


# ============================================================
# Main CLI Group
# ============================================================

@click.group()
@click.version_option(version="1.0.0", prog_name="alfred")
def cli():
    """Alfred AI Credit Governance Platform CLI
    
    Manage AI credits, run completions, and monitor usage from the command line.
    """
    pass


# ============================================================
# Configuration Commands
# ============================================================

@cli.command()
@click.option("--api-key", prompt="API Key", help="Your Alfred API key")
@click.option("--api-url", default=DEFAULT_API_URL, help="Alfred API URL")
def configure(api_key: str, api_url: str):
    """Configure Alfred CLI with your credentials."""
    config = {
        "api_key": api_key,
        "api_url": api_url,
    }
    save_config(config)
    console.print("[green]Configuration saved to ~/.alfred/config.json[/green]")


@cli.command()
def whoami():
    """Show current user information."""
    with get_client() as client:
        response = client.get("/v1/users/me")
        if response.status_code != 200:
            handle_error(response)
        
        user = response.json()
        console.print(Panel(
            f"[bold]Name:[/bold] {user.get('name', 'N/A')}\n"
            f"[bold]Email:[/bold] {user.get('email', 'N/A')}\n"
            f"[bold]Role:[/bold] {user.get('role', 'user')}\n"
            f"[bold]ID:[/bold] {user.get('id', 'N/A')}",
            title="Current User"
        ))


# ============================================================
# Wallet Commands
# ============================================================

@cli.group()
def wallet():
    """Manage your credit wallet."""
    pass


@wallet.command("balance")
def wallet_balance():
    """Check your wallet balance."""
    with get_client() as client:
        response = client.get("/v1/wallets/me")
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        balance = float(data.get("balance", 0))
        soft_limit = float(data.get("soft_limit", 0))
        hard_limit = float(data.get("hard_limit", 0))
        
        # Color based on remaining balance
        color = "green" if balance > soft_limit * 0.5 else ("yellow" if balance > 0 else "red")
        
        console.print(Panel(
            f"[{color}]Balance: ${balance:.4f}[/{color}]\n"
            f"Soft Limit: ${soft_limit:.2f}\n"
            f"Hard Limit: ${hard_limit:.2f}",
            title="Wallet Balance"
        ))


@wallet.command("transactions")
@click.option("--limit", "-n", default=10, help="Number of transactions to show")
def wallet_transactions(limit: int):
    """List recent transactions."""
    with get_client() as client:
        response = client.get("/v1/wallets/me/transactions", params={"page_size": limit})
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        
        table = Table(title="Recent Transactions")
        table.add_column("Type", style="cyan")
        table.add_column("Amount", justify="right")
        table.add_column("Balance After", justify="right")
        table.add_column("Timestamp")
        table.add_column("Description")
        
        for tx in items[:limit]:
            amount = float(tx.get("amount", 0))
            color = "green" if amount > 0 else "red"
            table.add_row(
                tx.get("type", ""),
                f"[{color}]${amount:+.4f}[/{color}]",
                f"${float(tx.get('balance_after', 0)):.4f}",
                tx.get("created_at", "")[:19],
                tx.get("description", "")[:30],
            )
        
        console.print(table)


# ============================================================
# Completion Commands
# ============================================================

@cli.command()
@click.argument("prompt")
@click.option("--model", "-m", default="gpt-4o", help="Model to use")
@click.option("--temperature", "-t", default=0.7, type=float, help="Sampling temperature")
@click.option("--max-tokens", "-n", default=None, type=int, help="Maximum tokens")
@click.option("--system", "-s", default=None, help="System message")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
def chat(prompt: str, model: str, temperature: float, max_tokens: Optional[int], system: Optional[str], as_json: bool):
    """Send a chat completion request.
    
    Example: alfred chat "What is the capital of France?"
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
    with get_client() as client:
        with Progress() as progress:
            task = progress.add_task("Generating...", total=None)
            response = client.post("/v1/chat/completions", json=payload)
            progress.update(task, completed=True)
        
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        
        if as_json:
            console.print_json(json.dumps(data, indent=2))
            return
        
        # Pretty output
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        cost = data.get("cost")
        
        console.print(Panel(content, title=f"Response ({model})"))
        
        stats = f"Tokens: {usage.get('total_tokens', 0)} (in: {usage.get('prompt_tokens', 0)}, out: {usage.get('completion_tokens', 0)})"
        if cost:
            stats += f" | Cost: ${cost:.4f}"
        console.print(f"[dim]{stats}[/dim]")


@cli.command()
@click.argument("input_file", type=click.File("r"))
@click.option("--model", "-m", default="gpt-4o", help="Model to use")
@click.option("--output", "-o", type=click.File("w"), help="Output file")
def batch(input_file, model: str, output):
    """Process a batch of prompts from a file.
    
    Input file should have one prompt per line.
    """
    prompts = [line.strip() for line in input_file if line.strip()]
    
    if not prompts:
        console.print("[red]No prompts found in input file[/red]")
        return
    
    results = []
    
    with get_client() as client:
        with Progress() as progress:
            task = progress.add_task("Processing...", total=len(prompts))
            
            for prompt in prompts:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                }
                
                response = client.post("/v1/chat/completions", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    results.append({
                        "prompt": prompt,
                        "response": content,
                        "tokens": data.get("usage", {}).get("total_tokens", 0),
                        "cost": data.get("cost"),
                    })
                else:
                    results.append({
                        "prompt": prompt,
                        "error": response.text,
                    })
                
                progress.advance(task)
    
    if output:
        json.dump(results, output, indent=2)
        console.print(f"[green]Results saved to {output.name}[/green]")
    else:
        for r in results:
            console.print(Panel(r.get("response", r.get("error", "")), title=r["prompt"][:50]))


# ============================================================
# Analytics Commands
# ============================================================

@cli.group()
def analytics():
    """View usage analytics."""
    pass


@analytics.command("usage")
@click.option("--start", help="Start date (YYYY-MM-DD)")
@click.option("--end", help="End date (YYYY-MM-DD)")
def analytics_usage(start: Optional[str], end: Optional[str]):
    """Show usage report."""
    params = {}
    if start:
        params["start_date"] = start
    if end:
        params["end_date"] = end
    
    with get_client() as client:
        response = client.get("/v1/analytics/usage/me", params=params)
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        
        console.print(Panel(
            f"[bold]Total Requests:[/bold] {data.get('total_requests', 0):,}\n"
            f"[bold]Total Tokens:[/bold] {data.get('total_tokens_input', 0) + data.get('total_tokens_output', 0):,}\n"
            f"[bold]Total Cost:[/bold] ${float(data.get('total_cost', 0)):.2f}",
            title="Usage Summary"
        ))
        
        # By model breakdown
        by_model = data.get("by_model", [])
        if by_model:
            table = Table(title="By Model")
            table.add_column("Model")
            table.add_column("Requests", justify="right")
            table.add_column("Tokens", justify="right")
            table.add_column("Cost", justify="right")
            
            for m in by_model:
                table.add_row(
                    m.get("model", ""),
                    f"{m.get('requests', 0):,}",
                    f"{m.get('tokens', 0):,}",
                    f"${float(m.get('cost', 0)):.2f}",
                )
            
            console.print(table)


@analytics.command("export")
@click.option("--format", "fmt", type=click.Choice(["csv", "json"]), default="csv")
@click.option("--output", "-o", required=True, help="Output file path")
def analytics_export(fmt: str, output: str):
    """Export usage data."""
    with get_client() as client:
        response = client.get("/v1/analytics/usage/me")
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        
        if fmt == "json":
            with open(output, "w") as f:
                json.dump(data, f, indent=2)
        else:  # csv
            import csv
            with open(output, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Model", "Requests", "Tokens", "Cost"])
                for m in data.get("by_model", []):
                    writer.writerow([
                        m.get("model", ""),
                        m.get("requests", 0),
                        m.get("tokens", 0),
                        m.get("cost", 0),
                    ])
        
        console.print(f"[green]Exported to {output}[/green]")


# ============================================================
# Transfer Commands
# ============================================================

@cli.group()
def transfer():
    """Manage credit transfers."""
    pass


@transfer.command("send")
@click.argument("to_user_id")
@click.argument("amount", type=float)
@click.option("--message", "-m", help="Transfer message")
def transfer_send(to_user_id: str, amount: float, message: Optional[str]):
    """Send credits to another user."""
    with get_client() as client:
        payload = {
            "to_user_id": to_user_id,
            "amount": amount,
        }
        if message:
            payload["message"] = message
        
        response = client.post("/v1/transfers", json=payload)
        if response.status_code not in (200, 201):
            handle_error(response)
        
        console.print(f"[green]Successfully transferred ${amount:.2f} to {to_user_id}[/green]")


@transfer.command("list")
@click.option("--limit", "-n", default=10, help="Number of transfers to show")
def transfer_list(limit: int):
    """List recent transfers."""
    with get_client() as client:
        response = client.get("/v1/transfers", params={"page_size": limit})
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        
        table = Table(title="Recent Transfers")
        table.add_column("Type", style="cyan")
        table.add_column("Amount", justify="right")
        table.add_column("With", style="dim")
        table.add_column("Status")
        table.add_column("Timestamp")
        
        for t in items[:limit]:
            color = "red" if t.get("type") == "sent" else "green"
            table.add_row(
                t.get("type", "").upper(),
                f"[{color}]${float(t.get('amount', 0)):.2f}[/{color}]",
                str(t.get("other_user", {}).get("email", ""))[:30],
                t.get("status", ""),
                t.get("created_at", "")[:19],
            )
        
        console.print(table)


# ============================================================
# API Key Commands
# ============================================================

@cli.group()
def keys():
    """Manage API keys."""
    pass


@keys.command("list")
def keys_list():
    """List your API keys."""
    with get_client() as client:
        response = client.get("/v1/api-keys")
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        
        table = Table(title="API Keys")
        table.add_column("Name")
        table.add_column("Prefix")
        table.add_column("Created")
        table.add_column("Last Used")
        table.add_column("Status")
        
        for key in items:
            status = "[green]Active[/green]" if key.get("is_active") else "[red]Revoked[/red]"
            table.add_row(
                key.get("name", ""),
                key.get("key_prefix", "")[:8] + "...",
                key.get("created_at", "")[:10],
                (key.get("last_used_at") or "Never")[:10],
                status,
            )
        
        console.print(table)


@keys.command("create")
@click.argument("name")
@click.option("--scopes", "-s", multiple=True, help="Key scopes")
@click.option("--expires", type=int, help="Expiration in days")
def keys_create(name: str, scopes: tuple, expires: Optional[int]):
    """Create a new API key."""
    with get_client() as client:
        payload = {
            "name": name,
            "scopes": list(scopes) or [],
        }
        if expires:
            payload["expires_in_days"] = expires
        
        response = client.post("/v1/api-keys", json=payload)
        if response.status_code not in (200, 201):
            handle_error(response)
        
        data = response.json()
        console.print(Panel(
            f"[bold green]API Key Created[/bold green]\n\n"
            f"[bold]Key:[/bold] {data.get('key', 'N/A')}\n\n"
            f"[yellow]⚠️  Save this key now — you won't be able to see it again![/yellow]",
            title="New API Key"
        ))


@keys.command("revoke")
@click.argument("key_id")
@click.confirmation_option(prompt="Are you sure you want to revoke this key?")
def keys_revoke(key_id: str):
    """Revoke an API key."""
    with get_client() as client:
        response = client.delete(f"/v1/api-keys/{key_id}")
        if response.status_code not in (200, 204):
            handle_error(response)
        
        console.print(f"[green]API key {key_id} revoked[/green]")


# ============================================================
# Provider Commands
# ============================================================

@cli.command()
def providers():
    """List available LLM providers and health status."""
    with get_client() as client:
        response = client.get("/v1/providers")
        if response.status_code != 200:
            handle_error(response)
        
        data = response.json()
        items = data.get("items", data) if isinstance(data, dict) else data
        
        table = Table(title="LLM Providers")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Models")
        
        for p in items:
            status = p.get("health_status", "unknown")
            status_color = "green" if status == "healthy" else ("yellow" if status == "degraded" else "red")
            models = ", ".join(p.get("models", [])[:3])
            if len(p.get("models", [])) > 3:
                models += f" +{len(p['models']) - 3} more"
            
            table.add_row(
                p.get("name", ""),
                p.get("type", ""),
                f"[{status_color}]{status}[/{status_color}]",
                models,
            )
        
        console.print(table)


if __name__ == "__main__":
    cli()
