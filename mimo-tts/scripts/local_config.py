"""Local credentials and reusable voice profiles; Python standard library only."""

import hashlib
import io
import json
import logging
import os
import re
import tempfile
import time
import wave
from pathlib import Path


PACES = ("slow", "normal", "brisk", "fast")
COMPRESSIONS = ("original", "32k", "24k")


PRESET_VOICES = {
    name: {"type": "preset", "voice": name, "locale": locale}
    for name, locale in (
        ("Mia", "en"), ("Chloe", "en"), ("Milo", "en"), ("Dean", "en"),
        ("冰糖", "zh-CN"), ("茉莉", "zh-CN"), ("苏打", "zh-CN"),
        ("白桦", "zh-CN"), ("mimo_default", "auto"),
    )
}


def data_dir():
    override = os.environ.get("MIMO_TTS_HOME")
    if override:
        return Path(override).expanduser().resolve()
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".config"))
    return base / "mimo-tts"


def key_path():
    return data_dir() / "api-key"


def generation_settings():
    path = data_dir() / "settings.json"
    settings = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    if not isinstance(settings, dict) or settings.get("pace", "normal") not in PACES:
        raise ValueError("Invalid default pace in local settings")
    if settings.get("compression", "original") not in COMPRESSIONS:
        raise ValueError("Invalid default compression in local settings")
    return {"pace": "normal", "compression": "original", **settings}


def set_default_pace(pace):
    if pace not in PACES:
        raise ValueError("pace must be slow, normal, brisk or fast")
    settings = generation_settings()
    settings["pace"] = pace
    atomic_write(data_dir() / "settings.json",
                 json.dumps(settings, ensure_ascii=False, indent=2).encode("utf-8"), replace=True)


def set_default_compression(compression):
    if compression not in COMPRESSIONS:
        raise ValueError("compression must be original, 32k or 24k")
    settings = generation_settings()
    settings["compression"] = compression
    atomic_write(data_dir() / "settings.json",
                 json.dumps(settings, ensure_ascii=False, indent=2).encode("utf-8"), replace=True)


def _retry_windows_file_operation(operation):
    for attempt in range(101):
        try:
            return operation()
        except OSError as error:
            # Antivirus and readers may briefly omit FILE_SHARE_DELETE.
            if os.name != "nt" or error.winerror not in (5, 32, 33) or attempt == 100:
                raise
            time.sleep(0.05)


def atomic_write(path, content, replace=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".mimo-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            _retry_windows_file_operation(lambda: os.replace(temporary, path))
        else:
            # Publishing a completed file must not overwrite an existing file.
            _retry_windows_file_operation(lambda: os.link(temporary, path))
    finally:
        try:
            _retry_windows_file_operation(lambda: Path(temporary).unlink(missing_ok=True))
        except OSError as error:
            # Cleanup must not undo successful publication or mask its failure.
            logging.getLogger(__name__).warning("Temporary file cleanup deferred: %s (%s)", temporary, error)


def validate_key(value):
    value = value.strip()
    if not value or any(ord(char) < 33 or ord(char) > 126 for char in value):
        raise ValueError("API Key must be nonempty ASCII without whitespace")
    return value


def save_key(value):
    content = validate_key(value).encode("ascii")
    atomic_write(key_path(), content, replace=True)
    if os.name != "nt":
        key_path().chmod(0o600)


def load_key():
    value = os.environ.get("MIMO_API_KEY", "").strip()
    if value:
        return validate_key(value), "environment"
    if not key_path().is_file():
        raise ValueError("No API Key configured. Run: config set-key")
    return validate_key(key_path().read_text(encoding="ascii")), "local"


def audio_info(content, audio_format):
    info = {"bytes": len(content), "audio_sha256": hashlib.sha256(content).hexdigest()}
    if audio_format == "wav":
        try:
            with wave.open(io.BytesIO(content), "rb") as audio:
                frames, rate = audio.getnframes(), audio.getframerate()
                samples = audio.readframes(frames)
                expected = frames * audio.getnchannels() * audio.getsampwidth()
                if frames <= 0 or rate <= 0 or len(samples) != expected:
                    raise ValueError("WAV audio is empty or truncated")
                info.update(duration_seconds=round(frames / rate, 4),
                            sample_rate=rate, channels=audio.getnchannels())
        except (wave.Error, EOFError) as error:
            raise ValueError("Response is not a readable WAV file") from error
    elif audio_format == "mp3":
        frame_header = len(content) > 2 and content[0] == 255 and content[1] & 224 == 224
        if len(content) < 16 or not (content.startswith(b"ID3") or frame_header):
            raise ValueError("Response does not have an MP3 header")
    else:
        raise ValueError("Only WAV and MP3 files are supported")
    return info


def registry():
    path = data_dir() / "voices.json"
    saved = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    custom = saved.get("voices", {})
    if not isinstance(custom, dict) or set(custom) & set(PRESET_VOICES):
        raise ValueError("Invalid local voice registry")
    voices = {**PRESET_VOICES, **custom}
    default = saved.get("default", "Mia")
    if default not in voices:
        raise ValueError("Default voice is missing from local registry")
    return default, voices


def write_registry(default, voices):
    custom = {name: value for name, value in voices.items() if name not in PRESET_VOICES}
    content = json.dumps({"version": 1, "default": default, "voices": custom},
                         ensure_ascii=False, indent=2).encode("utf-8")
    atomic_write(data_dir() / "voices.json", content, replace=True)


def reference_bytes(profile):
    root = data_dir().resolve()
    path = (root / profile["reference_audio"]).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Voice reference must be inside the local MiMo TTS directory")
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != profile["reference_sha256"]:
        raise ValueError("Voice reference has changed; register the intended sample again")
    if ((len(content) + 2) // 3) * 4 > 10_000_000:
        raise ValueError("Base64 voice reference exceeds the documented 10 MB limit")
    return content


def add_voice(name, reference, locale, description="", style="", replace=False):
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", name):
        raise ValueError("Custom voice names must use 1-48 lowercase letters, digits or hyphens")
    default, voices = registry()
    if name in voices and (not replace or name in PRESET_VOICES):
        raise ValueError("Voice name already exists; choose another name or use --replace")
    reference = Path(reference)
    audio_format = reference.suffix.lower().lstrip(".")
    content = reference.read_bytes()
    info = audio_info(content, audio_format)
    if ((len(content) + 2) // 3) * 4 > 10_000_000:
        raise ValueError("Base64 voice reference exceeds the documented 10 MB limit")
    relative = f"voices/{name}-{info['audio_sha256'][:12]}.{audio_format}"
    target = data_dir() / relative
    if not target.exists():
        atomic_write(target, content)
    voices[name] = {"type": "clone", "locale": locale, "description": description,
                    "style": style, "reference_audio": relative,
                    "reference_sha256": info["audio_sha256"]}
    write_registry(default, voices)
    return voices[name]
