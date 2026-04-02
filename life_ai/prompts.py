from life_ai.agent import Agent

# Explicit tone instructions keyed by relationship state.
# These are injected into the LLM prompt so state → behavior is unambiguous.
_REL_TONE: dict[str, str] = {
    "aligned":     "be openly supportive — reinforce their point, show solidarity",
    "neutral":     "be factual and balanced — no strong pull toward or against them",
    "strained":    "be guarded and terse — keep emotional distance, watch your words",
    "distrustful": "be skeptical and probing — question their motives, don't accept their framing",
    "hostile":     "be aggressive and cutting — let the animosity show, no softening",
}

# Human-readable label for each relationship state (used in prompt phrasing).
_REL_LABEL: dict[str, str] = {
    "aligned":     "allied with",
    "friendly":    "friendly with",
    "neutral":     "neutral toward",
    "strained":    "strained with",
    "distrustful": "distrustful of",
    "hostile":     "hostile toward",
}


def _rel_guidance(relationship_summary: str, rel_events_summary: str) -> str:
    """Build one line per relationship: causal event first, then tone directive.

    Format: You are <label> <name> because: <event(s)> → <tone>
    Leading with "because" ensures the LLM anchors tone to a specific past event,
    not just a state label.
    """
    if not relationship_summary or relationship_summary == "—":
        return "  (no established relationships)"

    # Parse events into a target → reason string map
    event_map: dict[str, str] = {}
    if rel_events_summary and rel_events_summary != "—":
        for line in rel_events_summary.strip().splitlines():
            line = line.strip()
            if ": " in line:
                tgt, evt = line.split(": ", 1)
                event_map[tgt.strip()] = evt.strip()

    lines: list[str] = []
    for part in relationship_summary.split(", "):
        if ": " not in part:
            lines.append(f"  - {part}")
            continue
        name, state = part.split(": ", 1)
        name, state = name.strip(), state.strip()
        label  = _REL_LABEL.get(state, "neutral toward")
        tone   = _REL_TONE.get(state, "be neutral")
        reason = event_map.get(name)
        if reason:
            lines.append(f"  - You are {label} {name} because: {reason} → {tone}")
        else:
            lines.append(f"  - You are {label} {name} → {tone}")
    return "\n".join(lines)


def agent_line_prompt(
    *,
    idea: str,
    setting: str,
    conflict: str,
    beat_label: str,
    agent: Agent,
    history: list[str],
    memory_summary: str = "—",
    relationship_summary: str = "—",
    rel_events_summary: str = "—",
    target_name: str = "",
    target_rel: str = "neutral",
    intent: str = "persuade",
    last_speaker: str | None = None,
    last_line: str | None = None,
    response_type: str = "new_move",
    alliance_context: str = "",
) -> str:
    history_block = "\n".join(history[-8:]) if history else "—"
    target_block = target_name if target_name else "the group"

    last_speaker_block = last_speaker or "—"
    last_line_block    = last_line    or "—"

    if response_type == "direct_response":
        response_instruction = f'The last speaker IS your target ({target_block}). Respond DIRECTLY to what they just said: "{last_line_block}"'
    else:
        response_instruction = "This is a new move — don't react to the last line, drive your own agenda."

    alliance_block = f"\n{alliance_context}\n" if alliance_context else ""

    return f"""You are writing one punchy line for a dramatic story simulation.

Setting: {setting}
Conflict: {conflict}
Moment: {beat_label}

Character: {agent.name} | {agent.role}
Personality: {agent.personality}
Goal: {agent.goal}
Strategy: form alliances against shared enemies; betray when the alliance no longer serves you.

Relationships — what happened and how to act:
{_rel_guidance(relationship_summary, rel_events_summary)}
{alliance_block}
Memory (what {agent.name} remembers):
{memory_summary}

Recent dialogue:
{history_block}

Last speaker: {last_speaker_block}
Last statement: {last_line_block}

Target: {target_block}
Relationship to target: [{target_rel}]
Intent: {intent}

{response_instruction}

Intent definitions — you MUST follow the one matching "{intent}" exactly:
  attack   → Accuse or challenge {target_block}. Reference something specific they did or said.
  defend   → Justify yourself, reject blame, or counter an accusation directed at you.
  persuade → Try to change {target_block}'s mind. Use reasoning, framing, or pressure.
  align    → Show explicit support or agreement with {target_block}.
  threaten → State or imply consequences if {target_block} does not comply.
  ally     → Propose working together with {target_block}. Name the shared threat explicitly.
  betray   → Turn on {target_block}. Name the alliance and make clear you are ending it.

Write ONE line for {agent.name}. Hard rules — no exceptions:
1. START the line with "{target_block}," — address them first, by name.
2. FOLLOW the intent style for "{intent}" strictly as defined above.
3. If a "because" reason appears above, name the specific event — not just the emotion.
4. Max 2 sentences, ≤ 35 words. Direct speech only. No narration. No surrounding quotes.
Output the line only."""
