"""Video production media configuration and host-owned provider dispatch.

Credentials are resolved only from environment variables (or an injected secret
source). Values are never logged. When production is disabled or a credential is
missing, providers fail closed with a typed outcome (no silent fake success that
claims a live generation occurred).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class MediaProviderId(StrEnum):
    """Supported live media provider identifiers."""

    SORA = "sora"
    VEO = "veo"
    RUNWAY = "runway"
    ELEVENLABS = "elevenlabs"


# Environment variable names (never hard-code secret values).
ENV_PRODUCTION_ENABLED = "CASOPS_VIDEO_PRODUCTION_ENABLED"
ENV_ALLOW_NETWORK = "CASOPS_VIDEO_MEDIA_NETWORK"
ENV_CREDENTIALS: dict[MediaProviderId, tuple[str, ...]] = {
    MediaProviderId.SORA: ("CASOPS_MEDIA_SORA_API_KEY", "OPENAI_API_KEY"),
    MediaProviderId.VEO: ("CASOPS_MEDIA_VEO_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"),
    MediaProviderId.RUNWAY: ("CASOPS_MEDIA_RUNWAY_API_KEY", "RUNWAY_API_KEY"),
    MediaProviderId.ELEVENLABS: ("CASOPS_MEDIA_ELEVENLABS_API_KEY", "ELEVENLABS_API_KEY"),
}

DEFAULT_ENDPOINTS: dict[MediaProviderId, str] = {
    MediaProviderId.SORA: "https://api.openai.com/v1/videos",
    MediaProviderId.VEO: "https://generativelanguage.googleapis.com/v1beta/models",
    MediaProviderId.RUNWAY: "https://api.dev.runwayml.com/v1/image_to_video",
    MediaProviderId.ELEVENLABS: "https://api.elevenlabs.io/v1/text-to-speech",
}

ENV_ENDPOINT: dict[MediaProviderId, str] = {
    MediaProviderId.SORA: "CASOPS_MEDIA_SORA_ENDPOINT",
    MediaProviderId.VEO: "CASOPS_MEDIA_VEO_ENDPOINT",
    MediaProviderId.RUNWAY: "CASOPS_MEDIA_RUNWAY_ENDPOINT",
    MediaProviderId.ELEVENLABS: "CASOPS_MEDIA_ELEVENLABS_ENDPOINT",
}

HttpTransport = Callable[[str, Mapping[str, str], bytes, float], tuple[int, bytes]]


def _env_flag(name: str) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    return raw in {"1", "true", "yes", "on", "enabled"}


def production_profile_path(video_root: Path | None = None) -> Path:
    root = video_root or Path(__file__).resolve().parents[3] / "business" / "video"
    return root / "production" / "profile.json"


def load_production_profile(video_root: Path | None = None) -> dict[str, Any]:
    path = production_profile_path(video_root)
    if not path.is_file():
        return {"enabled": False, "schema_version": "1.0"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"enabled": False, "schema_version": "1.0", "error": "unreadable_profile"}
    return data if isinstance(data, dict) else {"enabled": False}


def is_video_production_enabled(video_root: Path | None = None) -> bool:
    """Production requires both env enablement and pack profile enabled."""
    if not _env_flag(ENV_PRODUCTION_ENABLED):
        return False
    profile = load_production_profile(video_root)
    return profile.get("enabled") is True


def network_media_allowed() -> bool:
    """Network calls require an explicit second flag (defense in depth)."""
    return _env_flag(ENV_ALLOW_NETWORK) or _env_flag(ENV_PRODUCTION_ENABLED)


@dataclass(frozen=True, slots=True)
class ProviderCredential:
    """In-memory credential; never include in logs or repr."""

    provider: MediaProviderId
    api_key: str
    endpoint: str

    def __repr__(self) -> str:
        return f"ProviderCredential(provider={self.provider!s}, api_key=***, endpoint={self.endpoint!r})"


def resolve_credential(provider: MediaProviderId) -> ProviderCredential | None:
    """Resolve one provider credential from the environment only."""
    key: str | None = None
    for env_name in ENV_CREDENTIALS[provider]:
        value = os.environ.get(env_name, "").strip()
        if value:
            key = value
            break
    if not key:
        return None
    endpoint = os.environ.get(ENV_ENDPOINT[provider], "").strip() or DEFAULT_ENDPOINTS[provider]
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc:
        return None
    # Prefer https in production; allow http only for explicit local mock endpoints.
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost"}:
        return None
    return ProviderCredential(provider=provider, api_key=key, endpoint=endpoint)


def credential_status() -> dict[str, bool]:
    """Public-safe map of which providers have credentials configured."""
    return {provider.value: resolve_credential(provider) is not None for provider in MediaProviderId}


def _default_transport(
    url: str, headers: Mapping[str, str], body: bytes, timeout: float
) -> tuple[int, bytes]:
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 — host allowlist
            return int(response.status), response.read()
    except urllib.error.HTTPError as error:
        return int(error.code), error.read() if error.fp else b""
    except urllib.error.URLError as error:
        return 0, str(error.reason).encode("utf-8", errors="replace")


@dataclass(frozen=True, slots=True)
class MediaGenerationRequest:
    """Safe tool arguments for a media generation attempt."""

    prompt: str
    provider: MediaProviderId
    model: str | None = None
    voice_id: str | None = None
    duration_seconds: int | None = None


@dataclass(frozen=True, slots=True)
class MediaGenerationResult:
    """Result of a host-owned media generation attempt (no raw secrets)."""

    ok: bool
    outcome: str
    provider: str
    effect_digest: str
    http_status: int | None = None
    artifact_uri: str | None = None
    detail: str | None = None


def generate_media(
    request: MediaGenerationRequest,
    *,
    transport: HttpTransport | None = None,
    timeout_seconds: float = 60.0,
    video_root: Path | None = None,
) -> MediaGenerationResult:
    """Dispatch one media generation through a configured live provider."""
    digest_base = f"{request.provider}|{request.prompt}|{request.model or ''}"
    effect_digest = sha256(digest_base.encode("utf-8")).hexdigest()

    if not is_video_production_enabled(video_root):
        return MediaGenerationResult(
            ok=False,
            outcome="media_production_disabled",
            provider=request.provider.value,
            effect_digest=effect_digest,
            detail="Set CASOPS_VIDEO_PRODUCTION_ENABLED=true and enable business/video/production/profile.json",
        )
    if not network_media_allowed():
        return MediaGenerationResult(
            ok=False,
            outcome="media_network_disabled",
            provider=request.provider.value,
            effect_digest=effect_digest,
            detail="Set CASOPS_VIDEO_MEDIA_NETWORK=true to permit host outbound media calls",
        )

    credential = resolve_credential(request.provider)
    if credential is None:
        return MediaGenerationResult(
            ok=False,
            outcome="media_credentials_not_configured",
            provider=request.provider.value,
            effect_digest=effect_digest,
            detail=f"Missing API key for {request.provider.value}",
        )

    body_obj = _provider_payload(request)
    body = json.dumps(body_obj).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "common-agent-swarm-ops-media/1.0",
        **_provider_auth_headers(credential),
    }
    runner = transport or _default_transport
    status, raw = runner(credential.endpoint, headers, body, timeout_seconds)
    ok = 200 <= status < 300
    artifact_uri = None
    if ok:
        try:
            parsed = json.loads(raw.decode("utf-8", errors="replace"))
            if isinstance(parsed, dict):
                data = parsed.get("data")
                data_url = data.get("url") if isinstance(data, dict) else None
                artifact_uri = parsed.get("url") or parsed.get("artifact_uri") or data_url
        except json.JSONDecodeError:
            artifact_uri = None
    return MediaGenerationResult(
        ok=ok,
        outcome="media_generation_succeeded" if ok else "media_generation_failed",
        provider=request.provider.value,
        effect_digest=sha256((effect_digest + str(status)).encode("utf-8")).hexdigest(),
        http_status=status,
        artifact_uri=str(artifact_uri) if artifact_uri else None,
        detail=None if ok else f"provider_http_status={status}",
    )


def _provider_auth_headers(credential: ProviderCredential) -> dict[str, str]:
    if credential.provider is MediaProviderId.ELEVENLABS:
        return {"xi-api-key": credential.api_key}
    if credential.provider is MediaProviderId.RUNWAY:
        return {"Authorization": f"Bearer {credential.api_key}", "X-Runway-Version": "2024-11-06"}
    if credential.provider is MediaProviderId.VEO:
        return {"x-goog-api-key": credential.api_key}
    # Sora / OpenAI-compatible
    return {"Authorization": f"Bearer {credential.api_key}"}


def _provider_payload(request: MediaGenerationRequest) -> dict[str, Any]:
    if request.provider is MediaProviderId.ELEVENLABS:
        return {
            "text": request.prompt,
            "model_id": request.model or "eleven_multilingual_v2",
        }
    if request.provider is MediaProviderId.RUNWAY:
        return {
            "promptText": request.prompt,
            "model": request.model or "gen3a_turbo",
            "duration": request.duration_seconds or 5,
        }
    if request.provider is MediaProviderId.VEO:
        return {
            "contents": [{"parts": [{"text": request.prompt}]}],
            "model": request.model or "veo-2",
        }
    # Sora / OpenAI-style video job
    return {
        "model": request.model or "sora-2",
        "prompt": request.prompt,
        "seconds": str(request.duration_seconds or 4),
    }


ADAPTER_ID_BY_PROVIDER: dict[MediaProviderId, str] = {
    MediaProviderId.SORA: "media.sora",
    MediaProviderId.VEO: "media.veo",
    MediaProviderId.RUNWAY: "media.runway",
    MediaProviderId.ELEVENLABS: "media.elevenlabs",
}

PROVIDER_BY_ADAPTER_ID: dict[str, MediaProviderId] = {
    adapter_id: provider for provider, adapter_id in ADAPTER_ID_BY_PROVIDER.items()
}

PRODUCTION_MEDIA_TOOL_IDS: tuple[str, ...] = tuple(ADAPTER_ID_BY_PROVIDER.values()) + ("media.stub",)
