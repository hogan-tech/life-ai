# life-ai

**Turn any idea into a living AI world — in one command.**

life-ai takes a single idea and turns it into a cast of characters with conflicting goals, then simulates how they evolve over time.

Not just text generation.  
**Agents. Roles. Conflict. Story.**

> Current state: MVP (rule-based simulation). LLM-powered agents coming next.

---

## Why life-ai?

Most AI tools are one-shot:
> input → output

life-ai is different:

> input → world → agents → conflict → evolution

Each run creates:
- a world
- multiple agents
- different roles & incentives
- and emergent behavior over time

---

## Demo

```bash
python -m life_ai.main "Harvard students building a startup" --rounds 5
```

```
Harvard students building a startup

────────────────────────────────────────────────── Day 1 ──────────────────────────────────────────────────
  The pitch begins.

  Maya      Founder-CEO, Running Out of TimeMaya lays out the vision: close series a before runway hits 3 
months.
  Ethan     Co-Founder, Will Not Ship Broken CodeEthan opens a doc and starts listing what's wrong.

────────────────────────────────────────────────── Day 2 ──────────────────────────────────────────────────
  The numbers don't add up.

  Ethan     Co-Founder, Will Not Ship Broken CodeEthan refuses to sign off. Not yet. Not like this.
  Jordan    Lead Investor, Already Losing PatienceJordan quietly shifts position when the numbers change.

────────────────────────────────────────────────── Day 3 ──────────────────────────────────────────────────
  Everyone snaps.

  Jordan    Lead Investor, Already Losing PatienceJordan makes a backroom offer. It's not subtle.
  Priya     Head of Design, Only Adult in the RoomPriya says it out loud — 'This isn't what we said we 
stood for.'
  Maya      Founder-CEO, Running Out of TimeMaya goes all-in: 'If we don't move now, we lose everything.'

────────────────────────────────────────────────── Day 4 ──────────────────────────────────────────────────
  The damage lands.

  Priya     Head of Design, Only Adult in the RoomPriya realizes the ideal version isn't happening.
  Maya      Founder-CEO, Running Out of TimeMaya doubles down. The room gets quieter.

────────────────────────────────────────────────── Day 5 ──────────────────────────────────────────────────
  Ship it or kill it.

  Maya      Founder-CEO, Running Out of TimeMaya reframes the loss as a pivot. Not everyone buys it.
  Ethan     Co-Founder, Will Not Ship Broken CodeEthan extracts one promise before signing off.
```

---

## Installation

```bash
git clone https://github.com/hogan-tech/life-ai.git
cd life-ai

python -m venv .venv
source .venv/bin/activate

pip install -e .
cp .env.example .env
```

---

## Usage

After install:
```bash
life-ai "<your idea>" --rounds 3
```

Or without installing:
```bash
python -m life_ai.main "<your idea>" --rounds 3
```

---

## Try these

```bash
life-ai "Harvard students building a startup"
life-ai "Board fires the founder-CEO"
life-ai "Pirates running a tech company"
```

---

## What this is (and isn't)

This is:
- a multi-agent simulation prototype
- a system for generating structured conflict
- a foundation for LLM-driven worlds

This is NOT (yet):
- a fully autonomous AI system
- a persistent simulation
- powered by real LLM reasoning (coming soon)

---

## Roadmap

- [x] CLI simulation engine
- [x] World generation from idea string
- [x] Multi-round structured interactions
- [x] Role-driven agent behavior

Next:
- [ ] LLM-powered agents (Anthropic / OpenAI)
- [ ] Agent memory across rounds
- [ ] Persistent worlds (save/load)
- [ ] Web interface
- [ ] Multi-language support

---

## Project Structure

```
life_ai/
├── main.py        # CLI entry point
├── simulator.py   # Simulation loop
├── world.py       # World generation logic
├── agent.py       # Agent models
├── llm.py         # LLM abstraction
├── prompts.py     # Prompt templates
└── utils.py       # Helpers
```

---

## Contributing

PRs welcome.

If you have ideas for:
- new world types
- better agent behavior
- more dramatic simulations

open an issue or submit a PR.

---

## License

MIT
