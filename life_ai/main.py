import typer
from rich.console import Console
from rich.rule import Rule
from rich.text import Text
from rich.theme import Theme

from life_ai.simulator import simulate

_AGENT_COLORS = ["cyan", "magenta", "green", "yellow", "blue"]

_THEME = Theme({
    "title":  "bold white",
    "day":    "bold yellow",
    "beat":   "dim italic",
    "role":   "dim",
    "speech": "white",
})

app = typer.Typer()
console = Console(theme=_THEME, highlight=False)


def _agent_color(name: str, roster: list[str]) -> str:
    idx = roster.index(name) if name in roster else 0
    return _AGENT_COLORS[idx % len(_AGENT_COLORS)]


@app.command()
def main(
    idea: str = typer.Argument(..., help="The world idea to simulate"),
    rounds: int = typer.Option(3, "--rounds", help="Number of simulation rounds"),
) -> None:
    log = simulate(idea, rounds=rounds)

    # Build a stable name → color mapping from day 1
    all_names: list[str] = []
    for day in log:
        for line in day["lines"]:
            if line["speaker"] not in all_names:
                all_names.append(line["speaker"])

    console.print()
    console.print(f"[title]  {idea}[/title]")
    console.print()

    for day in log:
        console.print(Rule(f"[day]Day {day['day']}[/day]", style="yellow"))
        console.print(f"  [beat]{day['label']}[/beat]")
        console.print()

        for line in day["lines"]:
            color = _agent_color(line["speaker"], all_names)
            row = Text("  ")
            row.append(f"{line['speaker']:<10}", style=f"bold {color}")
            row.append(f"{line['role']:<20}", style="role")
            row.append(line["text"], style="speech")
            console.print(row)

        console.print()


def run() -> None:
    app()


if __name__ == "__main__":
    app()
