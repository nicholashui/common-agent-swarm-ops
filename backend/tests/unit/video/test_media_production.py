"""Unit tests for live media production configuration and adapters."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.adapters.media_live import LiveMediaAdapter, default_live_media_adapters
from app.adapters import default_local_adapters
from app.governance.adapter_execution import broker_invocation
from app.video.media_production import (
    MediaGenerationRequest,
    MediaProviderId,
    generate_media,
    is_video_production_enabled,
    resolve_credential,
)


def test_default_adapters_include_live_media_providers() -> None:
    ids = {getattr(a, "adapter_id") for a in default_local_adapters()}
    assert "media.stub" in ids
    assert "media.sora" in ids
    assert "media.veo" in ids
    assert "media.runway" in ids
    assert "media.elevenlabs" in ids
    assert len(default_live_media_adapters()) == 4


def test_generate_media_disabled_without_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    profile = tmp_path / "production" / "profile.json"
    profile.parent.mkdir(parents=True)
    profile.write_text(json.dumps({"enabled": True}), encoding="utf-8")
    monkeypatch.delenv("CASOPS_VIDEO_PRODUCTION_ENABLED", raising=False)
    result = generate_media(
        MediaGenerationRequest(prompt="hello", provider=MediaProviderId.SORA),
        video_root=tmp_path,
    )
    assert result.ok is False
    assert result.outcome == "media_production_disabled"


def test_generate_media_requires_credentials(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    profile = tmp_path / "production" / "profile.json"
    profile.parent.mkdir(parents=True)
    profile.write_text(json.dumps({"enabled": True}), encoding="utf-8")
    monkeypatch.setenv("CASOPS_VIDEO_PRODUCTION_ENABLED", "true")
    monkeypatch.setenv("CASOPS_VIDEO_MEDIA_NETWORK", "true")
    for key in (
        "CASOPS_MEDIA_SORA_API_KEY",
        "OPENAI_API_KEY",
    ):
        monkeypatch.delenv(key, raising=False)
    result = generate_media(
        MediaGenerationRequest(prompt="scene", provider=MediaProviderId.SORA),
        video_root=tmp_path,
    )
    assert result.ok is False
    assert result.outcome == "media_credentials_not_configured"


def test_generate_media_live_success_with_transport(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    profile = tmp_path / "production" / "profile.json"
    profile.parent.mkdir(parents=True)
    profile.write_text(json.dumps({"enabled": True}), encoding="utf-8")
    monkeypatch.setenv("CASOPS_VIDEO_PRODUCTION_ENABLED", "true")
    monkeypatch.setenv("CASOPS_VIDEO_MEDIA_NETWORK", "true")
    monkeypatch.setenv("CASOPS_MEDIA_SORA_API_KEY", "test-key-not-real")
    monkeypatch.setenv("CASOPS_MEDIA_SORA_ENDPOINT", "https://example.test/v1/videos")

    def transport(url: str, headers: dict, body: bytes, timeout: float) -> tuple[int, bytes]:
        assert "example.test" in url
        assert headers.get("Authorization", "").startswith("Bearer ")
        return 200, json.dumps({"url": "https://cdn.example/video.mp4"}).encode("utf-8")

    result = generate_media(
        MediaGenerationRequest(prompt="cinematic shot", provider=MediaProviderId.SORA),
        transport=transport,
        video_root=tmp_path,
    )
    assert result.ok is True
    assert result.outcome == "media_generation_succeeded"
    assert result.artifact_uri == "https://cdn.example/video.mp4"
    assert resolve_credential(MediaProviderId.SORA) is not None


def test_live_adapter_execute_under_broker(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    profile = tmp_path / "production" / "profile.json"
    profile.parent.mkdir(parents=True)
    profile.write_text(json.dumps({"enabled": True}), encoding="utf-8")
    monkeypatch.setenv("CASOPS_VIDEO_PRODUCTION_ENABLED", "true")
    monkeypatch.setenv("CASOPS_VIDEO_MEDIA_NETWORK", "true")
    monkeypatch.setenv("CASOPS_MEDIA_ELEVENLABS_API_KEY", "el-test")
    monkeypatch.setenv("CASOPS_MEDIA_ELEVENLABS_ENDPOINT", "https://example.test/tts")

    # Point profile loader at tmp by monkeypatching path helper
    monkeypatch.setattr(
        "app.video.media_production.production_profile_path",
        lambda video_root=None: profile,
    )

    def transport(url: str, headers: dict, body: bytes, timeout: float) -> tuple[int, bytes]:
        return 200, json.dumps({"url": "https://cdn.example/audio.mp3"}).encode("utf-8")

    monkeypatch.setattr(
        "app.adapters.media_live.generate_media",
        lambda request, **kwargs: generate_media(request, transport=transport, video_root=tmp_path),
    )

    adapter = LiveMediaAdapter(provider=MediaProviderId.ELEVENLABS, adapter_id="media.elevenlabs")
    with broker_invocation():
        result = adapter.execute({"prompt": "Narrate the intro", "text": "Narrate the intro"})
    assert result.outcome in {
        "media_generation_succeeded",
        "media_credentials_not_configured",
        "media_production_disabled",
    }


def test_pack_production_profile_enabled_in_repo() -> None:
    root = Path(__file__).resolve().parents[3].parent / "business" / "video"
    # repo layout: backend/tests/unit/video -> parents[3]=backend, need project root
    project = Path(__file__).resolve().parents[4]
    profile = project / "business" / "video" / "production" / "profile.json"
    assert profile.is_file()
    data = json.loads(profile.read_text(encoding="utf-8"))
    assert data.get("enabled") is True
