from pydantic import BaseModel

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
