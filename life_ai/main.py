import typer
from rich.console import Console
from rich.rule import Rule
from rich.text import Text
from rich.theme import Theme

from life_ai.simulator import simulate

_AGENT_COLORS = ["cyan", "magenta", "green", "yellow", "blue"]

_THEME = Theme({
    "title":   "bold white",
    "day":     "bold yellow",
    "beat":    "dim italic",
    "role":    "dim",
    "speech":  "white",
    "src.llm": "dim green",
    "src.fallback": "dim red",
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
    debug: bool = typer.Option(False, "--debug", help="Show LLM vs fallback source per line"),
) -> None:
    log = simulate(idea, rounds=rounds, debug=debug)

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

            # Header: name + role on one line
            header = Text("  ")
            header.append(line["speaker"], style=f"bold {color}")
            header.append(f"  [{line['role']}]", style="role")
            if debug:
                src_style = "src.llm" if line["source"] == "llm" else "src.fallback"
                header.append(f"  {line['source'].upper()}", style=src_style)
            console.print(header)

            # Text: indented below
            console.print(Text(f"  {line['text']}", style="speech"))
            console.print()


def run() -> None:
    app()


if __name__ == "__main__":
    app()
