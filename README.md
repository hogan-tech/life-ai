# life-ai

**Turn any idea into a living AI world — in one command.**

life-ai takes a single idea and generates a cast of characters with conflicting goals, then simulates how they clash over multiple rounds.

Not just text generation. **Agents. Roles. Conflict. Story.**

> Current state: Intent-driven multi-agent simulation with targeted dialogue and conversational memory.

---

## What's New

- Intent-driven dialogue — every line has a target and a goal (attack, defend, persuade, align, threaten)
- Targeted addressing — agents speak directly to a named character, not into the void
- Conversation memory — agents respond to what was just said when their target spoke last
- Relationship evolution — relationships shift based on what agents actually do
- Agent memory — each agent remembers what they said, heard, and what tensions occurred
- LLM-powered dialogue (Anthropic-ready)
- Strong prompt constraints → sharper, more cinematic output

---

## Try it in 30 seconds

```bash
git clone https://github.com/hogan-tech/life-ai.git
cd life-ai
python -m venv .venv && source .venv/bin/activate
pip install -e .

life-ai "Pirates running a tech company" --rounds 3 --debug
```

---

## Demo (LLM Mode)

```
Day 1 — The ship sails.

Finn, we sail at first light — Port Null or nothing.
Bones, that heading puts us on the rocks by morning.

Day 2 — The map is questioned.

Finn, you hid the numbers once already — I’m not signing anything you touch.
Bones, the map is open right now, so name what you actually want.

Day 3 — Steel is drawn.

Finn, hand over the ledger now or I take this to the crew and you’re done.
Bones, go ahead — the crew already knows who’s been skimming.
```

Each line targets a specific agent and reflects a concrete intent (attack, threaten, defend, etc.).

---

## Core Idea

Most AI tools are one-shot:

input → output

life-ai is a system:

input → world → agents → conflict → evolution

Each run creates:
- A setting and central conflict
- 4 agents with roles, personalities, goals
- Multi-round interactions
- Emergent narrative

---

## Usage

```bash
life-ai "<your idea>" --rounds 5 --debug
```

or

```bash
python -m life_ai.main "<your idea>" --rounds 5
```

---

## Agent Behavior

Each turn, an agent:

1. **Selects a target** — the agent with the strongest relationship (most hostile or most aligned). Falls back to the last speaker if all relationships are neutral.
2. **Picks an intent** — derived from the relationship state:
   - `hostile` / `distrustful` → `attack` or `threaten`
   - `strained` → `defend` or `persuade`
   - `neutral` → `persuade`
   - `friendly` / `aligned` → `align`
3. **Determines response type** — if the target spoke last, the agent responds directly to their line (`direct_response`). Otherwise it drives its own agenda (`new_move`).

---

## Prompt Design

Every LLM call enforces:

- **Target addressing** — line must start with the target's name
- **Intent compliance** — strict behavioral definition for each intent (attack = accuse, threaten = state consequences, etc.)
- **Specific reference** — if a relationship event exists, the line must name it, not just the feeling
- Max 2 sentences, ≤ 35 words, direct speech only

---

## Post-processing (_trim)

Every LLM output is cleaned:

- Keep max 2 sentences
- Enforce word limit (~40 words hard cap)
- Remove quotes / noise
- Ensure clean punctuation

---

## Project Structure

```
life_ai/
├── main.py
├── simulator.py
├── world.py
├── agent.py
├── llm.py
├── prompts.py
└── utils.py
```

---

## Environment Setup (LLM)

Create `.env`:

ANTHROPIC_API_KEY=your_api_key_here

---

## Try These Ideas

```bash
life-ai "Board fires the founder-CEO"
life-ai "Harvard students building a startup"
life-ai "Elon Musk vs OpenAI board"
life-ai "Ancient Rome with AI agents"
```

---

## Roadmap

- [x] CLI simulation engine
- [x] Multi-agent system
- [x] LLM-powered dialogue
- [x] Prompt optimization
- [x] Output post-processing
- [x] Agent memory
- [x] Relationship evolution
- [x] Targeted interaction (target selection + intent system)
- [x] Conversation memory (direct response vs new move)
- [ ] Persistent world state
- [ ] Web UI
- [ ] API / SDK

---

## Contributing

PRs welcome. High-impact areas:
- Agent intelligence
- Prompt tuning
- Memory systems
- UI / visualization

---

## Philosophy

This is not a story generator.  
It's a system where characters conflict, adapt, and evolve.

---

## License

MIT
