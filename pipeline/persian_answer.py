import re

import requests

from pipeline.analyzer import MedicineInfo

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"
TIMEOUT_SECONDS = 90
DISCLAIMER = "قبل از مصرف، بروشور دارو را مطالعه کنید و در صورت تردید از پزشک یا داروساز بپرسید."
UNIT_FA = {
    "mg": "میلی‌گرم",
    "mcg": "میکروگرم",
    "g": "گرم",
    "ml": "میلی‌لیتر",
    "iu": "واحد بین‌المللی",
}
PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")


def build_template_answer(info: MedicineInfo) -> str:
    if not info.name_en:
        return (
            "نام دارو به‌طور قابل اطمینان خوانده نشد. "
            "لطفاً دوباره عکس بگیرید یا برچسب را مستقیم بخوانید."
        )
    sentences = [f"این دارو {info.name_fa} است."]
    unit = UNIT_FA.get(info.unit, info.unit)
    form = info.form_fa or "عدد"
    if info.dose and info.count:
        sentences.append(f"دوز آن {info.dose} {unit} و تعداد آن {info.count} {form} است.")
    elif info.dose:
        sentences.append(f"دوز آن {info.dose} {unit} است.")
    elif info.count:
        sentences.append(f"تعداد آن {info.count} {form} است.")
    if info.usage_fa:
        sentences.append(f"این دارو {info.usage_fa}.")
    sentences.extend(info.warnings)
    sentences.append(DISCLAIMER)
    return "\n".join(sentences)


def generate_answer(info: MedicineInfo, use_llm: bool = True) -> str:
    base = build_template_answer(info)
    if not use_llm or not info.name_en:
        return base
    try:
        polished = _ask_llm(base)
    except (requests.RequestException, KeyError, ValueError):
        return base
    if _is_safe(base, polished, info):
        return polished
    return base


def _ask_llm(text: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "options": {"temperature": 0.2},
        "messages": [
            {
                "role": "system",
                "content": (
                    "تو یک بازنویس متن فارسی هستی. متن کاربر را با فارسی ساده و روان "
                    "بازنویسی کن. هیچ عدد، نام دارو، هشدار یا اطلاعات جدیدی اضافه یا "
                    "حذف نکن. فقط متن بازنویسی‌شده را بنویس."
                ),
            },
            {"role": "user", "content": text},
        ],
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


def _numbers(text: str) -> set:
    return set(re.findall(r"\d+", text.translate(PERSIAN_DIGITS)))


def _is_safe(base: str, polished: str, info: MedicineInfo) -> bool:
    if not polished:
        return False
    if _numbers(base) != _numbers(polished):
        return False
    short_name = info.name_fa.split(" (")[0]
    return short_name in polished