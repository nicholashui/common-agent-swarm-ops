"""Aesthetics Agent Host foundation (offline Critic · Aligner · Taste-Keeper).

Implements a fail-closed, deterministic subset of
``aesthetics_agent_functional_specification.md``:

- Decomposed AestheticVector (D1–D10) + gated AQ
- Modes: screen | score | align | compare | refine
- Versioned AestheticProfile store (process-local)
- Anti-hack fields (ensemble disagreement, OOD/hack likelihood)

Not included (explicit non-goals of this Host slice):
live SigLIP/VLM/network vision, DPO training loops, GPU autoscale, Redis bus.
"""

from app.aesthetics.service import AestheticsService, get_aesthetics_service

__all__ = ["AestheticsService", "get_aesthetics_service"]
