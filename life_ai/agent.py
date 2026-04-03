from dataclasses import dataclass, field
from pydantic import BaseModel

# Ordered from most positive to most negative.
_REL_SCALE = ["aligned", "friendly", "neutral", "strained", "distrustful", "hostile"]

# Map existing relationship labels onto scale positions so initial state is preserved.
_REL_SEED: dict[str, str] = {
    "aligned":              "aligned",
    "friendly":             "friendly",
    "trusted":              "friendly",
    "trusted ally":         "friendly",
    "ally":                 "friendly",
    "ally of convenience":  "neutral",
    "mentor":               "friendly",
    "mentee":               "friendly",
    "neutral":              "neutral",
    "former ally":          "strained",
    "co-founder tension":   "strained",
    "pressure":             "strained",
    "skeptical":            "strained",
    "strained":             "strained",
    "distrustful":          "distrustful",
    "hostile":              "hostile",
    "rivalry":              "distrustful",
    "rival":                "distrustful",
    "tension":              "distrustful",
}


@dataclass
class RelationshipMap:
    """Mutable per-agent relationship state. Evolves during simulation."""
    _state: dict[str, str] = field(default_factory=dict)
    # last signal type this agent sent toward each target ("betray", "challenge", "support", "")
    _last_signal: dict[str, str] = field(default_factory=dict)
    # last round index in which this agent interacted with each target
    _last_interaction: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_agent(cls, agent: "Agent") -> "RelationshipMap":
        state: dict[str, str] = {}
        for name, label in agent.relationships.items():
            state[name] = _REL_SEED.get(label.lower(), "neutral")
        return cls(_state=state)

    def get(self, name: str) -> str:
        return self._state.get(name, "neutral")

    def shift(self, name: str, direction: int) -> None:
        """direction: -1 improves relationship, +1 worsens it."""
        current = self._state.get(name, "neutral")
        idx = _REL_SCALE.index(current) if current in _REL_SCALE else 2
        self._state[name] = _REL_SCALE[max(0, min(len(_REL_SCALE) - 1, idx + direction))]

    def apply_signal(self, name: str, signal: str, round_idx: int) -> int:
        """Apply a signal-driven relationship transition with escalation for repeats.

        Escalation rules:
          betray   → always +2 (drastic; never softened)
          challenge → +1 normally; +2 if the last signal toward this target was also negative
          support  → -1 normally; -2 if the last signal was also support (trust compounds)

        Returns the shift amount actually applied.
        """
        last = self._last_signal.get(name, "")
        if signal == "betray":
            amount = +2
        elif signal == "challenge":
            amount = +2 if last in ("betray", "challenge") else +1
        elif signal == "support":
            amount = -2 if last == "support" else -1
        else:
            amount = 0

        self.shift(name, amount)
        self._last_signal[name] = signal
        self._last_interaction[name] = round_idx
        return amount

    def decay_toward_neutral(self, name: str) -> bool:
        """Move one step toward neutral due to inactivity. Returns True if state changed."""
        current = self._state.get(name, "neutral")
        idx = _REL_SCALE.index(current) if current in _REL_SCALE else 2
        if idx == 2:
            return False
        direction = +1 if idx < 2 else -1
        new_state = _REL_SCALE[max(0, min(len(_REL_SCALE) - 1, idx + direction))]
        if new_state == current:
            return False
        self._state[name] = new_state
        return True

    def summary(self) -> str:
        if not self._state:
            return "—"
        return ", ".join(f"{name}: {rel}" for name, rel in self._state.items())

    def to_dict(self) -> dict:
        return {
            "state": self._state,
            "last_signal": self._last_signal,
            "last_interaction": self._last_interaction,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RelationshipMap":
        obj = cls(_state=data.get("state", {}))
        obj._last_signal = data.get("last_signal", {})
        obj._last_interaction = {k: int(v) for k, v in data.get("last_interaction", {}).items()}
        return obj


@dataclass
class RelationshipEventLog:
    """Records the cause behind each relationship state — the 'why' behind how an agent feels.

    Stores at most _max_per_target concise, first-person event summaries per target.
    Kept separate from Memory so relationship reasons stay co-located with relationship state.
    """
    _events: dict[str, list[str]] = field(default_factory=dict)
    _max_per_target: int = 2  # keep the 2 most recent causal events per target

    def record(self, target: str, description: str) -> None:
        existing = self._events.get(target, [])
        self._events[target] = (existing + [description])[-self._max_per_target:]

    def summary(self) -> str:
        """One line per target: most recent event that shaped the relationship."""
        if not self._events:
            return "—"
        return "\n".join(f"  {target}: {evts[-1]}" for target, evts in self._events.items())

    def to_dict(self) -> dict:
        return {"events": self._events}

    @classmethod
    def from_dict(cls, data: dict) -> "RelationshipEventLog":
        return cls(_events=data.get("events", {}))


@dataclass
class Memory:
    """Lightweight per-agent short-term memory. Bounded to recent rounds only."""
    said: list[str] = field(default_factory=list)      # things this agent said
    heard: list[str] = field(default_factory=list)     # things others said to/about them
    tensions: list[str] = field(default_factory=list)  # explicit conflict moments
    _max: int = 4                                       # max entries per bucket

    def record_said(self, text: str) -> None:
        self.said = (self.said + [text])[-self._max:]

    def record_heard(self, speaker: str, text: str) -> None:
        self.heard = (self.heard + [f"{speaker}: {text}"])[-self._max:]

    def record_tension(self, note: str) -> None:
        self.tensions = (self.tensions + [note])[-self._max:]

    def summary(self) -> str:
        parts: list[str] = []
        if self.said:
            parts.append("I said: " + " / ".join(self.said[-2:]))
        if self.heard:
            parts.append("Others: " + " / ".join(self.heard[-2:]))
        if self.tensions:
            parts.append("Tension: " + " / ".join(self.tensions[-2:]))
        return "\n".join(parts) if parts else "—"

    def to_dict(self) -> dict:
        return {"said": self.said, "heard": self.heard, "tensions": self.tensions}

    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        m = cls()
        m.said = data.get("said", [])
        m.heard = data.get("heard", [])
        m.tensions = data.get("tensions", [])
        return m


_TEMPLATES: dict[str, list[str]] = {
    "aggressive":    ["{name} demands {goal} — now, not later.",
                      "{name} cuts through the noise: {goal} is non-negotiable."],
    "cautious":      ["{name} raises a flag: rushing {goal} could backfire.",
                      "{name} insists on validating every step before {goal}."],
    "visionary":     ["{name} pitches a bold path to {goal}.",
                      "{name} reframes the whole problem around {goal}."],
    "perfectionist": ["{name} won't ship until {goal} meets the bar.",
                      "{name} flags three edge cases blocking {goal}."],
    "pragmatic":     ["{name} proposes the shortest path to {goal}.",
                      "{name} trades ideal for done: good enough is {goal}."],
    "idealistic":    ["{name} argues {goal} is worth the sacrifice.",
                      "{name} rallies the room: {goal} is the right thing to do."],
    "greedy":        ["{name} maneuvers to own {goal} before anyone else can.",
                      "{name} quietly ensures {goal} benefits {name} most."],
    "diplomatic":    ["{name} finds the middle ground — {goal} without losing anyone.",
                      "{name} smooths the tension and redirects toward {goal}."],
}

_DEFAULT_TEMPLATES = ["{name} pushes forward on {goal}.",
                      "{name} makes a move toward {goal}."]


class Agent(BaseModel):
    name: str
    role: str
    personality: str
    goal: str
    relationships: dict[str, str] = {}

    def act(self, step: int = 0) -> str:
        trait = self.personality.split(",")[0].strip().lower()
        templates = _TEMPLATES.get(trait, _DEFAULT_TEMPLATES)
        template = templates[step % len(templates)]
        return template.format(name=self.name, goal=self.goal.lower())
