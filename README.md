# life-ai

**Turn any idea into a living AI world — in one command.**

life-ai takes a single idea and generates a cast of characters with conflicting goals, then simulates how they clash over multiple rounds.

Not just text generation. **Agents. Roles. Conflict. Story.**

> Current state: MVP (rule-based simulation). LLM-powered agents coming next.

---

## Try it in 30 seconds

```bash
git clone https://github.com/hogan-tech/life-ai.git
cd life-ai
python -m venv .venv && source .venv/bin/activate
pip install -e .

life-ai "Pirates running a tech company"
```

---

## Demo

```
Pirates running a tech company

──────────────────────────── Day 1 ────────────────────────────
  The ship sails.

  Captain Redd   Captain, Hiding Something About the Map
  Captain Redd plants the map on the table: 'We sail at dawn or we rot in port.'

  Bones          Navigator, Loyal Until Proven Wrong
  Bones studies the stars and says the heading is wrong.

──────────────────────────── Day 2 ────────────────────────────
  The map is questioned.

  Yara           Quartermaster, Already Skimming the Treasury
  Yara quietly moves something from the hold to their own quarters.

  Finn           Crew Agitator, One Speech Away from Mutiny
  Finn starts asking why the captain eats while the crew doesn't.

──────────────────────────── Day 3 ────────────────────────────
  Steel is drawn.

  Captain Redd   Captain, Hiding Something About the Map
  Captain Redd draws steel: 'I said Port Null. Anyone disagree says it to my face.'

  Bones          Navigator, Loyal Until Proven Wrong
  Bones refuses to navigate further until someone explains the map.

  Yara           Quartermaster, Already Skimming the Treasury
  Yara offers the crew a cut. It's coming out of someone else's share.
```

---

## Try these ideas

```bash
life-ai "Board fires the founder-CEO"
life-ai "Harvard students building a startup"
life-ai "Elon Musk vs OpenAI board"
life-ai "Ancient Rome with AI agents"
```

---

## Why life-ai?

Most AI tools are one-shot: `input → output`

life-ai is different: `input → world → agents → conflict → evolution`

Each run creates:
- A setting and central conflict
- 4 agents with distinct roles, personalities, and goals
- Multi-round drama where not everyone agrees

---

## Usage

```bash
# after install
life-ai "<your idea>" --rounds 5

# or without installing
python -m life_ai.main "<your idea>" --rounds 5
```

---

## What this is

- A multi-agent simulation prototype
- A system for generating structured conflict from any idea
- A foundation for LLM-driven worlds

## What this is not (yet)

- Powered by a real LLM (coming next)
- Persistent across sessions
- A web app

---

## Roadmap

- [x] CLI simulation engine
- [x] World generation from idea string
- [x] Role-driven agent behavior with personality signals
- [x] Multi-round dramatic arc
- [x] Installable as a package (`pip install -e .`)
- [ ] LLM-powered agents (Anthropic / OpenAI)
- [ ] Agent memory across rounds
- [ ] Persistent world state (save / load)
- [ ] Web interface

---

## Project structure

```
life_ai/
├── main.py        # CLI entry point
├── simulator.py   # Simulation loop and arc structure
├── world.py       # World + agent generation
├── agent.py       # Agent model and act() logic
├── llm.py         # LLM client abstraction (Anthropic-ready)
├── prompts.py     # Prompt templates (stub)
└── utils.py       # Shared helpers (stub)
```

---

## Contributing

PRs welcome. Ideas that would make great contributions:
- New world templates (fantasy, sports, space, politics)
- More personality-driven dialogue patterns
- LLM integration via `llm.py`

---

## License

MIT
