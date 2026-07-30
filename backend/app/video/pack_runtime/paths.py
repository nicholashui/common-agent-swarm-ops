"""Resolve video pack roots relative to the monorepo."""

from __future__ import annotations

from pathlib import Path

# backend/app/video/pack_runtime/paths.py → repo root is parents[4]
REPO_ROOT = Path(__file__).resolve().parents[4]
VIDEO_PACK_ROOT = REPO_ROOT / "business" / "video"
AGENTS_ROOT = VIDEO_PACK_ROOT / "agents"
EVALS_AGENTS_ROOT = VIDEO_PACK_ROOT / "evals" / "agents"
SPECIAL_SKILLS_ROOT = VIDEO_PACK_ROOT / "special_skills"

SPINE_AGENT_IDS: tuple[str, ...] = (
    "video.orchestrator",
    "video.planner",
    "video.router",
    "video.judge",
    "video.gatekeeper",
    "video.critic",
    "video.memory",
)
