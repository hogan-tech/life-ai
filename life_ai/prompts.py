from life_ai.agent import Agent


def agent_line_prompt(
    *,
    idea: str,
    setting: str,
    conflict: str,
    beat_label: str,
    agent: Agent,
    history: list[str],
) -> str:
    history_block = "\n".join(history[-4:]) if history else "—"
    rivals = [n for n, r in agent.relationships.items()
              if any(w in r for w in ("tension", "rival", "distrust", "skeptic"))]
    rival_note = f"Main rival: {rivals[0]}." if rivals else ""

    return f"""You are writing one punchy line for a dramatic story simulation.

Setting: {setting}
Conflict: {conflict}
Moment: {beat_label}

Character: {agent.name} | {agent.role}
Personality: {agent.personality}
Goal: {agent.goal}
{rival_note}

Recent:
{history_block}

Write ONE line for {agent.name}. Rules:
- Max 2 sentences, under 35 words total.
- Strong action or direct speech. No soft narration.
- Reflect their personality. Raise the stakes.
- No name prefix. No quotes around the whole line.
- Output the line only."""
