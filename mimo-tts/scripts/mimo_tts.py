#!/usr/bin/env python3
"""MiMo TTS 2.5: local keys, voice profiles, and resumable MP3 generation."""

import argparse
import base64
import binascii
import csv
import getpass
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from local_config import (COMPRESSIONS, PACES, add_voice, atomic_write, audio_info, data_dir,
                          generation_settings, key_path, load_key, reference_bytes,
                          registry, save_key, set_default_compression, set_default_pace,
                          write_registry)


API_BASES = (
    "https://api.xiaomimimo.com/v1",
    "https://token-plan-cn.xiaomimimo.com/v1",
    "https://token-plan-sgp.xiaomimimo.com/v1",
    "https://token-plan-ams.xiaomimimo.com/v1",
)
LOCALES = ("en", "en-US", "en-GB", "zh-CN", "auto")
KINDS = ("word", "sentence", "text")
INSTRUCTION_MODES = ("faithful", "educational", "neutral")
FAITHFUL_CONTEXTS = {
    "word": ("For this {language}vocabulary recording, pronounce each supplied word exactly once, "
             "in the given order, with neutral dictionary-style delivery and correct lexical stress."),
    "sentence": ("For this {language}example-sentence recording, read the supplied sentence exactly once, "
                 "preserving its words and punctuation with natural phrasing."),
    "text": "Read the supplied text exactly once, preserving its words and punctuation with neutral delivery.",
}
FAITHFUL_READING = (
    "Read only the exact text in the assistant message. Do not add any content not present in that text. "
    "Do not repeat, translate, expand or explain it. Do not read these instructions aloud. "
    "Stop immediately after the supplied text."
)
NEUTRAL_PACES = {"slow": "Slow, clear pace.", "normal": "Natural pace.",
                 "brisk": "Moderately brisk pace.", "fast": "Fast, clear pace."}
PACE_INSTRUCTIONS = {
    "slow": "Read slowly and clearly with measured phrasing, without exaggerating individual sounds.",
    "normal": ("Read at a natural, fluent everyday conversational pace, with smooth connected speech "
               "and short natural pauses. Do not read word by word or stretch vowels. "
               "Keep the selected speaker's voice while adjusting the delivery pace."),
    "brisk": ("Read at a moderately brisk conversational pace, smoothly and continuously. "
              "Use short natural pauses, avoid gaps between words and do not stretch syllables. "
              "Keep pronunciation clear and retain the selected speaker's voice."),
    "fast": ("Read at a fast, fluent conversational pace with quick connected speech and minimal pauses. "
             "Do not stretch syllables; keep every word intelligible and retain the selected speaker's voice."),
}
READING = (
    "Speak only the supplied text without adding or removing words. "
    "Do not add introductions, definitions, translations, spelling-out or background music. "
    "Use clear, natural educational pronunciation."
)
ACCENTS = {"en": "Speak in English.", "en-US": "Use a clear General American English accent.",
           "en-GB": "Use a clear standard British English accent.",
           "zh-CN": "使用标准普通话。", "auto": ""}


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def api_endpoint(key):
    explicit = os.environ.get("MIMO_TTS_API_BASE", "").rstrip("/")
    if explicit and explicit not in API_BASES:
        raise ValueError("MIMO_TTS_API_BASE must be a documented official MiMo API base")
    base = explicit or API_BASES[1 if key.startswith(("tp-", "ttp-")) else 0]
    return base + "/chat/completions"


def safe_filename(value, audio_format):
    if (not isinstance(value, str) or not value or value != value.strip() or value.endswith(".")
            or re.search(r'[<>:"/\\|?*\x00-\x1f]', value)
            or value in (".", "..")):
        raise ValueError("filename must be a single valid filename without directories")
    if re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", value):
        raise ValueError("filename is a reserved Windows device name")
    suffix = Path(value).suffix.lower()
    if suffix and suffix != "." + audio_format:
        raise ValueError("filename extension must match the MP3 output format")
    return value if suffix else value + "." + audio_format


def make_job(row, options, output=None):
    if not isinstance(row, dict) or not isinstance(row.get("text"), str) or not row["text"].strip():
        raise ValueError("Every item must contain a nonempty text string")
    text = row["text"].strip()
    kind = row.get("kind") or options.kind
    if kind not in KINDS:
        raise ValueError("kind must be word, sentence or text")
    audio_format = "mp3"
    if output and output.suffix.lower() != ".mp3":
        raise ValueError("Generated audio is fixed to MP3; output must end in .mp3")
    if options.command == "design":
        voice_name = None
        profile = {"type": "design", "locale": "en", "description": options.description}
    else:
        default, voices = registry()
        voice_name = row.get("voice") or options.voice or default
        if voice_name not in voices:
            raise ValueError(f"Unknown voice profile: {voice_name}. Run: voices list")
        profile = voices[voice_name]
    locale = row.get("locale") or options.locale or profile.get("locale", "en")
    if locale not in LOCALES:
        raise ValueError("Unsupported locale; use en, en-US, en-GB, zh-CN or auto")
    pace = row.get("pace") or options.pace or generation_settings()["pace"]
    if pace not in PACES:
        raise ValueError("pace must be slow, normal, brisk or fast")
    compression = row.get("compression") or options.compression or generation_settings()["compression"]
    if compression not in COMPRESSIONS:
        raise ValueError("compression must be original, 32k or 24k")
    style = "\n".join(filter(None, [profile.get("style", ""), row.get("style") or options.style]))
    instruction_mode = row.get("instruction_mode") or getattr(options, "instruction_mode", None) or "faithful"
    if instruction_mode not in INSTRUCTION_MODES:
        raise ValueError("instruction_mode must be faithful, educational or neutral")
    if instruction_mode == "faithful":
        language = "English " if locale.startswith("en") else ""
        english_only = "Use English pronunciation only. Do not switch languages." if language else ""
        instructions = [FAITHFUL_CONTEXTS[kind].format(language=language), english_only, ACCENTS[locale],
                        NEUTRAL_PACES[pace], FAITHFUL_READING, style]
    elif instruction_mode == "neutral":
        instructions = ["Read the supplied text once with neutral delivery.", ACCENTS[locale],
                        NEUTRAL_PACES[pace], style]
    else:
        instructions = [READING, ACCENTS[locale]]
        if kind == "word":
            instructions.append("Pronounce the whole word with its correct lexical stress.")
        elif kind == "sentence":
            instructions.append("Preserve the sentence's phrasing and punctuation with smooth connected speech.")
        instructions.append(style)
        instructions.append(PACE_INSTRUCTIONS[pace])
    audio = {"format": audio_format}
    identity = {}
    if profile["type"] == "design":
        model = "mimo-v2.5-tts-voicedesign"
        instructions.insert(0, profile["description"])
    elif profile["type"] == "preset":
        model = "mimo-v2.5-tts"
        audio["voice"] = profile["voice"]
    elif profile["type"] == "clone":
        model = "mimo-v2.5-tts-voiceclone"
        reference = reference_bytes(profile)
        identity["reference_sha256"] = hashlib.sha256(reference).hexdigest()
    else:
        raise ValueError("Unsupported voice profile type")
    instruction = "\n".join(filter(None, instructions))
    payload = {"model": model, "stream": False, "audio": audio,
               "messages": [{"role": "user", "content": instruction},
                            {"role": "assistant", "content": text}]}
    fingerprint = digest({"payload": payload, **identity})
    if compression != "original":
        fingerprint = digest({"synthesis_sha256": fingerprint,
                              "postprocess": compression_profile(compression)})
    if output is None:
        label = str(row.get("id") or text)
        slug = re.sub(r"[^\w-]+", "-", label, flags=re.UNICODE).strip("-_")[:60] or "audio"
        filename = row.get("filename") or f"{slug}-{fingerprint[:12]}.{audio_format}"
        output = Path(options.output_dir) / safe_filename(filename, audio_format)
    return {"id": row.get("id"), "text": text, "kind": kind, "locale_requested": locale,
            "voice": voice_name, "model": model, "format": audio_format, "pace": pace,
            "compression": compression,
            "instruction": instruction, "instruction_mode": instruction_mode, "request_sha256": fingerprint,
            "output": output.expanduser().resolve(), "payload": payload, "profile": profile}


def is_completed(job, overwrite):
    output = job["output"]
    existing_parent = output.parent
    while not existing_parent.exists():
        existing_parent = existing_parent.parent
    if not existing_parent.is_dir():
        raise ValueError(f"Output parent is a file: {existing_parent}")
    metadata = output.with_suffix(output.suffix + ".json")
    if not output.exists() and not metadata.exists():
        return False
    if overwrite:
        if output.is_dir() or metadata.is_dir():
            raise ValueError("An output path points to a directory")
        return False
    if output.is_file() and metadata.is_file():
        saved = json.loads(metadata.read_text(encoding="utf-8"))
        if (saved.get("request_sha256") == job["request_sha256"]
                and saved.get("audio_sha256") == hashlib.sha256(output.read_bytes()).hexdigest()):
            return True
    raise ValueError(f"Existing output is unverified or has different settings: {output}. "
                     "Choose a different output, or use --overwrite if replacement is intended.")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def synthesize(job, key, timeout):
    payload = {**job["payload"], "audio": dict(job["payload"]["audio"])}
    if job["profile"]["type"] == "clone":
        content = reference_bytes(job["profile"])
        extension = Path(job["profile"]["reference_audio"]).suffix.lower()
        mime = "audio/wav" if extension == ".wav" else "audio/mpeg"
        payload["audio"]["voice"] = f"data:{mime};base64," + base64.b64encode(content).decode("ascii")
    endpoint = api_endpoint(key)
    request = urllib.request.Request(endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"), method="POST",
        headers={"api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        hints = {400: "request rejected", 401: "API Key rejected", 403: "access denied",
                 402: "insufficient balance or unsupported plan", 429: "rate limit reached"}
        # Never print headers, credentials, or an arbitrary response body.
        hint = hints.get(error.code, "MiMo service request failed")
        raise ValueError(f"MiMo HTTP {error.code}: {hint}; no automatic retry") from None
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError("MiMo connection failed or timed out; no automatic retry") from error
    try:
        choice = result["choices"][0]
        if choice.get("finish_reason") not in (None, "stop"):
            raise ValueError("Audio generation was truncated or filtered")
        encoded = choice["message"]["audio"]["data"]
        content = base64.b64decode(encoded, validate=True)
        info = audio_info(content, job["format"])
    except (KeyError, IndexError, TypeError, binascii.Error) as error:
        raise ValueError("MiMo response did not contain valid Base64 audio") from error
    return content, {**info, "api_endpoint": endpoint, "response_id": result.get("id"),
                     "usage": result.get("usage")}


def compression_profile(compression):
    if compression not in COMPRESSIONS:
        raise ValueError("compression must be original, 32k or 24k")
    if compression == "original":
        return {"compression": "original"}
    return {"compression": compression, "codec": "libmp3lame",
            "bitrate_bps": int(compression[:-1]) * 1000, "sample_rate": 24000, "channels": 1}


def ffmpeg_run(arguments, timeout):
    try:
        return subprocess.run(arguments, check=True, capture_output=True, timeout=timeout,
                              creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    except (OSError, subprocess.SubprocessError):
        raise ValueError("FFmpeg processing failed; no output was published") from None


def require_ffmpeg():
    executable = shutil.which("ffmpeg")
    if not executable:
        raise ValueError("32k/24k compression requires FFmpeg with libmp3lame on PATH")
    encoders = ffmpeg_run([executable, "-hide_banner", "-encoders"], timeout=15)
    if b"libmp3lame" not in encoders.stdout:
        raise ValueError("This FFmpeg build does not include the libmp3lame encoder")
    return executable


def compress_mp3(content, compression, executable):
    profile = compression_profile(compression)
    if compression == "original":
        return content
    with tempfile.TemporaryDirectory(prefix="mimo-mp3-") as folder:
        source = Path(folder) / "source.mp3"
        output = Path(folder) / "compressed.mp3"
        source.write_bytes(content)
        ffmpeg_run([executable, "-nostdin", "-n", "-hide_banner", "-loglevel", "error",
                    "-i", str(source), "-map_metadata", "-1", "-vn", "-codec:a", profile["codec"],
                    "-ac", str(profile["channels"]), "-ar", str(profile["sample_rate"]),
                    "-b:a", compression, str(output)], timeout=120)
        ffmpeg_run([executable, "-nostdin", "-hide_banner", "-v", "error", "-i", str(output),
                    "-f", "null", "-"], timeout=120)
        result = output.read_bytes()
        audio_info(result, "mp3")
        return result


def postprocess_audio(content, compression, executable):
    if compression == "original":
        return content, {}
    source_info = audio_info(content, "mp3")
    result = compress_mp3(content, compression, executable)
    return result, {**audio_info(result, "mp3"), "source_bytes": source_info["bytes"],
                    "source_audio_sha256": source_info["audio_sha256"],
                    "postprocess": compression_profile(compression)}


def make_compression_job(source, output, compression):
    source = Path(source).expanduser().resolve()
    output = Path(output).expanduser().resolve()
    if source == output:
        raise ValueError("Compression output must differ from the original input file")
    if source.suffix.lower() != ".mp3" or output.suffix.lower() != ".mp3":
        raise ValueError("Compression input and output must use .mp3")
    content = source.read_bytes()
    info = audio_info(content, "mp3")
    job = {"output": output, "source_file": str(source), "source_bytes": len(content),
           "source_audio_sha256": info["audio_sha256"], "format": "mp3",
           "compression": compression, "operation": "local-compression",
           "request_sha256": digest({"source_audio_sha256": info["audio_sha256"],
                                     "postprocess": compression_profile(compression)})}
    original_metadata = source.with_suffix(".mp3.json")
    if original_metadata.is_file():
        original = json.loads(original_metadata.read_text(encoding="utf-8"))
        for key in ("text", "kind", "locale_requested", "voice", "model", "pace"):
            if key in original:
                job[key] = original[key]
        job["source_request_sha256"] = original.get("request_sha256")
    return job


def write_compression_job(job, executable, overwrite):
    content = Path(job["source_file"]).read_bytes()
    if hashlib.sha256(content).hexdigest() != job["source_audio_sha256"]:
        raise ValueError("Source audio changed after planning; run the command again")
    result, processing = postprocess_audio(content, job["compression"], executable)
    record = {**public_record(job), **audio_info(result, "mp3"), **processing,
              "status": "compressed" if job["compression"] != "original" else "copied-original",
              "created_at": datetime.now(timezone.utc).isoformat()}
    record.pop("skip", None)
    output = job["output"]
    atomic_write(output, result, replace=overwrite)
    atomic_write(output.with_suffix(".mp3.json"),
                 json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8"), replace=overwrite)
    return record


def run_compression(options):
    job = make_compression_job(options.input, options.output, options.compression)
    if is_completed(job, options.overwrite):
        emit({**public_record(job), "status": "skipped"})
        return 0
    if options.dry_run:
        emit({**public_record(job), "status": "planned"})
        return 0
    executable = require_ffmpeg() if options.compression != "original" else None
    emit(write_compression_job(job, executable, options.overwrite))
    return 0


def run_batch_compression(options):
    source_root = Path(options.input_dir).expanduser().resolve()
    output_root = Path(options.output_dir).expanduser().resolve()
    if not source_root.is_dir():
        raise ValueError("Compression input directory does not exist")
    if output_root.is_relative_to(source_root):
        raise ValueError("Batch compression output must be outside the input directory")
    entries = source_root.rglob("*") if options.recursive else source_root.iterdir()
    sources = sorted((path for path in entries if path.is_file() and path.suffix.lower() == ".mp3"),
                     key=lambda path: str(path.relative_to(source_root)).casefold())
    if not sources:
        raise ValueError("No MP3 files found in the input directory")
    jobs, targets = [], set()
    for source in sources:
        output = (output_root / source.relative_to(source_root)).resolve()
        if not output.is_relative_to(output_root):
            raise ValueError("Compression output path resolves outside its output directory")
        target_key = str(output).casefold()
        if target_key in targets:
            raise ValueError("Batch compression contains duplicate output paths")
        targets.add(target_key)
        job = make_compression_job(source, output, options.compression)
        job["skip"] = is_completed(job, options.overwrite)
        jobs.append(job)
    if options.dry_run:
        for job in jobs:
            emit({**public_record(job), "status": "skipped" if job["skip"] else "planned"})
        emit({"status": "dry_run", "items": len(jobs),
              "pending": sum(not job["skip"] for job in jobs), "requests": 0})
        return 0
    pending = any(not job["skip"] for job in jobs)
    executable = require_ffmpeg() if pending and options.compression != "original" else None
    manifest = output_root / "compression-manifest.jsonl"
    processed = skipped = 0
    for job in jobs:
        record = public_record(job)
        record.pop("skip", None)
        try:
            if job["skip"]:
                record["status"] = "skipped"
                skipped += 1
            else:
                record = write_compression_job(job, executable, options.overwrite)
                processed += 1
        except (ValueError, OSError) as error:
            record.update(status="failed", error=str(error))
            append_manifest(manifest, record)
            emit(record)
            emit({"status": "stopped", "processed": processed, "skipped": skipped,
                  "remaining": len(jobs) - processed - skipped})
            return 1
        append_manifest(manifest, record)
        emit(record)
    emit({"status": "complete", "processed": processed, "skipped": skipped})
    return 0


def read_batch(path):
    suffix = path.suffix.lower()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        if suffix == ".csv":
            rows = list(csv.DictReader(handle))
        elif suffix == ".json":
            rows = json.load(handle)
        elif suffix == ".jsonl":
            rows = [json.loads(line) for line in handle if line.strip()]
        elif suffix == ".txt":
            rows = [{"text": line.strip()} for line in handle if line.strip()]
        else:
            raise ValueError("Batch input must be .txt, .csv, .json or .jsonl")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Batch input must contain a nonempty list of items")
    return rows


def public_record(job):
    return {key: value for key, value in job.items() if key not in ("payload", "profile", "output")} | {
        "output_file": str(job["output"])}


def run_generation(options):
    if not math.isfinite(options.timeout) or options.timeout <= 0:
        raise ValueError("--timeout must be a positive finite number")
    if options.command == "batch":
        if not math.isfinite(options.interval) or options.interval < 0:
            raise ValueError("--interval must be a nonnegative finite number")
        rows = read_batch(Path(options.input))
        jobs = [make_job(row, options) for row in rows]
        manifest = Path(options.output_dir).expanduser().resolve() / "manifest.jsonl"
    else:
        text = options.text if options.text is not None else Path(options.text_file).read_text(encoding="utf-8-sig")
        jobs = [make_job({"text": text}, options, Path(options.output))]
        manifest = None
    paths = set()
    for job in jobs:
        path_key = str(job["output"]).casefold()
        if path_key in paths:
            raise ValueError("Batch has duplicate output paths; assign unique filenames or remove duplicates")
        paths.add(path_key)
        job["skip"] = is_completed(job, options.overwrite)
    if options.dry_run:
        for job in jobs:
            record = public_record(job)
            record["status"] = "skip" if job["skip"] else "planned"
            emit(record)
        emit({"status": "dry_run", "items": len(jobs),
              "requests": sum(not job["skip"] for job in jobs)})
        return 0
    pending = [job for job in jobs if not job["skip"]]
    executable = require_ffmpeg() if any(job["compression"] != "original" for job in pending) else None
    key = load_key()[0] if pending else None
    generated = skipped = 0
    for job in jobs:
        record = public_record(job)
        record.pop("skip", None)
        try:
            if job["skip"]:
                record["status"] = "skipped"
                skipped += 1
            else:
                if generated and options.command == "batch":
                    time.sleep(options.interval)
                content, extra = synthesize(job, key, options.timeout)
                content, processing = postprocess_audio(content, job["compression"], executable)
                extra.update(processing)
                record.update(extra, status="generated", created_at=datetime.now(timezone.utc).isoformat())
                atomic_write(job["output"], content, replace=options.overwrite)
                atomic_write(job["output"].with_suffix(job["output"].suffix + ".json"),
                             json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8"),
                             replace=options.overwrite)
                generated += 1
        except (ValueError, OSError) as error:
            record.update(status="failed", error=str(error))
            if manifest:
                append_manifest(manifest, record)
            emit(record)
            emit({"status": "stopped", "generated": generated, "skipped": skipped,
                  "remaining": len(jobs) - generated - skipped})
            return 1
        if manifest:
            append_manifest(manifest, record)
        emit(record)
    emit({"status": "complete", "generated": generated, "skipped": skipped})
    return 0


def append_manifest(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="command", required=True)
    config = actions.add_parser("config", help="Manage the local API Key")
    config_actions = config.add_subparsers(dest="config_action", required=True)
    set_key = config_actions.add_parser("set-key", help="Save a key without echoing it")
    set_key.add_argument("--stdin", action="store_true", help="Read the key from standard input")
    config_actions.add_parser("status", help="Show configured state without revealing the key")
    set_pace = config_actions.add_parser("set-pace", help="Save the default delivery pace")
    set_pace.add_argument("pace", choices=PACES)
    set_compression = config_actions.add_parser("set-compression", help="Save the default local MP3 compression")
    set_compression.add_argument("compression", choices=COMPRESSIONS)
    compress = actions.add_parser("compress", help="Compress an existing MP3 locally without calling MiMo")
    compress.add_argument("--input", required=True)
    compress.add_argument("--output", required=True)
    compress.add_argument("--compression", choices=COMPRESSIONS, default="32k")
    compress.add_argument("--overwrite", action="store_true")
    compress.add_argument("--dry-run", action="store_true")
    batch_compress = actions.add_parser("batch-compress", help="Compress a directory of existing MP3 files locally")
    batch_compress.add_argument("--input-dir", required=True)
    batch_compress.add_argument("--output-dir", required=True)
    batch_compress.add_argument("--compression", choices=COMPRESSIONS, default="32k")
    batch_compress.add_argument("--recursive", action="store_true", help="Include subdirectories and keep their layout")
    batch_compress.add_argument("--overwrite", action="store_true")
    batch_compress.add_argument("--dry-run", action="store_true")
    voices = actions.add_parser("voices", help="Manage fixed voice options")
    voice_actions = voices.add_subparsers(dest="voice_action", required=True)
    voice_actions.add_parser("list")
    default = voice_actions.add_parser("default")
    default.add_argument("name")
    add = voice_actions.add_parser("add")
    add.add_argument("name")
    add.add_argument("--reference", required=True, help="Selected WAV/MP3 sample to copy locally")
    add.add_argument("--locale", choices=LOCALES, default="en")
    add.add_argument("--description", default="")
    add.add_argument("--style", default="")
    add.add_argument("--replace", action="store_true")
    for command in ("generate", "batch", "design"):
        action = actions.add_parser(command)
        if command == "batch":
            action.add_argument("--input", required=True)
            action.add_argument("--output-dir", required=True)
            action.add_argument("--interval", type=float, default=0.7,
                                help="Seconds between sequential requests (default: 0.7)")
        else:
            source = action.add_mutually_exclusive_group(required=True)
            source.add_argument("--text")
            source.add_argument("--text-file", help="UTF-8 target text")
            action.add_argument("--output", required=True)
        if command == "design":
            action.add_argument("--description", required=True, help="Natural-language voice design")
        else:
            action.add_argument("--voice", help="Registered voice option; defaults to local selection")
        action.add_argument("--kind", choices=KINDS, default="text")
        action.add_argument("--locale", choices=LOCALES)
        action.add_argument("--pace", choices=PACES, help="Delivery pace; defaults to local settings")
        action.add_argument("--compression", choices=COMPRESSIONS,
                            help="Local MP3 compression; defaults to local settings (initially original)")
        action.add_argument("--style", default="", help="Natural-language pace, tone and emphasis")
        action.add_argument("--instruction-mode", choices=INSTRUCTION_MODES, default="faithful",
                            help="faithful uses kind-specific read-once context (default); "
                                 "educational and neutral preserve earlier requests")
        action.add_argument("--timeout", type=float, default=120)
        action.add_argument("--overwrite", action="store_true")
        action.add_argument("--dry-run", action="store_true", help="Plan only; no API calls or files")
    return parser


def main(argv=None):
    options = build_parser().parse_args(argv)
    try:
        if options.command == "config":
            if options.config_action == "set-key":
                value = sys.stdin.read() if options.stdin else getpass.getpass("MiMo API Key: ")
                save_key(value)
                emit({"configured": True, "path": str(key_path()), "storage": "local plaintext"})
            elif options.config_action == "set-pace":
                set_default_pace(options.pace)
                emit({"default_pace": options.pace, "path": str(data_dir() / "settings.json")})
            elif options.config_action == "set-compression":
                set_default_compression(options.compression)
                emit({"default_compression": options.compression, "path": str(data_dir() / "settings.json")})
            else:
                try:
                    key, source = load_key()
                except ValueError:
                    source = "none"
                emit({"configured": source != "none", "source": source, "path": str(key_path()),
                      "default_voice": registry()[0],
                      "default_pace": generation_settings()["pace"],
                      "default_compression": generation_settings()["compression"],
                      "api_endpoint": api_endpoint(key) if source != "none" else None})
            return 0
        if options.command == "compress":
            return run_compression(options)
        if options.command == "batch-compress":
            return run_batch_compression(options)
        if options.command == "voices":
            default, voices = registry()
            if options.voice_action == "list":
                emit({"default": default, "voices": voices})
            elif options.voice_action == "default":
                if options.name not in voices:
                    raise ValueError("Unknown voice; run: voices list")
                write_registry(options.name, voices)
                emit({"default": options.name, "path": str(data_dir() / "voices.json")})
            else:
                profile = add_voice(options.name, options.reference, options.locale,
                                    options.description, options.style, options.replace)
                emit({"name": options.name, "profile": profile, "default": default})
            return 0
        return run_generation(options)
    except (ValueError, OSError, KeyError, TypeError) as error:
        emit({"status": "error", "error": str(error)})
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
