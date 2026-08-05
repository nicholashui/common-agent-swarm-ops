"""Catalog of Host offline skill foundations for product discoverability."""

from __future__ import annotations

from typing import Any

HOST_SKILLS: list[dict[str, Any]] = [
    {
        "skill_id": "aesthetics",
        "title": "Aesthetics Agent",
        "api_prefix": "/api/v1/aesthetics",
        "tools": ["aesthetics.evaluate", "aesthetics.compare"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "rag",
        "title": "Agentic RAG",
        "api_prefix": "/api/v1/rag",
        "tools": ["rag.query", "rag.ingest"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "agent_loop_v3",
        "title": "Agent Loop v3",
        "api_prefix": "/api/v1/agent-loops",
        "tools": [],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "knowledge",
        "title": "Knowledge Router",
        "api_prefix": "/api/v1/knowledge",
        "tools": ["knowledge.route"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "research",
        "title": "Research Agent",
        "api_prefix": "/api/v1/research",
        "tools": ["research.query"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "thinking",
        "title": "Thinking Models",
        "api_prefix": "/api/v1/thinking",
        "tools": ["thinking.recommend"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "intent",
        "title": "Intent Analysis (DIA lite)",
        "api_prefix": "/api/v1/intent",
        "tools": ["intent.analyze"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "optimization",
        "title": "Optimization Agent",
        "api_prefix": "/api/v1/optimization",
        "tools": ["optimization.recommend"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "creative",
        "title": "General Creative Agent",
        "api_prefix": "/api/v1/creative",
        "tools": ["creative.ideate", "creative.patterns"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "complex_problem",
        "title": "Complex Problem Process",
        "api_prefix": "/api/v1/complex-problem",
        "tools": ["complex_problem.solve"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "strategic",
        "title": "Strategic Goals",
        "api_prefix": "/api/v1/strategic",
        "tools": ["strategic.plan"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "llm_usage",
        "title": "LLM Usage Policy",
        "api_prefix": "/api/v1/llm-usage",
        "tools": ["llm_usage.record"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "psychology",
        "title": "Psychological Profile / Recommend",
        "api_prefix": "/api/v1/psychology",
        "tools": ["psychology.profile", "psychology.recommend"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "coding",
        "title": "Coding Agent (plan-only)",
        "api_prefix": "/api/v1/coding",
        "tools": ["coding.plan"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "podcast",
        "title": "Podcast / Audio Outline",
        "api_prefix": "/api/v1/podcast",
        "tools": ["podcast.outline"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "screenwriting",
        "title": "Screenwriting Strategic Beats",
        "api_prefix": "/api/v1/screenwriting",
        "tools": ["screenwriting.plan"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "tech_radar",
        "title": "Video Gen Tech Radar",
        "api_prefix": "/api/v1/tech-radar",
        "tools": ["tech_radar.advise"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "lqr",
        "title": "LQR Workflow Overview",
        "api_prefix": "/api/v1/lqr",
        "tools": ["lqr.overview"],
        "status": "host_offline_foundation",
    },
    {
        "skill_id": "skill_evals",
        "title": "Skill Golden Evals",
        "api_prefix": "/api/v1/skill-evals",
        "tools": ["skill_evals.run"],
        "status": "host_offline_foundation",
    },
]


def list_host_skills() -> dict[str, Any]:
    return {
        "items": list(HOST_SKILLS),
        "count": len(HOST_SKILLS),
        "activation_policy": {
            "production_media": False,
            "network": False,
            "mode": "offline_host_foundations",
            "note": "Catalog of process-local Host skill APIs only.",
        },
    }
