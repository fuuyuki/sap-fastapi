"""Store small mouth-open snapshots attached to medlogs.

Uploaded images are always decoded and re-encoded server-side. That strips
EXIF (including GPS), prevents storing arbitrary payloads, and keeps each
snapshot tiny (max 480px, JPEG) since it is only supporting evidence.
"""

import io
import os
from pathlib import Path

from PIL import Image, ImageOps

MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "media"))

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # reject huge uploads before decoding
MAX_PIXELS = 25_000_000
MAX_DIMENSION = 480
JPEG_QUALITY = 70
MIN_JPEG_QUALITY = 45
MAX_STORED_BYTES = 64 * 1024

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}

Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class EvidenceError(ValueError):
    """Raised when an uploaded snapshot cannot be accepted."""


def _normalize(raw: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(raw)) as source:
            if source.width * source.height > MAX_PIXELS:
                raise EvidenceError("Image resolution is too large")
            image = ImageOps.exif_transpose(source)
            image = image.convert("RGB")
            image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
    except EvidenceError:
        raise
    except Exception as exc:  # Pillow raises several unrelated exception types
        raise EvidenceError("Unsupported or corrupt image") from exc

    quality = JPEG_QUALITY
    while True:
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=quality, optimize=True)
        if buffer.tell() <= MAX_STORED_BYTES or quality <= MIN_JPEG_QUALITY:
            return buffer.getvalue()
        quality -= 10


def save_evidence(medlog_id, raw: bytes) -> str:
    """Normalize ``raw`` and write it as ``<medlog_id>.jpg``. Returns the key."""
    data = _normalize(raw)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    key = f"{medlog_id}.jpg"
    destination = MEDIA_DIR / key
    temporary = destination.with_name(f".{key}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, destination)
    return key


def resolve_evidence(key: str) -> Path:
    """Resolve a stored key to a path inside MEDIA_DIR (never trust the key)."""
    path = (MEDIA_DIR / Path(key).name).resolve()
    if path.parent != MEDIA_DIR.resolve():
        raise EvidenceError("Invalid evidence path")
    return path


def delete_evidence(key: str) -> None:
    try:
        resolve_evidence(key).unlink(missing_ok=True)
    except (EvidenceError, OSError):
        pass
