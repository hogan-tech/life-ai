from life_ai.agent import Agent
from life_ai.world import generate_world


def _mock_line(agent: Agent, round_num: int) -> str:
    first_trait = agent.personality.split(",")[0].strip()
    if round_num == 1:
        return f"[{first_trait}] We need to talk about {agent.goal.lower()}."
    if round_num % 2 == 0:
        rivals = [name for name, rel in agent.relationships.items() if "tension" in rel or "distrust" in rel]
        if rivals:
            return f"[{first_trait}] {rivals[0]}, you're missing the point entirely."
        return f"[{first_trait}] I've thought about it — {agent.goal.lower()}. That's final."
    return f"[{first_trait}] If we don't act now, everything falls apart. {agent.goal.split()[0]} is on the line."


def simulate(idea: str, rounds: int = 3) -> list[dict]:
    world = generate_world(idea)
    agents = world["agents"]
    log: list[dict] = []

    for round_num in range(1, rounds + 1):
        for agent in agents:
            log.append({
                "round": round_num,
                "speaker": agent.name,
                "role": agent.role,
                "text": _mock_line(agent, round_num),
            })

    return log
