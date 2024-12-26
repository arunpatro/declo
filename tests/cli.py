"""CLI tool to display and test Declo examples."""
import json
from pathlib import Path
import ast
import traceback

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt
from rich.columns import Columns
from rich.progress import track
from declo.compiler import compile_declo_to_python
from declo.decompiler import compile_python_to_declo

app = typer.Typer(no_args_is_help=True)  # Show help by default if no args provided
console = Console()

def load_examples() -> list[dict]:
    """Load examples from JSON file."""
    json_path = Path(__file__).parent / "test_examples.json"
    with open(json_path) as f:
        data = json.load(f)
    return data["examples"]

def display_example(example: dict) -> None:
    """Display a single example with syntax highlighting."""
    console.print()
    console.print(f"[bold cyan]Example:[/bold cyan] {example['title']}")
    
    # Create panels for both Declo and Python code
    declo_syntax = Syntax(example["declo"], "python", theme="monokai", line_numbers=True)
    python_syntax = Syntax(example["python"], "python", theme="monokai", line_numbers=True)
    
    declo_panel = Panel(declo_syntax, title="[bold green]Declo Code[/bold green]", padding=(1, 1))
    python_panel = Panel(python_syntax, title="[bold blue]Python Code[/bold blue]", padding=(1, 1))
    
    # Display panels side by side using Columns with auto-width
    console.print(Columns([declo_panel, python_panel], padding=1, expand=False))

def display_examples_table(examples: list[dict]) -> None:
    """Display all examples in a table format."""
    table = Table(title="Declo Examples")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title", style="green")
    
    for idx, example in enumerate(examples, 1):
        table.add_row(str(idx), example["title"])
    
    console.print(table)

def display_code(code: str, title: str, language: str = "python") -> None:
    """Display code with syntax highlighting in a panel."""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=title))

def inspect_ast(code: str) -> str:
    """Return a string representation of the AST for debugging."""
    try:
        tree = ast.parse(code)
        return ast.dump(tree, indent=2)
    except Exception as e:
        return f"Failed to parse AST: {str(e)}"

@app.command()
def list():
    """List all available examples."""
    examples = load_examples()
    display_examples_table(examples)

@app.command()
def test(example_id: int = typer.Argument(None, help="ID of the example to test")):
    """Test a specific example or all examples. If example_id is provided, test only that example."""
    examples = load_examples()
    
    if example_id is not None:
        if 1 <= example_id <= len(examples):
            example = examples[example_id - 1]
            display_example(example)
            test_example(example)
        else:
            console.print(f"[red]Invalid example ID. Please enter a number between 1 and {len(examples)}[/red]")
        return
    
    for i, example in enumerate(examples, 1):
        console.print(f"[bold cyan]Example {i}:[/bold cyan]")
        display_example(example)
        test_example(example)

def test_example(example: dict) -> None:
    """Test a single example's compilation and decompilation."""
    try:
        # Test compilation (Declo -> Python)
        console.print("\n[bold]Testing Steps:[/bold]")
        
        # Compilation test
        try:
            compiled = compile_declo_to_python(example["declo"])
            console.print("[green]✓[/green] Compilation successful")
            display_code(compiled, "[green]Compiled Python[/green]")
        except Exception as e:
            console.print("[red]✗[/red] Compilation failed")
            console.print("[red]Error:[/red]", str(e))
            console.print("[dim]" + "\n".join(traceback.format_exc().split("\n")[1:]) + "[/dim]")
            return
        
        # Decompilation test
        try:
            decompiled = compile_python_to_declo(example["python"])
            console.print("[green]✓[/green] Decompilation successful")
            display_code(decompiled, "[green]Decompiled Declo[/green]")
        except Exception as e:
            console.print("[red]✗[/red] Decompilation failed")
            console.print("[red]Error:[/red]", str(e))
            console.print("[dim]" + "\n".join(traceback.format_exc().split("\n")[1:]) + "[/dim]")
            return
        
        # Roundtrip test
        try:
            roundtrip = compile_python_to_declo(compile_declo_to_python(example["declo"]))
            if roundtrip.strip() == example["declo"].strip():
                console.print("[green]✓[/green] Roundtrip successful")
            else:
                console.print("[red]✗[/red] Roundtrip produced different output")
                from rich.text import Text
                diff = Text()
                for i, (line1, line2) in enumerate(zip(example["declo"].splitlines(), roundtrip.splitlines())):
                    if line1 != line2:
                        diff.append(f"Line {i+1}:\n", style="bold yellow")
                        diff.append(f"Expected: {line1}\n", style="blue")
                        diff.append(f"Got:      {line2}\n", style="red")
                console.print(Panel(diff, title="[yellow]Differences[/yellow]"))
        except Exception as e:
            console.print("[red]✗[/red] Roundtrip failed")
            console.print("[red]Error:[/red]", str(e))
            console.print("[dim]" + "\n".join(traceback.format_exc().split("\n")[1:]) + "[/dim]")
    
    except Exception as e:
        console.print("[red]✗[/red] Unexpected error during testing")
        console.print("[red]Error:[/red]", str(e))
        console.print("[dim]" + "\n".join(traceback.format_exc().split("\n")[1:]) + "[/dim]")
        console.print("\n[bold red]Debug Information:[/bold red]")
        console.print(Panel(inspect_ast(example["declo"]), title="[red]Last Valid AST[/red]"))

@app.command(name="test-all")
def test_all():
    """Test compile and decompile on all examples and report detailed statistics."""
    examples = load_examples()
    stats = {
        "total": len(examples),
        "compile_success": 0,
        "decompile_success": 0,
        "roundtrip_success": 0,
        "errors": []
    }
    
    console.print("\n[bold cyan]Testing Examples[/bold cyan]")
    
    for example in examples:
        console.print(f"\n[bold yellow]Testing: {example['title']}[/bold yellow]")
        try:
            # Test compilation (Declo -> Python)
            console.print("\n[bold green]Compiling Declo -> Python:[/bold green]")
            display_code(example["declo"], "[blue]Input (Declo)[/blue]")
            
            # Show AST before compilation
            console.print("[bold magenta]AST before compilation:[/bold magenta]")
            console.print(Panel(inspect_ast(example["declo"]), title="[magenta]AST[/magenta]"))
            
            compiled = compile_declo_to_python(example["declo"])
            display_code(compiled, "[green]Output (Python)[/green]")
            stats["compile_success"] += 1
            
            # Test decompilation (Python -> Declo)
            console.print("\n[bold green]Decompiling Python -> Declo:[/bold green]")
            display_code(example["python"], "[blue]Input (Python)[/blue]")
            decompiled = compile_python_to_declo(example["python"])
            display_code(decompiled, "[green]Output (Declo)[/green]")
            stats["decompile_success"] += 1
            
            # Test roundtrip (Declo -> Python -> Declo)
            console.print("\n[bold green]Testing Roundtrip:[/bold green]")
            display_code(example["declo"], "[blue]Original Declo[/blue]")
            roundtrip = compile_python_to_declo(compile_declo_to_python(example["declo"]))
            display_code(roundtrip, "[green]After Roundtrip[/green]")
            
            if roundtrip.strip() == example["declo"].strip():
                stats["roundtrip_success"] += 1
                console.print("[green]✓ Roundtrip successful[/green]")
            else:
                console.print("[yellow]⚠ Roundtrip produced different output[/yellow]")
                # Show diff if outputs are different
                from rich.text import Text
                diff = Text()
                for i, (line1, line2) in enumerate(zip(example["declo"].splitlines(), roundtrip.splitlines())):
                    if line1 != line2:
                        diff.append(f"Line {i+1}:\n", style="bold yellow")
                        diff.append(f"Expected: {line1}\n", style="blue")
                        diff.append(f"Got:      {line2}\n", style="red")
                console.print(Panel(diff, title="[yellow]Differences[/yellow]"))
            
            console.print("\n" + "─" * 80)
            
        except Exception as e:
            stats["errors"].append({
                "title": example["title"],
                "error": str(e),
                "code": example["declo"]
            })
            console.print(f"[red]Error: {str(e)}[/red]")
            console.print("\n[bold red]Debug Information:[/bold red]")
            console.print(Panel(inspect_ast(example["declo"]), title="[red]Last Valid AST[/red]"))
            console.print("\n" + "─" * 80)
    
    # Display results table and errors (unchanged)
    table = Table(title="Test Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Percentage", justify="right", style="yellow")
    
    def add_stat_row(metric: str, count: int):
        percentage = f"{(count / stats['total']) * 100:.1f}%"
        table.add_row(metric, str(count), percentage)
    
    add_stat_row("Total Examples", stats["total"])
    add_stat_row("Compile Success", stats["compile_success"])
    add_stat_row("Decompile Success", stats["decompile_success"])
    add_stat_row("Roundtrip Success", stats["roundtrip_success"])
    
    console.print("\n")
    console.print(table)
    
    if stats["errors"]:
        console.print("\n[bold red]Summary of Errors:[/bold red]")
        for error in stats["errors"]:
            console.print(f"\n[bold yellow]{error['title']}[/bold yellow]")
            display_code(error["code"], "[red]Failed Code[/red]")
            console.print(f"[red]Error: {error['error']}[/red]")

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main() 