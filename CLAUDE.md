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
* **`simulator.py`** — Simulation loop and turn orchestration
* **`world.py`** — World generation and shared scenario context
* **`agent.py`** — Agent data models and agent-related logic
* **`llm.py`** — LLM provider wrapper for Anthropic/OpenAI
* **`prompts.py`** — Prompt templates for world and agent generation
* **`utils.py`** — Shared utilities

Typical flow:

`main.py` → `simulator.py` → `world.py` / `agent.py` → `llm.py` → formatted output in CLI

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
* occasional disagreement
* concise, punchy dialogue

Avoid:

* bland generic responses
* overly long speeches
* repetitive outputs

## Environment Variables

Expected environment variables:

* `ANTHROPIC_API_KEY`
* `OPENAI_API_KEY`
* `DEFAULT_MODEL`
* `DEBUG`

See `.env.example`.

## Near-Term Build Order

1. Agent model
2. Mock world generation
3. Mock simulation loop
4. CLI output
5. LLM wrapper
6. Prompt refinement
7. README polish

## Notes

When in doubt, optimize for:

* clarity
* speed
* clean structure
* a better demo

