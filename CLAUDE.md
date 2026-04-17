# CLAUDE.md

This file provides implementation guidance for Claude Code when working in this repository.

## Project Overview

**life-ai** turns a simple idea into a living multi-agent AI simulation with distinct characters, goals, and evolving interactions.

Example:

```bash
python -m life_ai.main "Silicon Valley startup"
````

The project should feel:

* simple to run
* fun to demo
* easy to understand
* extensible over time

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then fill in API keys if LLM features are enabled.

## Core Architecture

All core logic lives in `life_ai/`.

* **`main.py`** — Typer CLI entry point
* **`simulator.py`** — Simulation loop, turn neoxration, target selection, intent system, relationship updates
* **`world.py`** — World generation and shared scenario context
* **`agent.py`** — Agent models, `RelationshipMap`, `RelationshipEventLog`, `Memory`
* **`llm.py`** — LLM provider wrapper for Anthropic/OpenAI
* **`prompts.py`** — Prompt templates; encodes intent definitions and all behavioral constraints
* **`utils.py`** — Shared utilities

Typical flow:

`main.py` → `simulator.py` → `world.py` / `agent.py` → `llm.py` → formatted output in CLI

### Per-turn pipeline (simulator.py)

For each speaking agent each round:

1. `_select_target` — pick the agent with the strongest relationship (furthest from neutral). Fallback: last speaker.
2. `_select_intent` — map relationship state → intent label (`attack`, `defend`, `persuade`, `align`, `threaten`).
3. Compute `response_type` — `"direct_response"` if the target spoke last, else `"new_move"`.
4. Call `_line` → `_llm_line` → `agent_line_prompt` with all context.
5. Post-process output with `_trim`. Detect signals to update relationship maps.

## Development Principles

When editing this repository:

1. Keep the MVP simple and runnable.
2. Prefer small, focused changes over large rewrites.
3. Do not over-engineer abstractions too early.
4. Prioritize demo quality and CLI usability.
5. Keep output short, readable, and shareable.
6. Use mock logic first if a real LLM integration would slow down iteration.
7. Avoid modifying unrelated files unless necessary.

## Product Priorities

This repo is optimized for:

* fast iteration
* GitHub readability
* fun agent interactions
* memorable output
* future extensibility

Not optimized for:

* enterprise complexity
* premature framework design
* heavy infrastructure

## Prompt / Simulation Guidelines

Agent behavior should aim for:

* distinct personalities
* clear goals
* visible tension
* lines that target a specific agent by name
* intent that is legible in the line itself
* direct responses when the target spoke last

Avoid:

* lines that don't name the target
* generic emotional reactions with no specific reference
* intents that bleed into each other (attack ≠ threaten ≠ persuade)
* overly long speeches or narration

### Intent definitions (canonical — used in prompts)

| Intent | Required behavior |
|---|---|
| `attack` | Accuse or challenge the target. Reference something specific they did. |
| `defend` | Justify self, reject blame, or counter an accusation. |
| `persuade` | Try to change the target's mind with reasoning or pressure. |
| `align` | Show explicit support or agreement with the target. |
| `threaten` | State or imply consequences if the target does not comply. |

### Intent → relationship mapping

| Relationship state | Intents |
|---|---|
| `hostile` | `attack`, `threaten` |
| `distrustful` | `attack`, `threaten` |
| `strained` | `defend`, `persuade` |
| `neutral` | `persuade` |
| `friendly` | `align`, `persuade` |
| `aligned` | `align` |

## Environment Variables

Expected environment variables:

* `ANTHROPIC_API_KEY`
* `OPENAI_API_KEY`
* `DEFAULT_MODEL`
* `DEBUG`

See `.env.example`.

## Build History

1. Agent model
2. Mock world generation + simulation loop
3. CLI output
4. LLM wrapper
5. Agent memory (said / heard / tensions)
6. Relationship evolution (RelationshipMap + RelationshipEventLog)
7. Targeted interaction: target selection + intent system
8. Conversation memory: last_speaker + last_line + response_type
9. Prompt hardening: forced target addressing, strict intent enforcement

## Near-Term Next Steps

- Persistent world state across runs
- Web UI / shareable output
- API / SDK wrapper

## Notes

When in doubt, optimize for:

* clarity
* speed
* clean structure
* a better demo

