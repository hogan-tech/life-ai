# life-ai

**Turn any idea into a living AI world — in one command.**

life-ai takes a single idea and generates a cast of characters with conflicting goals, then simulates how they clash over multiple rounds.

Not just text generation. **Agents. Roles. Conflict. Story.**

> Current state: MVP → transitioning into LLM-powered multi-agent simulation.

---

## What's New

- LLM-powered dialogue (Anthropic-ready)
- Strong prompt constraints → sharper output
- Post-processing (_trim) for clean, punchy lines
- Reduced verbosity, more cinematic storytelling

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

We sail at first light — Port Null or nothing.
That heading puts us on the rocks by morning.
I've already counted the shares. Mine first, questions later.

Day 2 — The map is questioned.

Show the map or we stop the ship.
The numbers don’t lie — we’re bleeding.
You want trust? Start with the truth.

Day 3 — Steel is drawn.

Ask nicely, or I drop the map overboard.
Then drop it — we’ll chart our own course.
Fine. But we count the take together.
```

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

## Prompt Design (Key Upgrade)

We moved from vague prompts → constrained prompts:

- Max 2 sentences
- ≤ 35 words
- Strong action / direct speech only
- Rival surfaced explicitly

Result:
- Less fluff  
- More tension  
- Better character voice  

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
- [ ] Agent memory
- [ ] Relationship evolution
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
