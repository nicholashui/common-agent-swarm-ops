#!/usr/bin/env python3
"""Enable video production profile: agents, DNA, tools, and credentials template.

Does not embed API keys. Operators must set env vars (see credentials.env.example).

Usage:
  python scripts/business/enable_video_production.py --write
  CASOPS_VIDEO_PRODUCTION_ENABLED=true CASOPS_VIDEO_MEDIA_NETWORK=true ...
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "business" / "video"
NOW = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

# Agents that receive live media tool allow-lists when production is enabled.
MEDIA_AGENT_TOOLS: dict[str, list[str]] = {
    "video.promptengineer": ["media.stub", "media.sora", "media.veo", "media.runway"],
    "video.creativedirector": ["media.stub", "media.sora", "media.veo", "media.runway"],
    "video.archiveproducer": ["media.stub", "media.sora", "media.veo", "media.runway"],
    "video.styletransfer": ["media.stub", "media.runway", "media.veo"],
    "video.voiceover": ["media.stub", "media.elevenlabs"],
    "video.voiceclone": ["media.stub", "media.elevenlabs"],
    "video.audiobooknarrator": ["media.stub", "media.elevenlabs"],
    "video.sounddesign": ["media.stub", "media.elevenlabs"],
    "video.editor": ["media.stub", "media.runway"],
    "video.motiongraphics": ["media.stub", "media.runway"],
    "video.animator_2d": ["media.stub", "media.runway"],
    "video.orchestrator": ["media.stub"],
}


def write_profile(enabled: bool) -> Path:
    prod = VIDEO / "production"
    prod.mkdir(parents=True, exist_ok=True)
    profile = {
        "schema_version": "1.0",
        "enabled": enabled,
        "updated_at": NOW,
        "requires_env": [
            "CASOPS_VIDEO_PRODUCTION_ENABLED=true",
            "CASOPS_VIDEO_MEDIA_NETWORK=true",
            "CASOPS_MEDIA_SORA_API_KEY or OPENAI_API_KEY",
            "CASOPS_MEDIA_VEO_API_KEY or GOOGLE_API_KEY",
            "CASOPS_MEDIA_RUNWAY_API_KEY or RUNWAY_API_KEY",
            "CASOPS_MEDIA_ELEVENLABS_API_KEY or ELEVENLABS_API_KEY",
        ],
        "adapters": [
            "media.stub",
            "media.sora",
            "media.veo",
            "media.runway",
            "media.elevenlabs",
        ],
        "note": (
            "Pack-level production profile. Host still requires env flags and "
            "provider credentials before live network calls succeed."
        ),
    }
    path = prod / "profile.json"
    path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    return path


def write_credentials_example() -> Path:
    path = VIDEO / "production" / "credentials.env.example"
    path.write_text(
        "# Copy to a secrets store or local .env (never commit real keys).\n"
        "CASOPS_VIDEO_PRODUCTION_ENABLED=true\n"
        "CASOPS_VIDEO_MEDIA_NETWORK=true\n"
        "\n"
        "# Provider credentials (set the ones you use)\n"
        "CASOPS_MEDIA_SORA_API_KEY=\n"
        "# or OPENAI_API_KEY=\n"
        "CASOPS_MEDIA_VEO_API_KEY=\n"
        "# or GOOGLE_API_KEY=\n"
        "CASOPS_MEDIA_RUNWAY_API_KEY=\n"
        "# or RUNWAY_API_KEY=\n"
        "CASOPS_MEDIA_ELEVENLABS_API_KEY=\n"
        "# or ELEVENLABS_API_KEY=\n"
        "\n"
        "# Optional endpoint overrides (must be https, or http://localhost for mocks)\n"
        "# CASOPS_MEDIA_SORA_ENDPOINT=https://api.openai.com/v1/videos\n"
        "# CASOPS_MEDIA_VEO_ENDPOINT=https://generativelanguage.googleapis.com/v1beta/models\n"
        "# CASOPS_MEDIA_RUNWAY_ENDPOINT=https://api.dev.runwayml.com/v1/image_to_video\n"
        "# CASOPS_MEDIA_ELEVENLABS_ENDPOINT=https://api.elevenlabs.io/v1/text-to-speech\n",
        encoding="utf-8",
    )
    return path


def enable_agent_specs() -> int:
    n = 0
    for agent_id, tools in MEDIA_AGENT_TOOLS.items():
        path = VIDEO / "agents" / agent_id / "agent_spec.json"
        if not path.is_file():
            continue
        spec = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            continue
        spec["production_activation_requested"] = True
        spec["allowed_tools"] = tools
        model = spec.get("model_policy") if isinstance(spec.get("model_policy"), dict) else {}
        model = dict(model)
        model["network_access"] = True
        model["provider"] = "media_host"
        model["model_id"] = model.get("model_id") or "media-host-v1"
        spec["model_policy"] = model
        budget = spec.get("budget_policy") if isinstance(spec.get("budget_policy"), dict) else {}
        budget = dict(budget)
        budget["max_tool_requests"] = max(int(budget.get("max_tool_requests") or 0), 4)
        spec["budget_policy"] = budget
        path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        n += 1
    return n


def enable_dna_production_ready() -> int:
    n = 0
    for path in (VIDEO / "workflows").glob("*.dna.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue
        data["production_ready"] = True
        # Allow media tools on adapted graphs when production profile is on
        data["allowed_tools"] = [
            "media.stub",
            "media.sora",
            "media.veo",
            "media.runway",
            "media.elevenlabs",
        ]
        # Attach media tools to media-ish nodes
        nodes = data.get("nodes")
        tool_slots = 0
        if isinstance(nodes, list):
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                agent = str(node.get("agent_id") or "")
                if agent in MEDIA_AGENT_TOOLS:
                    node["tool_ids"] = list(MEDIA_AGENT_TOOLS[agent])
                tool_slots += len(node.get("tool_ids") or [])
        budget = data.get("execution_budget") if isinstance(data.get("execution_budget"), dict) else {}
        budget = dict(budget)
        # Host validator requires max_tool_requests >= declared node tool_ids count
        budget["max_tool_requests"] = max(int(budget.get("max_tool_requests") or 0), tool_slots, 16)
        data["execution_budget"] = budget
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        n += 1
    return n


def enable_pack_spine() -> None:
    """Keep pack_spine as the sole safe stub (production_ready false, media.stub only).

    Live media tools are attached to production DNA workflows, not the baseline spine.
    """
    path = VIDEO / "workflows" / "pack_spine.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return
    # pack_spine pattern forbids production_ready key entirely
    data.pop("production_ready", None)
    data.pop("allowed_tools", None)
    budget = data.get("execution_budget") if isinstance(data.get("execution_budget"), dict) else {}
    budget = dict(budget)
    budget["max_tool_requests"] = max(int(budget.get("max_tool_requests") or 0), 1)
    data["execution_budget"] = budget
    for node in data.get("nodes") or []:
        if not isinstance(node, dict):
            continue
        if node.get("id") == "media-stub" or node.get("agent_id") == "video.promptengineer":
            node["tool_ids"] = ["media.stub"]
            node["agent_id"] = "video.promptengineer"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_manifest_tools() -> None:
    path = VIDEO / "manifest.json"
    if not path.is_file():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return
    agents = data.get("agents")
    if not isinstance(agents, list):
        return
    for entry in agents:
        if not isinstance(entry, dict):
            continue
        agent_id = str(entry.get("agent_id") or "")
        if agent_id in MEDIA_AGENT_TOOLS:
            entry["allowed_tools"] = list(MEDIA_AGENT_TOOLS[agent_id])
    # Pack-level production flag remains false in manifest; profile.json is authority
    data["production_activation_requested"] = False
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_docs() -> None:
    (VIDEO / "production" / "PRODUCTION.md").write_text(
        "# Video production activation\n\n"
        f"Updated: {NOW}\n\n"
        "## What was enabled\n\n"
        "- Pack production profile: `production/profile.json` (`enabled: true`)\n"
        "- DNA / pack graphs: `production_ready: true` under `workflows/`\n"
        "- Media agents: `production_activation_requested: true` + live tool allow-lists\n"
        "- Host adapters: `media.sora`, `media.veo`, `media.runway`, `media.elevenlabs`\n\n"
        "## Required environment (host)\n\n"
        "```bash\n"
        "export CASOPS_VIDEO_PRODUCTION_ENABLED=true\n"
        "export CASOPS_VIDEO_MEDIA_NETWORK=true\n"
        "export CASOPS_MEDIA_SORA_API_KEY=...     # or OPENAI_API_KEY\n"
        "export CASOPS_MEDIA_VEO_API_KEY=...      # or GOOGLE_API_KEY\n"
        "export CASOPS_MEDIA_RUNWAY_API_KEY=...   # or RUNWAY_API_KEY\n"
        "export CASOPS_MEDIA_ELEVENLABS_API_KEY=... # or ELEVENLABS_API_KEY\n"
        "```\n\n"
        "See `credentials.env.example`. **Never commit real secrets.**\n\n"
        "## Behavior\n\n"
        "| Condition | Result |\n"
        "|-----------|--------|\n"
        "| Profile off or env off | Media adapters return `media_production_disabled` |\n"
        "| Missing API key | `media_credentials_not_configured` |\n"
        "| Enabled + key + network | Host POSTs to provider endpoint |\n\n"
        "## Safety\n\n"
        "- Credentials only from environment (or injected secret source in tests).\n"
        "- Endpoints must be https (or localhost http for mocks).\n"
        "- Inventory allows production agent fields only while profile.enabled is true.\n",
        encoding="utf-8",
    )
    tools_md = VIDEO / "tools" / "adapters.md"
    tools_md.write_text(
        "# Video tools\n\n"
        "## Local stub\n\n"
        "| tool_id | Adapter | Notes |\n"
        "|---------|---------|-------|\n"
        "| `media.stub` | StubMediaAdapter | Deterministic local stub |\n\n"
        "## Live media (production profile)\n\n"
        "| tool_id | Provider | Credential env |\n"
        "|---------|----------|----------------|\n"
        "| `media.sora` | OpenAI Sora-compatible | `CASOPS_MEDIA_SORA_API_KEY` / `OPENAI_API_KEY` |\n"
        "| `media.veo` | Google Veo / Generative Language | `CASOPS_MEDIA_VEO_API_KEY` / `GOOGLE_API_KEY` |\n"
        "| `media.runway` | Runway | `CASOPS_MEDIA_RUNWAY_API_KEY` / `RUNWAY_API_KEY` |\n"
        "| `media.elevenlabs` | ElevenLabs TTS | `CASOPS_MEDIA_ELEVENLABS_API_KEY` / `ELEVENLABS_API_KEY` |\n\n"
        "Registered via `default_local_adapters()` → `default_live_media_adapters()`.\n"
        "Network calls require `CASOPS_VIDEO_PRODUCTION_ENABLED` + pack `production/profile.json`.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Apply production enablement to the pack")
    parser.add_argument("--disable", action="store_true", help="Write profile enabled=false only")
    args = parser.parse_args()
    if not args.write and not args.disable:
        print("Pass --write to enable production pack, or --disable to turn profile off.")
        return 2
    if args.disable:
        path = write_profile(False)
        print(json.dumps({"profile": str(path), "enabled": False}, indent=2))
        return 0

    profile = write_profile(True)
    creds = write_credentials_example()
    agents = enable_agent_specs()
    dna = enable_dna_production_ready()
    enable_pack_spine()
    update_manifest_tools()
    write_docs()
    print(
        json.dumps(
            {
                "enabled": True,
                "profile": str(profile.relative_to(ROOT)),
                "credentials_example": str(creds.relative_to(ROOT)),
                "agents_updated": agents,
                "dna_updated": dna,
                "next": [
                    "export CASOPS_VIDEO_PRODUCTION_ENABLED=true",
                    "export CASOPS_VIDEO_MEDIA_NETWORK=true",
                    "export provider API keys from credentials.env.example",
                    "restart backend so default_local_adapters loads live media tools",
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
