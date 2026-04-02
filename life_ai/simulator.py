from __future__ import annotations

from life_ai.agent import Agent, Memory, RelationshipEventLog, RelationshipMap, _REL_SCALE
from life_ai.world import World, generate_world
import life_ai.llm as llm
from life_ai.prompts import agent_line_prompt
from life_ai.persistence import SimulationState

# ---------------------------------------------------------------------------
# Arc structure
# ---------------------------------------------------------------------------

_ARC: list[dict] = [
    {"beat": "opening",     "speakers": 2},
    {"beat": "tension",     "speakers": 2},
    {"beat": "conflict",    "speakers": 3},
    {"beat": "consequence", "speakers": 2},
    {"beat": "resolution",  "speakers": 2},
]

_ARC_LABELS: dict[str, list[str]] = {
    "board":   ["The room fills.", "Someone leaks.", "It goes public.", "A title disappears.", "Terms are set."],
    "pirates": ["The ship sails.", "The map is questioned.", "Steel is drawn.", "Someone goes overboard.", "A new course is set."],
    "startup": ["The pitch begins.", "The numbers don't add up.", "Everyone snaps.", "The damage lands.", "Ship it or kill it."],
    "harvard": ["Laptops open.", "The group chat goes quiet.", "Someone sends the email.", "The fallout hits.", "The application goes out."],
    "default": ["Things begin.", "Cracks appear.", "It boils over.", "Someone pays.", "A choice is made."],
}

# ---------------------------------------------------------------------------
# Beat lines: default + per-theme overrides
# ---------------------------------------------------------------------------

_DEFAULT_LINES: dict[str, dict[str, str]] = {
    "opening": {
        "visionary":     "{name} lays out the vision: {goal}.",
        "aggressive":    "{name} opens with a demand: {goal}. Today.",
        "cautious":      "{name} calls for patience before anyone commits to {goal}.",
        "perfectionist": "{name} opens a doc and starts listing what's wrong.",
        "pragmatic":     "{name} skips the preamble and asks who owns {goal}.",
        "idealistic":    "{name} argues this is bigger than anyone's personal agenda.",
        "greedy":        "{name} arrives late, already asking what's in it for them.",
        "diplomatic":    "{name} sets the agenda and makes sure everyone has a seat.",
        "_default":      "{name} shows up and says nothing yet.",
    },
    "tension": {
        "visionary":     "{name} grows impatient — the pace is killing the momentum.",
        "aggressive":    "{name} interrupts: someone is stalling and everyone knows it.",
        "cautious":      "{name} flags a risk nobody wants to hear.",
        "perfectionist": "{name} refuses to sign off. Not yet. Not like this.",
        "pragmatic":     "{name} tries to cut a deal. It doesn't land.",
        "idealistic":    "{name} accuses the group of losing sight of why this matters.",
        "greedy":        "{name} quietly shifts position when the numbers change.",
        "diplomatic":    "{name} tries to soften the blow. It comes across as evasion.",
        "_default":      "{name} senses something is wrong but says nothing.",
    },
    "conflict": {
        "visionary":     "{name} goes all-in: 'If we don't move now, we lose everything.'",
        "aggressive":    "{name} slams the table: '{rival} is sabotaging this.'",
        "cautious":      "{name} threatens to walk unless someone slows down.",
        "perfectionist": "{name} sends a 3am message listing everything that will break.",
        "pragmatic":     "{name} calls out the real problem: no one agrees on {goal}.",
        "idealistic":    "{name} says it out loud — 'This isn't what we said we stood for.'",
        "greedy":        "{name} makes a backroom offer. It's not subtle.",
        "diplomatic":    "{name} tries to mediate. Both sides turn on {name} instead.",
        "_default":      "{name} picks a side and doesn't explain why.",
    },
    "consequence": {
        "visionary":     "{name} doubles down. The room gets quieter.",
        "aggressive":    "{name} wins the argument. Nobody celebrates.",
        "cautious":      "{name}'s warning comes true. Told you so goes unsaid.",
        "perfectionist": "{name} was right about the flaw. Too bad no one listened.",
        "pragmatic":     "{name}'s compromise holds — barely.",
        "idealistic":    "{name} realizes the ideal version isn't happening.",
        "greedy":        "{name} got what they wanted. The cost lands on someone else.",
        "diplomatic":    "{name} absorbs the fallout to keep the peace.",
        "_default":      "{name} quietly adjusts their position.",
    },
    "resolution": {
        "visionary":     "{name} reframes the loss as a pivot. Not everyone buys it.",
        "aggressive":    "{name} sets the new terms. Take it or leave it.",
        "cautious":      "{name} agrees — only because the alternative is worse.",
        "perfectionist": "{name} extracts one promise before signing off.",
        "pragmatic":     "{name} closes it: 'Good enough. Let's move.'",
        "idealistic":    "{name} accepts the outcome and starts planning the next fight.",
        "greedy":        "{name} shakes hands and starts the next play immediately.",
        "diplomatic":    "{name} makes sure everyone walks away with something.",
        "_default":      "{name} nods and says nothing.",
    },
}

# Theme overrides — only traits that should sound different for a given world
_THEME_OVERRIDES: dict[str, dict[str, dict[str, str]]] = {
    "pirates": {
        "opening": {
            "aggressive":    "{name} plants the map on the table: 'We sail at dawn or we rot in port.'",
            "cautious":      "{name} studies the stars and says the heading is wrong.",
            "greedy":        "{name} counts the coin twice before anyone else gets a look.",
            "idealistic":    "{name} calls for equal shares before a single rope is pulled.",
            "_default":      "{name} watches the horizon and keeps their mouth shut.",
        },
        "tension": {
            "aggressive":    "{name} catches someone near the locked chest. Words are exchanged.",
            "cautious":      "{name} finds a hole in the hull that wasn't there yesterday.",
            "greedy":        "{name} quietly moves something from the hold to their own quarters.",
            "idealistic":    "{name} starts asking why the captain eats while the crew doesn't.",
            "_default":      "{name} sharpens a blade and doesn't say why.",
        },
        "conflict": {
            "aggressive":    "{name} draws steel: 'I said Port Null. Anyone disagree says it to my face.'",
            "cautious":      "{name} refuses to navigate further until someone explains the map.",
            "greedy":        "{name} offers the crew a cut. It's coming out of someone else's share.",
            "idealistic":    "{name} stands on the mainmast and calls for a vote. The captain doesn't look pleased.",
            "_default":      "{name} moves to the side of the ship with more crew on it.",
        },
        "consequence": {
            "aggressive":    "{name} is still captain. The dissenter swims.",
            "cautious":      "{name}'s reading was right. The rocks appear at dawn.",
            "greedy":        "{name} has the chest. Nobody can prove how.",
            "idealistic":    "{name} got the vote. The captain got the guns.",
            "_default":      "{name} survives by saying nothing at the right moment.",
        },
        "resolution": {
            "aggressive":    "{name} sets a new course. Nobody asks where it leads.",
            "cautious":      "{name} accepts the compromise and updates the charts.",
            "greedy":        "{name} splits the take — unevenly, but it's done.",
            "idealistic":    "{name} got partial equal shares. Counts it as a win.",
            "_default":      "{name} goes back to work. The sea doesn't care.",
        },
    },
    "board": {
        "opening": {
            "visionary":     "{name} arrives uninvited and takes the seat at the head of the table.",
            "aggressive":    "{name} opens with the vote count. It's not in {rival}'s favor.",
            "cautious":      "{name} reads the charter aloud before anyone says a word.",
            "greedy":        "{name} checks the stock price before asking about the agenda.",
            "diplomatic":    "{name} suggests they table the vote until everyone's lawyer arrives.",
            "_default":      "{name} takes a seat and waits.",
        },
        "tension": {
            "visionary":     "{name} leaks the real reason for the removal. The room goes cold.",
            "aggressive":    "{name} calls for an immediate second vote. Three people look at their phones.",
            "cautious":      "{name} raises the liability question nobody prepared for.",
            "greedy":        "{name} asks what the new CEO package looks like before the old one is out.",
            "diplomatic":    "{name} proposes a joint statement. Nobody agrees on a single word.",
            "_default":      "{name} sends a text under the table.",
        },
        "conflict": {
            "visionary":     "{name} names the real problem out loud: 'This was personal, not governance.'",
            "aggressive":    "{name} calls for {rival}'s resignation. On the record.",
            "cautious":      "{name} reads the clause that makes this removal legally contested.",
            "greedy":        "{name} switches sides when the new term sheet appears.",
            "diplomatic":    "{name} proposes a 30-day transition. Both sides call it a betrayal.",
            "_default":      "{name} abstains. Everyone notices.",
        },
        "consequence": {
            "visionary":     "{name} is out. The company trends on X within the hour.",
            "aggressive":    "{name} gets the chair. The company loses three senior engineers by 5pm.",
            "cautious":      "{name}'s legal flag holds. The vote is frozen pending review.",
            "greedy":        "{name} exits with a package. Nobody's happy about the number.",
            "diplomatic":    "{name}'s compromise fails. They get blamed by both sides.",
            "_default":      "{name} survives the meeting. Their future here is uncertain.",
        },
        "resolution": {
            "visionary":     "{name} posts a public statement. It's more threat than farewell.",
            "aggressive":    "{name} installs the new CEO. The press release goes out before the board vote is final.",
            "cautious":      "{name} ensures the minutes reflect exactly what was and wasn't said.",
            "greedy":        "{name} votes yes, takes the fee, and is on a flight by evening.",
            "diplomatic":    "{name} drafts the statement that satisfies no one and angers no one.",
            "_default":      "{name} signs the document and leaves without comment.",
        },
    },
    "harvard": {
        "opening": {
            "perfectionist": "{name} has already built a prototype. Nobody asked for it but nobody can ignore it.",
            "visionary":     "{name} pitches the B2B pivot at 2am like it's a TED talk.",
            "cautious":      "{name} googles 'co-founder agreement template' before anyone shakes hands.",
            "idealistic":    "{name} says they don't care about funding, only impact. Twice.",
            "diplomatic":    "{name} makes a shared doc and adds everyone as co-editors.",
            "_default":      "{name} shows up with iced coffee and quiet judgment.",
        },
        "tension": {
            "perfectionist": "{name} rewrites the landing page at 3am without telling anyone.",
            "visionary":     "{name} DMs a YC partner without looping in the team.",
            "cautious":      "{name} brings up the part where they still have finals next week.",
            "idealistic":    "{name} asks why the product doesn't mention students in the pitch anymore.",
            "diplomatic":    "{name} suggests a 'founder alignment session.' Nobody wants that.",
            "_default":      "{name} stops replying to the group chat.",
        },
        "conflict": {
            "perfectionist": "{name} says the MVP is embarrassing and refuses to submit it to YC.",
            "visionary":     "{name} says {rival} is holding the company back and everyone already knows it.",
            "cautious":      "{name} says out loud what everyone is thinking: 'What happens if this fails?'",
            "idealistic":    "{name} accuses the team of building for investors, not users.",
            "diplomatic":    "{name} tries to run a vote. It ends in a three-way tie.",
            "_default":      "{name} screenshots the conversation and doesn't say why.",
        },
        "consequence": {
            "perfectionist": "{name} submits a revised deck at 4:59am, one minute before the deadline.",
            "visionary":     "{name} gets credit for the pivot. The team gets a thank-you in the footnotes.",
            "cautious":      "{name}'s hesitation was warranted. The product has a real flaw.",
            "idealistic":    "{name} is right about the mission. The investors don't care.",
            "diplomatic":    "{name} keeps the team together. The product is still unclear.",
            "_default":      "{name} stays on the project. The equity split is unresolved.",
        },
        "resolution": {
            "perfectionist": "{name} ships the MVP. It's not perfect. That was always the problem.",
            "visionary":     "{name} leads the YC interview. The team watches from the waiting room.",
            "cautious":      "{name} signs the agreement after adding one clause nobody else read.",
            "idealistic":    "{name} accepts the B2B pivot. Quietly deletes the original mission statement.",
            "diplomatic":    "{name} proposes a 30-day trial period for the new direction. No one says no.",
            "_default":      "{name} stays. The equity conversation gets scheduled for next week.",
        },
    },
}


def _worst_relationship(agent: Agent, rel_map: RelationshipMap) -> str:
    """Return the name of the agent currently viewed most negatively."""
    worst_idx, worst_name = -1, "someone"
    for name in agent.relationships:
        rel = rel_map.get(name)
        idx = _REL_SCALE.index(rel) if rel in _REL_SCALE else 2
        if idx > worst_idx:
            worst_idx = idx
            worst_name = name
    return worst_name


# ---------------------------------------------------------------------------
# Target selection + intent system
# ---------------------------------------------------------------------------

_INTENT_BY_REL: dict[str, list[str]] = {
    "aligned":     ["align"],
    "friendly":    ["align", "persuade"],
    "neutral":     ["persuade"],
    "strained":    ["defend", "persuade"],
    "distrustful": ["attack", "threaten"],
    "hostile":     ["attack", "threaten"],
}


def _select_target(
    agent: Agent,
    rel_map: RelationshipMap,
    all_agents: list[Agent],
    last_speaker: str | None,
) -> tuple[str, str]:
    """Return (target_name, rel_state).

    Primary: pick the agent with the most extreme relationship (furthest from neutral).
    Tiebreak: prefer the negative side (distrustful > aligned when both score 2).
    Rationale: agents confront rivals first; alliances are addressed reactively.
    Fallback to last_speaker when all relationships are neutral.
    """
    others = [a.name for a in all_agents if a.name != agent.name]
    if not others:
        return "everyone", "neutral"

    # neutral is at index 2; score = (distance_from_neutral, negative_tiebreak)
    # negative_tiebreak=1 means the relationship is on the hostile side → preferred
    best_key   = (-1, 0)
    best_name  = others[0]
    best_state = rel_map.get(others[0])

    for name in others:
        state = rel_map.get(name)
        idx   = _REL_SCALE.index(state) if state in _REL_SCALE else 2
        key   = (abs(idx - 2), 1 if idx > 2 else 0)
        if key > best_key:
            best_key, best_name, best_state = key, name, state

    # All neutral → fall back to last speaker
    if best_key[0] == 0 and last_speaker and last_speaker in others:
        return last_speaker, rel_map.get(last_speaker)

    return best_name, best_state


def _select_intent(rel_state: str, step: int = 0) -> str:
    """Map relationship state to a concrete intent label."""
    options = _INTENT_BY_REL.get(rel_state, ["persuade"])
    return options[step % len(options)]


def _rule_based_line(agent: Agent, beat: str, theme: str, rel_map: RelationshipMap | None = None) -> str:
    trait = agent.personality.split(",")[0].strip().lower()
    theme_beats = _THEME_OVERRIDES.get(theme, {}).get(beat, {})
    default_beats = _DEFAULT_LINES.get(beat, {})
    template = theme_beats.get(trait) or default_beats.get(trait) or default_beats.get("_default", "{name} acts.")
    if rel_map is not None:
        rival = _worst_relationship(agent, rel_map)
    else:
        rival = next(
            (n for n, r in agent.relationships.items() if any(w in r for w in ("tension", "rival", "distrust", "skeptic"))),
            "someone",
        )
    return template.format(name=agent.name, goal=agent.goal.lower(), rival=rival)


_MAX_WORDS = 40


def _trim(text: str) -> str:
    """Keep the first 1–2 sentences and enforce a word cap."""
    text = text.strip().strip('"').strip()
    # Take at most 2 sentences
    sentences: list[str] = []
    for part in text.replace("! ", ". ").replace("? ", ". ").split(". "):
        part = part.strip()
        if not part:
            continue
        sentences.append(part)
        if len(sentences) == 2:
            break
    clipped = ". ".join(sentences)
    if not clipped.endswith((".", "!", "?")):
        clipped += "."
    # Hard word cap
    words = clipped.split()
    if len(words) > _MAX_WORDS:
        clipped = " ".join(words[:_MAX_WORDS]).rstrip(",") + "..."
    return clipped


def _rel_events_summary(rel_event_log: RelationshipEventLog) -> str:
    """Build an events summary with up to 2 causal reasons per target."""
    events = rel_event_log._events
    if not events:
        return "—"
    parts = []
    for target, evts in events.items():
        recent = evts[-2:]  # at most 2, most recent last
        parts.append(f"  {target}: {' / '.join(recent)}")
    return "\n".join(parts) if parts else "—"


def _llm_line(
    agent: Agent,
    beat_label: str,
    world: World,
    history: list[str],
    memory: Memory,
    rel_map: RelationshipMap,
    rel_event_log: RelationshipEventLog,
    target_name: str,
    target_rel: str,
    intent: str,
    last_speaker: str | None,
    last_line: str | None,
    response_type: str,
    alliance_context: str = "",
) -> str:
    prompt = agent_line_prompt(
        idea=world.idea,
        setting=world.setting,
        conflict=world.conflict,
        beat_label=beat_label,
        agent=agent,
        history=history,
        memory_summary=memory.summary(),
        relationship_summary=rel_map.summary(),
        rel_events_summary=_rel_events_summary(rel_event_log),
        target_name=target_name,
        target_rel=target_rel,
        intent=intent,
        last_speaker=last_speaker,
        last_line=last_line,
        response_type=response_type,
        alliance_context=alliance_context,
    )
    return _trim(llm.complete(prompt))


def _line(
    agent: Agent,
    beat: str,
    beat_label: str,
    world: World,
    history: list[str],
    memory: Memory,
    rel_map: RelationshipMap,
    rel_event_log: RelationshipEventLog,
    target_name: str,
    target_rel: str,
    intent: str,
    last_speaker: str | None,
    last_line: str | None,
    response_type: str,
    alliance_context: str = "",
    debug: bool = False,
) -> tuple[str, str]:
    """Return (text, source) where source is 'llm' or 'fallback'."""
    if llm.is_available():
        try:
            text = _llm_line(agent, beat_label, world, history, memory, rel_map, rel_event_log, target_name, target_rel, intent, last_speaker, last_line, response_type, alliance_context)
            return text, "llm"
        except Exception as exc:
            if debug:
                print(f"  [LLM ERROR] {agent.name}: {exc}")
    return _rule_based_line(agent, beat, world.theme, rel_map), "fallback"


def _pick_speakers(agents: list[Agent], n: int, day: int) -> list[Agent]:
    start = day % len(agents)
    rotated = agents[start:] + agents[:start]
    return rotated[:n]


_DECAY_ROUNDS = 3   # rounds of silence before a relationship drifts one step toward neutral

# ---------------------------------------------------------------------------
# Alliance detection
# ---------------------------------------------------------------------------

_ALLIANCE_STATES = {"aligned", "friendly"}
_ENEMY_STATES    = {"distrustful", "hostile"}


def _detect_alliances(
    agents: list[Agent],
    rel_maps: dict[str, RelationshipMap],
) -> dict[str, list[tuple[str, str]]]:
    """Return per-agent list of (ally_name, common_enemy) pairs.

    Alliance condition: mutual positive relationship AND a shared enemy.
    Each (ally, enemy) pair is stored once per side (A gets (B, C); B gets (A, C)).
    """
    result: dict[str, list[tuple[str, str]]] = {a.name: [] for a in agents}
    names  = [a.name for a in agents]
    seen: set[tuple[str, str, str]] = set()

    for a_name in names:
        for b_name in names:
            if b_name == a_name:
                continue
            if rel_maps[a_name].get(b_name) not in _ALLIANCE_STATES:
                continue
            if rel_maps[b_name].get(a_name) not in _ALLIANCE_STATES:
                continue
            for c_name in names:
                if c_name in (a_name, b_name):
                    continue
                if (rel_maps[a_name].get(c_name) in _ENEMY_STATES and
                        rel_maps[b_name].get(c_name) in _ENEMY_STATES):
                    key = (min(a_name, b_name), max(a_name, b_name), c_name)
                    if key not in seen:
                        seen.add(key)
                        result[a_name].append((b_name, c_name))
                        result[b_name].append((a_name, c_name))
    return result


def _apply_alliance_override(
    agent_name: str,
    target_name: str,
    rel_maps: dict[str, RelationshipMap],
    alliances: dict[str, list[tuple[str, str]]],
) -> tuple[str, str]:
    """If the selected target is an ally, redirect to the most hostile shared enemy instead.

    Returns (target_name, target_rel) — possibly unchanged.
    """
    items = alliances.get(agent_name, [])
    if not items:
        return target_name, rel_maps[agent_name].get(target_name)

    ally_names  = {ally  for ally,  _ in items}
    enemy_names = {enemy for _, enemy in items}

    if target_name in ally_names and enemy_names:
        best_enemy = max(
            enemy_names,
            key=lambda e: _REL_SCALE.index(rel_maps[agent_name].get(e))
            if rel_maps[agent_name].get(e) in _REL_SCALE else 2,
        )
        return best_enemy, rel_maps[agent_name].get(best_enemy)

    return target_name, rel_maps[agent_name].get(target_name)


def _fmt_alliance_context(
    agent_name: str,
    alliances: dict[str, list[tuple[str, str]]],
) -> str:
    """Return a formatted coalition block for prompt injection, or '' if none."""
    items = alliances.get(agent_name, [])
    if not items:
        return ""
    lines = [f"  - Allied with {ally} against {enemy}" for ally, enemy in items]
    return "Coalition:\n" + "\n".join(lines)


def _should_betray(
    agent_name: str,
    alliances: dict[str, list[tuple[str, str]]],
    rel_maps: dict[str, RelationshipMap],
    rel_events: dict[str, RelationshipEventLog],
) -> str | None:
    """Return the name of an ally to betray, or None.

    Betrayal conditions (any one sufficient):
      A — prior tension with the ally (they challenged / attacked / accused us)
      B — the common enemy is no longer a real threat (decayed to neutral or positive)
    """
    for ally, enemy in alliances.get(agent_name, []):
        events = rel_events[agent_name]._events.get(ally, [])
        has_tension = any(
            any(w in e.lower() for w in ("challenged", "attacked", "accused", "betrayed"))
            for e in events
        )
        weak_enemy = rel_maps[agent_name].get(enemy) not in _ENEMY_STATES
        if has_tension or weak_enemy:
            return ally
    return None


def _find_ally_target(
    agent_name: str,
    alliances: dict[str, list[tuple[str, str]]],
    rel_maps: dict[str, RelationshipMap],
    all_agents: list[Agent],
) -> tuple[str, str] | None:
    """Return (potential_ally_name, current_rel) or None.

    Seek alliance with a non-enemy agent who shares at least one of our strong enemies.
    Skips agents already allied or actively hostile.
    """
    names = [a.name for a in all_agents if a.name != agent_name]
    current_allies = {ally for ally, _ in alliances.get(agent_name, [])}

    agent_enemies = {name for name in names if rel_maps[agent_name].get(name) in _ENEMY_STATES}
    if not agent_enemies:
        return None

    for name in names:
        if name in current_allies:
            continue
        candidate_rel = rel_maps[agent_name].get(name)
        if candidate_rel in _ENEMY_STATES:
            continue
        for enemy in agent_enemies:
            if rel_maps[name].get(enemy) in _ENEMY_STATES:
                return name, candidate_rel
    return None


_BETRAY_WORDS = {
    "betray", "backstab", "sold us", "sold you", "lied to",
    "used you", "used us", "played us", "manipulated", "double-cross",
}
_CHALLENGE_WORDS = {
    "wrong", "sabotage", "stop", "against", "refuse", "won't", "can't trust",
    "enough", "overboard", "never", "liar", "lie", "cheat", "back off",
    "stay out", "you can't", "dare you", "ridiculous", "absurd",
    "threaten", "not your call", "no one asked", "over my",
}
_SUPPORT_WORDS = {
    "agree", "right", "with you", "trust", "protect", "together", "back you",
    "same", "support", "help", "exactly", "absolutely", "stand with",
    "behind you", "believe you", "your side", "stand by",
}


def _detect_signal(text: str) -> tuple[str, str]:
    """Return (signal_type, reason). Types: 'betray', 'challenge', 'support', or ''."""
    lower = text.lower()
    if any(w in lower for w in _BETRAY_WORDS):
        return "betray", "accused of betrayal"
    if any(w in lower for w in _CHALLENGE_WORDS):
        return "challenge", "direct challenge"
    if any(w in lower for w in _SUPPORT_WORDS):
        return "support", "showed agreement"
    return "", ""


def _mentioned(name: str, text: str) -> bool:
    return name.split()[0].lower() in text.lower()


def simulate(
    idea: str | None = None,
    rounds: int = 3,
    debug: bool = False,
    state: SimulationState | None = None,
) -> tuple[list[dict], SimulationState]:
    """Run the simulation and return (new_log, final_state).

    Pass `state` to resume from a saved run.  `idea` is required for fresh runs.
    """
    if state is not None:
        world        = state.world
        start_day    = state.current_day
        history      = list(state.history)
        memories     = state.memories
        rel_maps     = state.rel_maps
        rel_events   = state.rel_events
        last_speaker = state.last_speaker
        last_line    = state.last_line
        prior_log    = list(state.log)
    else:
        if idea is None:
            raise ValueError("idea is required when no saved state is loaded")
        world        = generate_world(idea)
        start_day    = 0
        history      = []
        memories     = {a.name: Memory()                       for a in world.agents}
        rel_maps     = {a.name: RelationshipMap.from_agent(a)  for a in world.agents}
        rel_events   = {a.name: RelationshipEventLog()         for a in world.agents}
        last_speaker = None
        last_line    = None
        prior_log    = []

    labels   = _ARC_LABELS.get(world.theme, _ARC_LABELS["default"])
    new_log:  list[dict] = []
    end_day  = start_day + rounds

    for day_idx in range(start_day, end_day):
        arc        = _ARC[day_idx % len(_ARC)]
        beat_label = labels[day_idx % len(labels)]
        speakers   = _pick_speakers(world.agents, arc["speakers"], day_idx)
        day_lines:       list[dict] = []
        day_rel_changes: list[dict] = []

        # --- Decay pass: relationships with no recent interaction drift toward neutral ---
        for a in world.agents:
            rel_map = rel_maps[a.name]
            for other in world.agents:
                if other.name == a.name:
                    continue
                last = rel_map._last_interaction.get(other.name, -_DECAY_ROUNDS - 1)
                if day_idx - last >= _DECAY_ROUNDS:
                    old = rel_map.get(other.name)
                    changed = rel_map.decay_toward_neutral(other.name)
                    if changed and debug:
                        new = rel_map.get(other.name)
                        print(f"  [DECAY] {a.name} → {other.name}: {old} → {new}")
                    if changed:
                        day_rel_changes.append({
                            "from": a.name, "to": other.name,
                            "old": old, "new": rel_map.get(other.name),
                            "reason": "inactivity decay",
                        })

        # Detect alliances once per round — used for target override + prompt context
        alliances = _detect_alliances(world.agents, rel_maps)

        for a in speakers:
            mem       = memories[a.name]
            rel_map   = rel_maps[a.name]
            rel_evlog = rel_events[a.name]

            target_name, target_rel = _select_target(a, rel_map, world.agents, last_speaker)

            # Strategic intent: betray > ally-build > default alliance override
            strategic_intent: str | None = None
            betray_target = _should_betray(a.name, alliances, rel_maps, rel_events)
            if betray_target:
                target_name      = betray_target
                target_rel       = rel_map.get(betray_target)
                strategic_intent = "betray"
            else:
                ally_result = _find_ally_target(a.name, alliances, rel_maps, world.agents)
                if ally_result:
                    target_name, target_rel = ally_result
                    strategic_intent = "ally"

            if strategic_intent is not None:
                intent = strategic_intent
            else:
                target_name, target_rel = _apply_alliance_override(a.name, target_name, rel_maps, alliances)
                intent = _select_intent(target_rel, step=day_idx)

            response_type = "direct_response" if last_speaker == target_name else "new_move"
            alliance_ctx  = _fmt_alliance_context(a.name, alliances)

            if debug:
                print(f"\n  [TARGET + INTENT + RESPONSE TYPE]")
                print(f"  {a.name} → {target_name} ({intent}, {response_type})")
                if alliance_ctx:
                    print(f"  [ALLIANCE] {alliance_ctx.replace(chr(10), ' | ')}")

            text, source = _line(
                a, arc["beat"], beat_label, world, history, mem, rel_map, rel_evlog,
                target_name, target_rel, intent, last_speaker, last_line, response_type,
                alliance_context=alliance_ctx, debug=debug,
            )
            last_speaker = a.name
            last_line    = text
            day_lines.append({
                "speaker": a.name, "role": a.role, "text": text, "source": source,
                "target": target_name, "intent": intent, "response_type": response_type,
            })
            history.append(f"{a.name}: {text}")
            mem.record_said(text)

            # --- Guaranteed updates for strategic intents (not keyword-dependent) ---
            agent_names_set = {ag.name for ag in world.agents}
            if intent == "betray" and target_name in agent_names_set:
                old = rel_maps[a.name].get(target_name)
                rel_maps[a.name].apply_signal(target_name, "betray", day_idx)
                rel_maps[target_name].apply_signal(a.name, "betray", day_idx)
                new = rel_maps[a.name].get(target_name)
                mem.record_tension(f"You betrayed {target_name}")
                memories[target_name].record_tension(f"{a.name} betrayed you")
                rel_events[a.name].record(target_name,  f"you betrayed {target_name}")
                rel_events[target_name].record(a.name,  f"{a.name} betrayed you")
                if old != new:
                    day_rel_changes.append({"from": a.name, "to": target_name, "old": old, "new": new, "reason": "intentional betrayal"})
                if debug:
                    print(f"\n  [BETRAYAL] {a.name} → {target_name}: {old} → {new}")

            elif intent == "ally" and target_name in agent_names_set:
                old = rel_maps[a.name].get(target_name)
                rel_maps[a.name].apply_signal(target_name, "support", day_idx)
                rel_maps[target_name].apply_signal(a.name, "support", day_idx)
                new = rel_maps[a.name].get(target_name)
                rel_events[a.name].record(target_name,  f"you sought alliance with {target_name}")
                rel_events[target_name].record(a.name,  f"{a.name} sought alliance with you")
                if old != new:
                    day_rel_changes.append({"from": a.name, "to": target_name, "old": old, "new": new, "reason": "alliance building"})
                if debug:
                    print(f"\n  [ALLY BUILD] {a.name} → {target_name}: {old} → {new}")

            signal, reason = _detect_signal(text)

            for other in world.agents:
                if other.name == a.name:
                    continue
                memories[other.name].record_heard(a.name, text)

                if not _mentioned(other.name, text):
                    continue

                if signal == "betray":
                    old = rel_maps[a.name].get(other.name)
                    rel_maps[a.name].apply_signal(other.name, "betray", day_idx)
                    rel_maps[other.name].apply_signal(a.name, "betray", day_idx)
                    new = rel_maps[a.name].get(other.name)
                    memories[other.name].record_tension(f"{a.name} accused you of betrayal")
                    mem.record_tension(f"You accused {other.name} of betrayal")
                    rel_events[a.name].record(other.name,  f"you accused {other.name} of betrayal")
                    rel_events[other.name].record(a.name,  f"{a.name} accused you of betrayal")
                    if old != new:
                        day_rel_changes.append({"from": a.name, "to": other.name, "old": old, "new": new, "reason": reason})
                    if debug:
                        print(f"\n  [RELATIONSHIP UPDATE]")
                        print(f"  {a.name} → {other.name}: {old} → {new} ({reason})")

                elif signal == "challenge":
                    old = rel_maps[a.name].get(other.name)
                    rel_maps[a.name].apply_signal(other.name, "challenge", day_idx)
                    rel_maps[other.name].apply_signal(a.name, "challenge", day_idx)
                    new = rel_maps[a.name].get(other.name)
                    memories[other.name].record_tension(f"{a.name} challenged you")
                    mem.record_tension(f"You challenged {other.name}")
                    rel_events[a.name].record(other.name,  f"you challenged {other.name} directly")
                    rel_events[other.name].record(a.name,  f"{a.name} challenged you directly")
                    if old != new:
                        day_rel_changes.append({"from": a.name, "to": other.name, "old": old, "new": new, "reason": reason})
                    if debug:
                        print(f"\n  [RELATIONSHIP UPDATE]")
                        print(f"  {a.name} → {other.name}: {old} → {new} ({reason})")

                elif signal == "support":
                    old = rel_maps[a.name].get(other.name)
                    rel_maps[a.name].apply_signal(other.name, "support", day_idx)
                    rel_maps[other.name].apply_signal(a.name, "support", day_idx)
                    new = rel_maps[a.name].get(other.name)
                    rel_events[a.name].record(other.name,  f"you backed {other.name} up")
                    rel_events[other.name].record(a.name,  f"{a.name} backed you up")
                    if old != new:
                        day_rel_changes.append({"from": a.name, "to": other.name, "old": old, "new": new, "reason": reason})
                    if debug:
                        print(f"\n  [RELATIONSHIP UPDATE]")
                        print(f"  {a.name} → {other.name}: {old} → {new} ({reason})")

        new_log.append({"day": day_idx + 1, "label": beat_label, "lines": day_lines, "rel_changes": day_rel_changes})

    final_state = SimulationState(
        world=world,
        current_day=end_day,
        history=history,
        last_speaker=last_speaker,
        last_line=last_line,
        memories=memories,
        rel_maps=rel_maps,
        rel_events=rel_events,
        log=prior_log + new_log,
    )
    return new_log, final_state
