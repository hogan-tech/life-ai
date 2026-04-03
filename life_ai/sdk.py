"""Python SDK for life-ai.

Provides a stable programmatic interface for running and resuming simulations
without touching the CLI or web UI layers.

Example usage::

    from life_ai.sdk import run_simulation, resume_simulation

    result = run_simulation("Silicon Valley startup", rounds=3)
    print(result["world"]["idea"])
    for day in result["log"]:
        print(day)

    # Save and resume
    result2 = run_simulation("pirate crew mutiny", rounds=2, save="pirates_run1")
    result3 = resume_simulation("pirates_run1", rounds=2)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from life_ai.persistence import SimulationState, load_state, save_state
from life_ai.simulator import simulate

_SAVES_DIR = Path(__file__).parent.parent / "saves"


def _state_to_payload(state: SimulationState) -> dict:
    """Convert simulation output into a JSON-serializable response dict."""
    world = state.world
    agents = [
        {
            "name": a.name,
            "role": a.role,
            "personality": a.personality,
            "goal": a.goal,
        }
        for a in world.agents
    ]
    relationships = {
        agent_name: {
            target: rm._state.get(target, "neutral")
            for target in rm._state
        }
        for agent_name, rm in state.rel_maps.items()
    }
    return {
        "world": {
            "idea": world.idea,
            "setting": world.setting,
            "conflict": world.conflict,
            "theme": world.theme,
        },
        "agents": agents,
        "relationships": relationships,
        "current_day": state.current_day,
        "log": state.log,
    }


def run_simulation(
    idea: str,
    rounds: int = 3,
    debug: bool = False,
    save: Optional[str] = None,
) -> dict:
    """Run a fresh simulation from an idea string.

    Args:
        idea:   Scenario concept, e.g. ``"Silicon Valley startup"``.
        rounds: Number of simulation rounds to run (default 3).
        debug:  Include LLM/fallback source metadata in each log entry.
        save:   If provided, persist the final state to ``saves/<save>.json``
                so it can be resumed later with :func:`resume_simulation`.

    Returns:
        A JSON-serializable dict with keys:

        - ``world``         — ``{idea, setting, conflict, theme}``
        - ``agents``        — list of ``{name, role, personality, goal}``
        - ``relationships`` — nested dict of final relationship states
        - ``current_day``   — total days simulated so far
        - ``log``           — list of day-log dicts produced by the simulator
    """
    _log, state = simulate(idea=idea, rounds=rounds, debug=debug)
    if save:
        os.makedirs(_SAVES_DIR, exist_ok=True)
        save_state(state, str(_SAVES_DIR / f"{save}.json"))
    return _state_to_payload(state)


def resume_simulation(
    load: str,
    rounds: int = 3,
    debug: bool = False,
    save: Optional[str] = None,
) -> dict:
    """Resume a previously saved simulation.

    Args:
        load:   Name of the save file (without ``.json``), previously written
                by :func:`run_simulation` or the CLI ``--save`` flag.
        rounds: Additional rounds to run (default 3).
        debug:  Include LLM/fallback source metadata in each log entry.
        save:   If provided, overwrite (or create) ``saves/<save>.json`` with
                the updated state after running.

    Returns:
        Same structure as :func:`run_simulation`.

    Raises:
        FileNotFoundError: If ``saves/<load>.json`` does not exist.
        ValueError: If the save file is malformed or missing required fields.
    """
    state = load_state(str(_SAVES_DIR / f"{load}.json"))
    _log, state = simulate(rounds=rounds, debug=debug, state=state)
    save_name = save or load
    os.makedirs(_SAVES_DIR, exist_ok=True)
    save_state(state, str(_SAVES_DIR / f"{save_name}.json"))
    return _state_to_payload(state)
