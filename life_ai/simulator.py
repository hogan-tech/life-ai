from life_ai.agent import Agent, Memory, RelationshipEventLog, RelationshipMap, _REL_SCALE
from life_ai.world import World, generate_world
import life_ai.llm as llm
from life_ai.prompts import agent_line_prompt

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

    Prefers the agent with the most extreme relationship (furthest from
    neutral — either hostile or aligned).  Falls back to the last speaker
    when all relationships are perfectly neutral.
    """
    others = [a.name for a in all_agents if a.name != agent.name]
    if not others:
        return "everyone", "neutral"

    # neutral sits at index 2 in _REL_SCALE; distance from it = strength
    best_score, best_name, best_state = -1, others[0], rel_map.get(others[0])
    for name in others:
        state = rel_map.get(name)
        idx = _REL_SCALE.index(state) if state in _REL_SCALE else 2
        score = abs(idx - 2)
        if score > best_score:
            best_score, best_name, best_state = score, name, state

    # All neutral → fall back to last speaker
    if best_score == 0 and last_speaker and last_speaker in others:
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
        rel_events_summary=rel_event_log.summary(),
        target_name=target_name,
        target_rel=target_rel,
        intent=intent,
        last_speaker=last_speaker,
        last_line=last_line,
        response_type=response_type,
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
    debug: bool = False,
) -> tuple[str, str]:
    """Return (text, source) where source is 'llm' or 'fallback'."""
    if llm.is_available():
        try:
            text = _llm_line(agent, beat_label, world, history, memory, rel_map, rel_event_log, target_name, target_rel, intent, last_speaker, last_line, response_type)
            return text, "llm"
        except Exception as exc:
            if debug:
                print(f"  [LLM ERROR] {agent.name}: {exc}")
    return _rule_based_line(agent, beat, world.theme, rel_map), "fallback"


def _pick_speakers(agents: list[Agent], n: int, day: int) -> list[Agent]:
    start = day % len(agents)
    rotated = agents[start:] + agents[:start]
    return rotated[:n]


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


def simulate(idea: str, rounds: int = 3, debug: bool = False) -> list[dict]:
    world: World = generate_world(idea)
    days = min(rounds, len(_ARC))
    labels = _ARC_LABELS.get(world.theme, _ARC_LABELS["default"])
    log: list[dict] = []
    history: list[str] = []
    memories:   dict[str, Memory]               = {a.name: Memory()                       for a in world.agents}
    rel_maps:   dict[str, RelationshipMap]      = {a.name: RelationshipMap.from_agent(a)  for a in world.agents}
    rel_events: dict[str, RelationshipEventLog] = {a.name: RelationshipEventLog()          for a in world.agents}

    last_speaker: str | None = None
    last_line:    str | None = None

    for day in range(days):
        arc = _ARC[day]
        beat_label = labels[day]
        speakers = _pick_speakers(world.agents, arc["speakers"], day)
        day_lines: list[dict] = []
        day_rel_changes: list[dict] = []

        for a in speakers:
            mem       = memories[a.name]
            rel_map   = rel_maps[a.name]
            rel_evlog = rel_events[a.name]

            target_name, target_rel = _select_target(a, rel_map, world.agents, last_speaker)
            intent = _select_intent(target_rel, step=day)
            response_type = "direct_response" if last_speaker == target_name else "new_move"

            if debug:
                print(f"\n  [TARGET + INTENT + RESPONSE TYPE]")
                print(f"  {a.name} → {target_name} ({intent}, {response_type})")

            text, source = _line(a, arc["beat"], beat_label, world, history, mem, rel_map, rel_evlog, target_name, target_rel, intent, last_speaker, last_line, response_type, debug=debug)
            last_speaker = a.name
            last_line    = text
            day_lines.append({"speaker": a.name, "role": a.role, "text": text, "source": source, "target": target_name, "intent": intent, "response_type": response_type})
            history.append(f"{a.name}: {text}")
            mem.record_said(text)

            signal, reason = _detect_signal(text)

            for other in world.agents:
                if other.name == a.name:
                    continue
                memories[other.name].record_heard(a.name, text)

                if not _mentioned(other.name, text):
                    continue

                if signal == "betray":
                    # Sharply negative: moves two steps (e.g. strained → hostile)
                    old = rel_maps[a.name].get(other.name)
                    rel_maps[a.name].shift(other.name, +2)
                    rel_maps[other.name].shift(a.name, +2)
                    new = rel_maps[a.name].get(other.name)
                    memories[other.name].record_tension(f"{a.name} accused you of betrayal")
                    mem.record_tension(f"You accused {other.name} of betrayal")
                    rel_events[a.name].record(other.name,     f"you accused {other.name} of betrayal")
                    rel_events[other.name].record(a.name,     f"{a.name} accused you of betrayal")
                    if old != new:
                        day_rel_changes.append({"from": a.name, "to": other.name, "old": old, "new": new, "reason": reason})
                    if debug:
                        print(f"\n  [RELATIONSHIP UPDATE]")
                        print(f"  {a.name} → {other.name}: {old} → {new} ({reason})")

                elif signal == "challenge":
                    old = rel_maps[a.name].get(other.name)
                    rel_maps[a.name].shift(other.name, +1)
                    rel_maps[other.name].shift(a.name, +1)
                    new = rel_maps[a.name].get(other.name)
                    memories[other.name].record_tension(f"{a.name} challenged you")
                    mem.record_tension(f"You challenged {other.name}")
                    rel_events[a.name].record(other.name,     f"you challenged {other.name} directly")
                    rel_events[other.name].record(a.name,     f"{a.name} challenged you directly")
                    if old != new:
                        day_rel_changes.append({"from": a.name, "to": other.name, "old": old, "new": new, "reason": reason})
                    if debug:
                        print(f"\n  [RELATIONSHIP UPDATE]")
                        print(f"  {a.name} → {other.name}: {old} → {new} ({reason})")

                elif signal == "support":
                    old = rel_maps[a.name].get(other.name)
                    rel_maps[a.name].shift(other.name, -1)
                    rel_maps[other.name].shift(a.name, -1)
                    new = rel_maps[a.name].get(other.name)
                    rel_events[a.name].record(other.name,     f"you backed {other.name} up")
                    rel_events[other.name].record(a.name,     f"{a.name} backed you up")
                    if old != new:
                        day_rel_changes.append({"from": a.name, "to": other.name, "old": old, "new": new, "reason": reason})
                    if debug:
                        print(f"\n  [RELATIONSHIP UPDATE]")
                        print(f"  {a.name} → {other.name}: {old} → {new} ({reason})")

        log.append({"day": day + 1, "label": beat_label, "lines": day_lines, "rel_changes": day_rel_changes})

    return log
