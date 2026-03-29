# life-ai

**Turn any idea into a living AI world in one command.**

life-ai takes a short idea string and generates a cast of characters with distinct personalities, goals, and relationships — then simulates how they interact over multiple rounds.

> Current state: MVP with mock world generation and mock dialogue. LLM-powered simulation coming next.

---

## Installation

```bash
git clone https://github.com/your-org/life-ai.git
cd life-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY when ready
```

## Usage

```bash
python -m life_ai.main "<your idea>" --rounds <n>
```

## Demo

```bash
python -m life_ai.main "AI startup drama" --rounds 2
```

```
Simulating: AI startup drama

────────────────── Round 1 ──────────────────
Maya  (CEO)              [visionary] We need to talk about secure series a funding before runway runs out.
Ethan (CTO)              [perfectionist] We need to talk about ship reliable software without cutting corners.
Priya (Head of Product)  [pragmatic] We need to talk about keep the team aligned and users happy.

────────────────── Round 2 ──────────────────
Maya  (CEO)              [visionary] Ethan, you're missing the point entirely.
Ethan (CTO)              [perfectionist] Maya, you're missing the point entirely.
Priya (Head of Product)  [pragmatic] I've thought about it — keep the team aligned and users happy. That's final.
```

---

## Project Vision

Most AI demos are one-shot: ask a question, get an answer. life-ai is different — it creates a persistent world with characters who have competing goals, histories, and relationships. Feed it any premise and watch the drama unfold.

The end goal: a multi-agent simulation engine where each character is powered by a real LLM, remembers past events, and drives the story forward autonomously.

---

## Roadmap

- [x] CLI entry point with `typer` + `rich` output
- [x] Mock world generation from an idea string
- [x] Mock multi-round dialogue simulation
- [x] LLM client abstraction (`life_ai/llm.py`)
- [ ] LLM-powered world generation via Anthropic API
- [ ] LLM-powered per-agent dialogue
- [ ] Agent memory across rounds
- [ ] Persistent world state (save/load)
- [ ] Web UI

---

## Project Structure

```
life_ai/
├── main.py        # CLI entry point
├── simulator.py   # Orchestration loop
├── world.py       # World generation
├── agent.py       # Agent data model
├── llm.py         # LLM client abstraction
├── prompts.py     # Prompt templates (stub)
└── utils.py       # Shared helpers (stub)
```

---

## Contributing

PRs welcome. Open an issue first for anything beyond small fixes.

## License

MIT
