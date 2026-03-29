import typer
from rich.console import Console
from rich.rule import Rule
from rich.text import Text

from life_ai.simulator import simulate

app = typer.Typer()
console = Console()


@app.command()
def main(
    idea: str = typer.Argument(..., help="The world idea to simulate"),
    rounds: int = typer.Option(3, "--rounds", help="Number of simulation rounds"),
) -> None:
    log = simulate(idea, rounds=rounds)

    console.print(f"\n[bold cyan]Simulating:[/bold cyan] {idea}\n")

    current_round = None
    for entry in log:
        if entry["round"] != current_round:
            current_round = entry["round"]
            console.print(Rule(f"[bold yellow]Round {current_round}[/bold yellow]"))

        speaker = Text(f"{entry['speaker']} ", style="bold green")
        role = Text(f"({entry['role']})  ", style="dim")
        text = Text(entry["text"])
        console.print(speaker + role + text)

    console.print()


if __name__ == "__main__":
    app()
