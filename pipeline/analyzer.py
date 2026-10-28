import re
from dataclasses import dataclass, field
from difflib import get_close_matches

from pipeline.ocr import OCRResult

DRUG_DB = {
    "paracetamol": ("استامینوفن (پاراستامول)", "برای کاهش تب و درد استفاده می‌شود"),
    "acetaminophen": ("استامینوفن", "برای کاهش تب و درد استفاده می‌شود"),
    "ibuprofen": ("ایبوپروفن", "برای کاهش درد، التهاب و تب استفاده می‌شود"),
    "aspirin": ("آسپرین", "برای کاهش درد و تب استفاده می‌شود"),
    "diclofenac": ("دیکلوفناک", "برای کاهش درد و التهاب استفاده می‌شود"),
    "naproxen": ("ناپروکسن", "برای کاهش درد و التهاب استفاده می‌شود"),
    "amoxicillin": ("آموکسی‌سیلین", "آنتی‌بیوتیک است و فقط با تجویز پزشک مصرف شود"),
    "metformin": ("متفورمین", "برای کنترل قند خون استفاده می‌شود"),
    "omeprazole": ("امپرازول", "برای کاهش اسید معده استفاده می‌شود"),
    "cetirizine": ("ستیریزین", "برای کاهش علائم آلرژی استفاده می‌شود"),
    "loratadine": ("لوراتادین", "برای کاهش علائم آلرژی استفاده می‌شود"),
    "atorvastatin": ("آتورواستاتین", "برای کاهش کلسترول استفاده می‌شود"),
}

DOSE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(mg|mcg|g|ml|iu)\b", re.IGNORECASE)
COUNT_RE = re.compile(
    r"(\d+)\s*(tablets?|tabs?|capsules?|caps?|pills?)\b", re.IGNORECASE
)
FORM_FA = {"tab": "قرص", "cap": "کپسول", "pil": "قرص"}
FUZZY_CUTOFF = 0.8
LOW_AVERAGE_LIMIT = 60


@dataclass
class MedicineInfo:
    raw_text: str = ""
    name_en: str = ""
    name_fa: str = ""
    usage_fa: str = ""
    dose: str = ""
    unit: str = ""
    count: str = ""
    form_fa: str = ""
    warnings: list = field(default_factory=list)


def analyze(ocr: OCRResult) -> MedicineInfo:
    info = MedicineInfo(raw_text=ocr.text)
    if not ocr.text:
        info.warnings.append("متنی از تصویر خوانده نشد.")
        return info
    _find_drug(ocr.text, info)
    _find_dose(ocr.text, info)
    _find_count(ocr.text, info)
    _check_confidence(ocr, info)
    return info


def _find_drug(text: str, info: MedicineInfo) -> None:
    words = re.findall(r"[a-zA-Z]{5,}", text.lower())
    for word in words:
        if word in DRUG_DB:
            _set_drug(word, info)
            return
    for word in words:
        match = get_close_matches(word, DRUG_DB.keys(), n=1, cutoff=FUZZY_CUTOFF)
        if match:
            _set_drug(match[0], info)
            info.warnings.append(
                "نام دارو با تردید تشخیص داده شد؛ حتماً نام روی جعبه را بررسی کنید."
            )
            return
    info.warnings.append("نام دارو در پایگاه داده‌ی برنامه پیدا نشد.")


def _set_drug(key: str, info: MedicineInfo) -> None:
    info.name_en = key
    info.name_fa, info.usage_fa = DRUG_DB[key]


def _find_dose(text: str, info: MedicineInfo) -> None:
    matches = DOSE_RE.findall(text)
    if not matches:
        info.warnings.append("دوز دارو روی برچسب پیدا نشد.")
        return
    cleaned = [(n.replace(",", "."), u.lower()) for n, u in matches]
    info.dose, info.unit = cleaned[0]
    if len(set(cleaned)) > 1:
        info.warnings.append(
            "چند مقدار دوز مختلف دیده شد؛ مقدار درست را از روی جعبه بخوانید."
        )


def _find_count(text: str, info: MedicineInfo) -> None:
    matches = COUNT_RE.findall(text)
    if not matches:
        return
    info.count, form = matches[0]
    info.form_fa = FORM_FA.get(form.lower()[:3], "")


def _check_confidence(ocr: OCRResult, info: MedicineInfo) -> None:
    shaky_numbers = [
        w for w in ocr.low_confidence_words if any(c.isdigit() for c in w.text)
    ]
    if shaky_numbers:
        info.warnings.append(
            "اطمینان خواندن بعضی اعداد کم است؛ حتماً با جعبه تطبیق دهید."
        )
    if ocr.average_confidence < LOW_AVERAGE_LIMIT:
        info.warnings.append("کیفیت خواندن متن پایین است؛ عکس واضح‌تری بگیرید.")