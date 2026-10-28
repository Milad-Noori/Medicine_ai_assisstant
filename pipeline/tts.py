import asyncio
import re
import tempfile
from pathlib import Path

import edge_tts

VOICE = "fa-IR-DilaraNeural"
RATE = "-10%"


class TTSError(Exception):
    """خطای مربوط به تبدیل متن به گفتار."""


def _clean_for_speech(text: str) -> str:
    text = re.sub(r"[«»\"*#_]", "", text)
    text = re.sub(r"\s*\n\s*", ". ", text)
    text = re.sub(r"\.\s*\.", ".", text)
    return text.strip()


async def _synthesize(text: str, path: str) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(path)


def text_to_speech(text: str, output_path: str = "") -> str:
    cleaned = _clean_for_speech(text)
    if not cleaned:
        raise TTSError("متنی برای تبدیل به گفتار وجود ندارد.")

    if not output_path:
        handle = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        handle.close()
        output_path = handle.name

    try:
        asyncio.run(_synthesize(cleaned, output_path))
    except Exception as exc:
        raise TTSError(f"تبدیل به گفتار ناموفق بود (اینترنت را بررسی کنید): {exc}") from exc

    if not Path(output_path).is_file() or Path(output_path).stat().st_size == 0:
        raise TTSError("فایل صوتی ساخته نشد.")
    return output_path