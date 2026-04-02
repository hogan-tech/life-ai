"""Persistence helpers for saving and loading simulation state."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from life_ai.agent import Memory, RelationshipEventLog, RelationshipMap
from life_ai.world import World


@dataclass
class SimulationState:
    """Complete snapshot of a simulation — enough to resume exactly where it left off."""
    world: World
    current_day: int          # next day index to run (0-based)
    history: list[str]        # full dialogue history as "Speaker: text" strings
    last_speaker: str | None
    last_line: str | None
    memories: dict[str, Memory]
    rel_maps: dict[str, RelationshipMap]
    rel_events: dict[str, RelationshipEventLog]
    log: list[dict]           # accumulated log from all prior runs

    def to_dict(self) -> dict:
        return {
            "world": self.world.model_dump(),
            "current_day": self.current_day,
            "history": self.history,
            "last_speaker": self.last_speaker,
            "last_line": self.last_line,
            "memories": {name: m.to_dict() for name, m in self.memories.items()},
            "rel_maps": {name: rm.to_dict() for name, rm in self.rel_maps.items()},
            "rel_events": {name: re.to_dict() for name, re in self.rel_events.items()},
            "log": self.log,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SimulationState:
        world = World.model_validate(data["world"])
        agent_names = {a.name for a in world.agents}

        memories = {
            name: Memory.from_dict(m)
            for name, m in data["memories"].items()
            if name in agent_names
        }
        rel_maps = {
            name: RelationshipMap.from_dict(rm)
            for name, rm in data["rel_maps"].items()
            if name in agent_names
        }
        rel_events = {
            name: RelationshipEventLog.from_dict(re)
            for name, re in data["rel_events"].items()
            if name in agent_names
        }

        # Ensure every agent has an entry even if the save predates them
        for a in world.agents:
            memories.setdefault(a.name, Memory())
            rel_maps.setdefault(a.name, RelationshipMap.from_agent(a))
            rel_events.setdefault(a.name, RelationshipEventLog())

        return cls(
            world=world,
            current_day=data["current_day"],
            history=data.get("history", []),
            last_speaker=data.get("last_speaker"),
            last_line=data.get("last_line"),
            memories=memories,
            rel_maps=rel_maps,
            rel_events=rel_events,
            log=data.get("log", []),
        )


def save_state(state: SimulationState, path: str) -> None:
    """Write simulation state to a JSON file. Creates parent directories if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(state.to_dict(), f, indent=2)


def load_state(path: str) -> SimulationState:
    """Load simulation state from a JSON file. Raises clear errors on failure."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Save file not found: {path}")
    with open(p) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed save file '{path}': {exc}") from exc
    required = {"world", "current_day", "memories", "rel_maps", "rel_events", "log"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Save file '{path}' is missing required fields: {missing}")
    return SimulationState.from_dict(data)
