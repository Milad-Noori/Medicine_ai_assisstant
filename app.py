import streamlit as st

from pipeline.analyzer import analyze
from pipeline.input_handler import ImageInputError, load_image_from_bytes
from pipeline.ocr import OCRError, extract_text
from pipeline.persian_answer import generate_answer
from pipeline.preprocess import preprocess_for_ocr
from pipeline.tts import TTSError, text_to_speech

st.set_page_config(page_title="Medicine Label Reader", page_icon="💊")

st.markdown(
    "<style>.block-container{direction:rtl;text-align:right;}</style>",
    unsafe_allow_html=True,
)
st.title("💊 دارو‌خوان")
st.caption("عکس برچسب دارو را بگیرید یا آپلود کنید تا توضیحش را فارسی بشنوید.")
st.warning("این برنامه جایگزین پزشک یا داروساز نیست. نام و دوز را حتماً روی جعبه بررسی کنید.")

source = st.radio("روش ورودی", ["دوربین", "آپلود فایل"], horizontal=True)
use_llm = st.checkbox("بازنویسی روان با مدل زبانی", value=True)

if source == "دوربین":
    picture = st.camera_input("از جعبه‌ی دارو عکس بگیرید")
else:
    picture = st.file_uploader("تصویر دارو", type=["jpg", "jpeg", "png", "webp"])

if picture is not None:
    try:
        image = load_image_from_bytes(picture.getvalue())
        st.image(image, channels="BGR", caption="تصویر ورودی", use_container_width=True)

        with st.spinner("در حال خواندن متن..."):
            ocr = extract_text(preprocess_for_ocr(image))
        info = analyze(ocr)

        with st.spinner("در حال ساخت پاسخ..."):
            answer = generate_answer(info, use_llm=use_llm)

        st.subheader("نتیجه")
        st.text_area("متن پاسخ", answer, height=220)

        with st.expander("متن خام OCR و اطلاعات استخراج‌شده"):
            st.write(f"میانگین اطمینان OCR: {ocr.average_confidence}")
            st.code(ocr.text or "(خالی)")
            st.json(info.__dict__)

        with st.spinner("در حال تبدیل به صدا..."):
            audio_path = text_to_speech(answer)
        with open(audio_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/mp3")

    except (ImageInputError, OCRError) as exc:
        st.error(str(exc))
    except TTSError as exc:
        st.warning(f"متن آماده است ولی صدا ساخته نشد: {exc}")