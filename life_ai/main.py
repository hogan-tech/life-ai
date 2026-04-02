from typing import Optional

import typer
from rich.console import Console
from rich.rule import Rule
from rich.text import Text
from rich.theme import Theme

from life_ai.simulator import simulate
from life_ai.persistence import load_state, save_state

_AGENT_COLORS = ["cyan", "magenta", "green", "yellow", "blue"]

_THEME = Theme({
    "title":   "bold white",
    "day":     "bold yellow",
    "beat":    "dim italic",
    "role":    "dim",
    "speech":  "white",
    "src.llm": "dim green",
    "src.fallback": "dim red",
    "rel":     "dim cyan",
})

app = typer.Typer()
console = Console(theme=_THEME, highlight=False)


def _agent_color(name: str, roster: list[str]) -> str:
    idx = roster.index(name) if name in roster else 0
    return _AGENT_COLORS[idx % len(_AGENT_COLORS)]


@app.command()
def main(
    idea: Optional[str] = typer.Argument(None, help="The world idea to simulate"),
    rounds: int = typer.Option(3, "--rounds", help="Number of simulation rounds"),
    debug: bool = typer.Option(False, "--debug", help="Show LLM vs fallback source per line"),
    save: Optional[str] = typer.Option(None, "--save", help="Save simulation state to this file after running"),
    load: Optional[str] = typer.Option(None, "--load", help="Load and resume a previously saved simulation"),
) -> None:
    if load and idea:
        typer.echo("Error: cannot use both an idea and --load. Use one or the other.", err=True)
        raise typer.Exit(code=1)
    if not load and not idea:
        typer.echo("Error: provide an idea or use --load to resume a saved simulation.", err=True)
        raise typer.Exit(code=1)

    loaded_state = None
    if load:
        try:
            loaded_state = load_state(load)
        except (FileNotFoundError, ValueError) as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(code=1)

    log, final_state = simulate(idea, rounds=rounds, debug=debug, state=loaded_state)

    if save:
        try:
            save_state(final_state, save)
        except OSError as exc:
            typer.echo(f"Warning: could not save state: {exc}", err=True)

    display_idea = final_state.world.idea

    all_names: list[str] = []
    for day in log:
        for line in day["lines"]:
            if line["speaker"] not in all_names:
                all_names.append(line["speaker"])

    console.print()
    console.print(f"[title]  {display_idea}[/title]")
    if load:
        console.print(f"[dim]  Resumed from {load} (day {loaded_state.current_day + 1})[/dim]")
    if save:
        console.print(f"[dim]  State saved → {save}[/dim]")
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

        if day.get("rel_changes"):
            for ch in day["rel_changes"]:
                reason = f"  ({ch['reason']})" if ch.get("reason") else ""
                console.print(Text(f"  ↳ {ch['from']} → {ch['to']}: {ch['old']} → {ch['new']}{reason}", style="rel"))
            console.print()


def run() -> None:
    app()


if __name__ == "__main__":
    app()
