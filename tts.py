#!/usr/bin/env python3
import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

ENV_DIR = Path(__file__).parent
load_dotenv(dotenv_path=ENV_DIR / ".env")

DEFAULT_ENDPOINT = "https://api.minimax.io/v1/t2a_v2"
LAST_TTS_REQUEST_AT: float | None = None


@dataclass
class MiniMaxTTSConfig:
    voice_id: str = "Cantonese_GentleLady"
    model: str = "speech-2.6-turbo"
    output: Path = Path("output.mp3")
    audio_format: str = "mp3"
    response_format: str = "hex"
    speed: float = 1.0
    volume: float = 1.0
    pitch: int = 0
    emotion: str | None = "fluent"
    language_boost: str | None = "Chinese,Yue"
    sample_rate: int = 32000
    bitrate: int = 128000
    channel: int = 1
    timeout: int = 120


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def ensure_success(payload: dict[str, Any]) -> None:
    base_resp = payload.get("base_resp") or {}
    status_code = first_non_empty(
        base_resp.get("status_code"),
        base_resp.get("code"),
        payload.get("status_code"),
        payload.get("code"),
    )
    if status_code in (None, 0, "0"):
        return

    message = first_non_empty(
        base_resp.get("status_msg"),
        base_resp.get("message"),
        payload.get("message"),
        payload.get("msg"),
        "MiniMax returned an unknown error.",
    )
    raise RuntimeError(f"MiniMax API error {status_code}: {message}")


def build_request(text: str, config: MiniMaxTTSConfig) -> dict[str, Any]:
    voice_setting: dict[str, Any] = {
        "voice_id": config.voice_id,
        "speed": config.speed,
        "vol": config.volume,
        "pitch": config.pitch,
    }
    if config.emotion:
        voice_setting["emotion"] = config.emotion

    audio_setting: dict[str, Any] = {
        "audio_sample_rate": config.sample_rate,
        "format": config.audio_format,
        "channel": config.channel,
    }
    if config.audio_format == "mp3":
        audio_setting["bitrate"] = config.bitrate

    payload: dict[str, Any] = {
        "model": config.model,
        "text": text,
        "stream": False,
        "output_format": config.response_format,
        "voice_setting": voice_setting,
        "audio_setting": audio_setting,
    }
    if config.language_boost:
        payload["language_boost"] = config.language_boost
    return payload


def throttle_tts_requests() -> None:
    global LAST_TTS_REQUEST_AT

    delay_seconds = float(os.getenv("MINIMAX_REQUEST_DELAY_SECONDS", "5"))
    if delay_seconds <= 0:
        return

    if LAST_TTS_REQUEST_AT is not None:
        elapsed = time.monotonic() - LAST_TTS_REQUEST_AT
        remaining = delay_seconds - elapsed
        if remaining > 0:
            print(f"Waiting {remaining:.1f}s before next TTS request...")
            time.sleep(remaining)


def is_tpm_rate_limit(payload: dict[str, Any]) -> bool:
    base_resp = payload.get("base_resp") or {}
    status_code = first_non_empty(
        base_resp.get("status_code"),
        base_resp.get("code"),
        payload.get("status_code"),
        payload.get("code"),
    )
    message = str(
        first_non_empty(
            base_resp.get("status_msg"),
            base_resp.get("message"),
            payload.get("message"),
            payload.get("msg"),
            "",
        )
    ).lower()
    return str(status_code) == "1039" or "rate limit exceeded" in message or "tpm" in message


def audio_bytes_from_hex(data: dict[str, Any]) -> bytes:
    audio_hex = first_non_empty(
        data.get("audio"),
        data.get("audio_hex"),
        data.get("audio_data"),
        data.get("hex"),
    )
    if not isinstance(audio_hex, str):
        raise RuntimeError(
            f"Could not find hex audio data in response. Keys: {sorted(data.keys())}"
        )
    return bytes.fromhex(audio_hex)


def audio_bytes_from_url(data: dict[str, Any], timeout: int) -> bytes:
    audio_url = first_non_empty(
        data.get("audio"),
        data.get("audio_url"),
        data.get("url"),
    )
    if not isinstance(audio_url, str):
        raise RuntimeError(
            f"Could not find audio URL in response. Keys: {sorted(data.keys())}"
        )

    response = requests.get(audio_url, timeout=timeout)
    response.raise_for_status()
    return response.content


def extract_audio_bytes(
    data: dict[str, Any], response_format: str, timeout: int
) -> bytes:
    if response_format == "hex":
        return audio_bytes_from_hex(data)
    return audio_bytes_from_url(data, timeout)


def request_audio_result(text: str, config: MiniMaxTTSConfig) -> dict[str, Any]:
    global LAST_TTS_REQUEST_AT

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        raise RuntimeError("Set MINIMAX_API_KEY in your environment or .env file.")

    if not text:
        raise RuntimeError("Input text is empty.")

    endpoint = os.getenv("MINIMAX_TTS_URL", DEFAULT_ENDPOINT)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = build_request(text, config)
    max_retries = int(os.getenv("MINIMAX_RATE_LIMIT_RETRIES", "5"))
    retry_delay_seconds = float(os.getenv("MINIMAX_RETRY_DELAY_SECONDS", "10"))
    retry_delay_step_seconds = float(os.getenv("MINIMAX_RETRY_DELAY_STEP_SECONDS", "5"))

    for attempt in range(max_retries + 1):
        throttle_tts_requests()

        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=config.timeout,
        )
        LAST_TTS_REQUEST_AT = time.monotonic()
        response.raise_for_status()

        result = response.json()
        if is_tpm_rate_limit(result):
            if attempt >= max_retries:
                ensure_success(result)
            wait_seconds = retry_delay_seconds + (attempt * retry_delay_step_seconds)
            print(
                f"MiniMax TPM rate limit hit, retrying in {wait_seconds:.1f}s "
                f"(attempt {attempt + 1}/{max_retries + 1})..."
            )
            time.sleep(wait_seconds)
            continue

        ensure_success(result)

        data = result.get("data")
        if not isinstance(data, dict):
            raise RuntimeError(
                f"MiniMax response did not include a data object: {json.dumps(result)}"
            )
        return result

    raise RuntimeError("MiniMax request failed after retries.")


def split_text_for_tts(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    def append_piece(piece: str) -> None:
        nonlocal current
        piece = piece.strip()
        if not piece:
            return
        candidate = f"{current}\n\n{piece}" if current else piece
        if len(candidate) <= max_chars:
            current = candidate
            return
        flush()
        if len(piece) <= max_chars:
            current = piece
            return

        sentence_parts = re.split(r"(?<=[.!?。！？])\s+", piece)
        if len(sentence_parts) > 1:
            for part in sentence_parts:
                append_piece(part)
            return

        words = piece.split()
        if len(words) > 1:
            line = ""
            for word in words:
                candidate_line = f"{line} {word}".strip()
                if len(candidate_line) <= max_chars:
                    line = candidate_line
                else:
                    if line:
                        chunks.append(line)
                    line = word
            if line:
                chunks.append(line)
            return

        for start in range(0, len(piece), max_chars):
            chunks.append(piece[start : start + max_chars])

    for paragraph in re.split(r"\n\s*\n", text.strip()):
        append_piece(paragraph)

    flush()
    return chunks or [text]


def generate_audio(text: str, config: MiniMaxTTSConfig) -> None:
    max_text_length = int(os.getenv("MINIMAX_MAX_TEXT_LENGTH", "3000"))
    chunks = split_text_for_tts(text, max_text_length)
    audio_parts: list[bytes] = []

    config.output.parent.mkdir(parents=True, exist_ok=True)
    for index, chunk in enumerate(chunks, start=1):
        if len(chunks) > 1:
            print(f"Sending TTS chunk {index}/{len(chunks)} ({len(chunk)} chars)")
        result = request_audio_result(chunk, config)
        audio_parts.append(
            extract_audio_bytes(result["data"], config.response_format, config.timeout)
        )

    config.output.write_bytes(b"".join(audio_parts))
    print(f"Saved audio to: {config.output}")


def default_output_path(input_path: Path) -> Path:
    if input_path.suffix:
        return input_path.with_suffix(".mp3")
    return input_path.parent / f"{input_path.name}.mp3"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a text file to Cantonese MP3 using MiniMax TTS."
    )
    parser.add_argument("input_file", type=Path, help="Path to the input text file.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to the output MP3 file. Defaults to the input filename with .mp3.",
    )
    parser.add_argument(
        "--voice-id",
        default="Cantonese_GentleLady",
        help="MiniMax Cantonese voice ID.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed multiplier.",
    )
    parser.add_argument(
        "--no-leading-pause",
        action="store_true",
        help="Do not prepend the <#0.5#> pause marker used in the existing script.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    input_path = args.input_file.resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8").strip()
    if not text:
        raise RuntimeError(f"Input file is empty: {input_path}")

    full_input = text if args.no_leading_pause else "\n".join(["<#0.5#>", text])
    output_path = (args.output or default_output_path(input_path)).resolve()

    config = MiniMaxTTSConfig(
        output=output_path,
        voice_id=args.voice_id,
        speed=args.speed,
    )
    generate_audio(full_input, config)


if __name__ == "__main__":
    main()
