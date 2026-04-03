"""Minimal FastAPI web UI for life-ai.

Run with:
    uvicorn life_ai.web:app --reload

JSON API endpoints (see /docs for interactive schema):
    POST /api/run   — start a fresh simulation
    POST /api/load  — resume a saved simulation
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from life_ai.persistence import load_state, save_state
from life_ai.sdk import resume_simulation, run_simulation
from life_ai.simulator import simulate

BASE_DIR = Path(__file__).parent.parent
SAVES_DIR = BASE_DIR / "saves"

app = FastAPI(title="life-ai")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _saves() -> list[str]:
    if not SAVES_DIR.exists():
        return []
    return sorted(p.stem for p in SAVES_DIR.glob("*.json"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"saves": _saves()},
    )


@app.post("/run", response_class=HTMLResponse)
async def run(
    request: Request,
    idea: str = Form(...),
    rounds: int = Form(3),
    debug: Optional[str] = Form(None),
    save_name: Optional[str] = Form(None),
) -> HTMLResponse:
    debug_bool = debug is not None
    log, state = simulate(idea=idea, rounds=rounds, debug=debug_bool)

    saved_to: Optional[str] = None
    name = (save_name or "").strip()
    if name:
        os.makedirs(SAVES_DIR, exist_ok=True)
        save_state(state, str(SAVES_DIR / f"{name}.json"))
        saved_to = name

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "idea": idea,
            "rounds": rounds,
            "debug": debug_bool,
            "log": log,
            "world": state.world,
            "saved_to": saved_to,
            "saves": _saves(),
        },
    )


@app.post("/load", response_class=HTMLResponse)
async def load(
    request: Request,
    save_name: str = Form(...),
    rounds: int = Form(3),
    debug: Optional[str] = Form(None),
) -> HTMLResponse:
    debug_bool = debug is not None
    state = load_state(str(SAVES_DIR / f"{save_name}.json"))
    log, state = simulate(rounds=rounds, debug=debug_bool, state=state)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "idea": state.world.idea,
            "rounds": rounds,
            "debug": debug_bool,
            "log": log,
            "world": state.world,
            "saves": _saves(),
        },
    )


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------

class RunRequest(BaseModel):
    idea: str
    rounds: int = 3
    debug: bool = False
    save: Optional[str] = None


class LoadRequest(BaseModel):
    load: str
    rounds: int = 3
    debug: bool = False
    save: Optional[str] = None


class ApiResponse(BaseModel):
    world: dict
    agents: list[dict]
    relationships: dict[str, dict[str, str]]
    current_day: int
    log: list[dict]


@app.post("/api/run", response_model=ApiResponse)
async def api_run(body: RunRequest) -> dict:
    """Start a fresh simulation and return structured JSON.

    Pass ``save`` to persist the final state for later resumption via ``/api/load``.
    """
    result = run_simulation(
        idea=body.idea,
        rounds=body.rounds,
        debug=body.debug,
        save=body.save,
    )
    return result


@app.post("/api/load", response_model=ApiResponse)
async def api_load(body: LoadRequest) -> dict:
    """Resume a saved simulation and return structured JSON.

    ``load`` must match the ``save`` name used in a prior ``/api/run`` call
    (or the CLI ``--save`` flag).  The updated state is written back to the
    same save file unless ``save`` overrides the destination.
    """
    try:
        result = resume_simulation(
            load=body.load,
            rounds=body.rounds,
            debug=body.debug,
            save=body.save,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result
