"""Schemas for AestheticVerdict / AestheticProfile (spec §§4, 6, 7, 10)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


AESTHETIC_DIMENSIONS: tuple[str, ...] = (
    "composition",
    "color_harmony",
    "light",
    "depth",
    "subject",
    "technical",
    "emotion",
    "style_fidelity",
    "novelty",
    "temporal",
)

Mode = Literal["screen", "score", "align", "compare", "refine"]
MediaType = Literal["image", "video_clip", "frame_sequence"]
Tier = Literal["fast", "deep"]
ProfileType = Literal[
    "director",
    "brand",
    "artist",
    "audience_cohort",
    "genre_prior",
    "neutral_baseline",
]


class IntentInput(StrictModel):
    shot_intent_text: str = Field(default="", max_length=4_000)
    reference_refs: list[str] = Field(default_factory=list, max_length=32)
    genre_prior: str = Field(default="", max_length=120)


class EmotionalTarget(StrictModel):
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    arousal: float = Field(default=0.0, ge=0.0, le=1.0)


class BudgetInput(StrictModel):
    max_latency_ms: int = Field(default=800, ge=50, le=60_000)
    tier: Tier = "fast"


class ConstraintsInput(StrictModel):
    aspect_ratio: str = Field(default="", max_length=32)
    color_space: str = Field(default="", max_length=64)
    deliverable: str = Field(default="", max_length=64)


class AestheticEvaluateRequest(StrictModel):
    """§7.1 input contract (single artifact)."""

    artifact_ref: str = Field(min_length=1, max_length=500)
    media_type: MediaType = "image"
    profile_id: str | None = Field(default=None, max_length=200)
    intent: IntentInput = Field(default_factory=IntentInput)
    emotional_target: EmotionalTarget = Field(default_factory=EmotionalTarget)
    mode: Mode = "score"
    constraints: ConstraintsInput = Field(default_factory=ConstraintsInput)
    budget: BudgetInput = Field(default_factory=BudgetInput)
    # Offline harness only — live multimodal requires Host go-live.
    allow_live_vision: bool = False


class AestheticCompareRequest(StrictModel):
    """Compare / rank N candidate artifacts (§7.3 compare)."""

    candidates: list[str] = Field(min_length=2, max_length=32)
    media_type: MediaType = "image"
    profile_id: str | None = Field(default=None, max_length=200)
    intent: IntentInput = Field(default_factory=IntentInput)
    emotional_target: EmotionalTarget = Field(default_factory=EmotionalTarget)
    allow_live_vision: bool = False


class AestheticProfileCreate(StrictModel):
    profile_id: str = Field(min_length=1, max_length=200)
    owner: str = Field(default="local", max_length=200)
    profile_type: ProfileType = "neutral_baseline"
    weights: dict[str, float] = Field(default_factory=dict)
    exemplars: list[str] = Field(default_factory=list, max_length=64)
    anti_exemplars: list[str] = Field(default_factory=list, max_length=64)
    elicited_criteria: list[str] = Field(default_factory=list, max_length=64)
    consent_scope: str = Field(default="local_process", max_length=200)


class AestheticProfileRecord(StrictModel):
    profile_id: str
    owner: str
    profile_type: ProfileType
    consent: dict[str, Any]
    weights: dict[str, float]
    exemplars: list[str]
    anti_exemplars: list[str]
    elicited_criteria: list[str]
    version: int
    lineage: list[str]
    activation_policy: dict[str, Any]


class AestheticVerdict(StrictModel):
    """§7.2 output contract."""

    artifact_ref: str
    profile_id: str
    mode: Mode
    media_type: MediaType
    aesthetic_vector: dict[str, float]
    confidence: dict[str, float]
    intent_fidelity: float
    emotion_match: float
    hack_likelihood: float
    aesthetic_quality: float
    top_failing_dimensions: list[str]
    actionable_critique: list[str]
    prompt_steer_hints: list[str]
    uncertainty_flag: bool
    escalate_to_hitl: bool
    provenance: dict[str, Any]
    reward: dict[str, Any] | None = None
    preference_pairs: list[dict[str, Any]] | None = None
    activation_policy: dict[str, Any]
    note: str


class AestheticCompareResult(StrictModel):
    ranking: list[dict[str, Any]]
    best_artifact_ref: str
    profile_id: str
    activation_policy: dict[str, Any]
    note: str


ACTIVATION_POLICY: dict[str, Any] = {
    "production_media": False,
    "live_vision": False,
    "network": False,
    "dpo_training": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline Host aesthetics foundation. Live SigLIP/VLM/DPO require "
        "explicit Host go-live review — not enabled here."
    ),
}
