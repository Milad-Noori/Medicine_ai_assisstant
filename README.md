# 💊 Medicine AI Assistant — داروخوان

A Persian-language medicine-label reader built with **Python** and **Streamlit**. The app lets a user take a picture of a medicine package or upload an image, extracts printed text with OCR, looks for a supported medicine name and dosage details, generates a Persian explanation, and can read the result aloud.

> **Important:** This is an educational prototype, not a medical device. OCR and the built-in medicine list can be incomplete or wrong. Always verify the medicine name and dosage directly on the packaging and ask a pharmacist or clinician when in doubt. Never use this app to decide whether to start, stop, or change a medicine.

## Features

- **Camera or image upload:** Capture a package photo in the browser or upload a JPG, JPEG, PNG, or WEBP image.
- **Image preparation:** Uses OpenCV to improve an image before text recognition, including grayscale conversion, denoising, contrast enhancement, and deskewing.
- **Persian and English OCR:** Uses Tesseract OCR with the `fas` and `eng` language data and reports an average OCR confidence score.
- **Medicine-label parsing:** Looks for a medicine name from a small built-in list, common dosage units (`mg`, `mcg`, `g`, `ml`, `IU`), and tablet/capsule counts when they are present in readable text.
- **Persian explanation:** Produces a template-based Persian explanation and includes warnings when the name, numbers, or OCR confidence are uncertain.
- **Optional local language model:** Can use the local Ollama model `qwen2.5:3b` to make the Persian wording more natural. If Ollama is unavailable, the app falls back to the template response.
- **Text-to-speech:** Reads the result aloud using the Persian `fa-IR-DilaraNeural` voice through `edge-tts`.
- **Right-to-left interface:** The Streamlit interface is styled for Persian text and can show the raw OCR text and extracted fields for review.

## How the processing pipeline works

1. The user takes a photo or uploads an image.
2. The image input handler validates and decodes the image.
3. The preprocessing module prepares the image for OCR.
4. Tesseract extracts Persian and English text and estimates recognition confidence.
5. The analyzer searches the recognized text for supported medicine names, dosage values, and package counts.
6. The answer module creates a Persian explanation, optionally asking a local Ollama model to rephrase it.
7. The text-to-speech module generates audio, which the app plays in the browser.

## Technology stack

- Python
- Streamlit — web interface
- OpenCV and NumPy — image loading and preprocessing
- Tesseract OCR and `pytesseract` — printed-text recognition
- Requests — communication with the local Ollama API
- Ollama with `qwen2.5:3b` — optional local text rephrasing
- `edge-tts` — Persian speech synthesis

## Project structure

```text
Medicine_ai_assisstant/
├── app.py
├── requirements.txt
├── LICENSE
├── README.md
└── pipeline/
    ├── analyzer.py
    ├── input_handler.py
    ├── ocr.py
    ├── persian_answer.py
    ├── preprocess.py
    └── tts.py
```

- `app.py` — Streamlit interface and main application flow.
- `pipeline/input_handler.py` — validates and loads input images.
- `pipeline/preprocess.py` — image enhancement before OCR.
- `pipeline/ocr.py` — Tesseract setup, text extraction, and OCR confidence data.
- `pipeline/analyzer.py` — checks OCR text against the built-in medicine list and extracts selected label details.
- `pipeline/persian_answer.py` — builds the Persian response and optionally calls Ollama.
- `pipeline/tts.py` — converts the response to speech.

## Requirements

- Windows, macOS, or Linux
- Python **3.11 recommended**
- Tesseract OCR installed separately, including both **English (`eng`) and Persian (`fas`) language data**
- Internet access for `edge-tts` speech generation
- Optional: [Ollama](https://ollama.com/) with the `qwen2.5:3b` model for local language-model rephrasing

The Python packages are listed in `requirements.txt`. Tesseract and Ollama are separate system applications and are not installed by `pip`.

## Installation on Windows

### 1. Clone the repository

```powershell
git clone https://github.com/Milad-Noori/Medicine_ai_assisstant.git
cd Medicine_ai_assisstant
```

If the project is already on your computer, open PowerShell in the project folder instead of cloning it again.

### 2. Create and activate a virtual environment

Python 3.11 is recommended as a starting point:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell reports that `py -3.11` is not available, install Python 3.11 first or use the launcher command for a compatible Python version installed on your computer.

### 3. Install Python dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Install and check Tesseract OCR

Install Tesseract OCR and make sure the `eng` and `fas` language data are available. A commonly used Windows installer is published by UB Mannheim: <https://github.com/UB-Mannheim/tesseract/wiki>.

The current code checks this default Windows executable path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

If Tesseract is installed in another location, update `DEFAULT_TESSERACT_PATH` in `pipeline/ocr.py` to point to the correct executable.

### 5. (Optional) Set up Ollama

Install Ollama, then download the model used by this project:

```powershell
ollama pull qwen2.5:3b
```

Make sure the Ollama service is running locally. The application expects its chat API at `http://localhost:11434/api/chat`. Ollama is optional; the app can return its template-based response when model rephrasing is disabled or unavailable.

### 6. Run the application

From the project root, with the virtual environment activated:

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually <http://localhost:8501>.

## Usage

1. Choose **Camera** or **Upload file** in the app.
2. Capture or select a clear picture of the medicine label.
3. Keep the **language-model rephrasing** option enabled only if you want to use the optional local Ollama model.
4. Review the Persian explanation and play the audio if available.
5. Expand **raw OCR and extracted information** to inspect the recognized text, confidence score, and parsed fields.
6. Verify the medicine name and every number against the original packaging before relying on the information.

For the best OCR results, photograph the label straight on, use good lighting, avoid glare and motion blur, and include the full text in the image.

## Troubleshooting

### `No module named streamlit`

Activate the project's virtual environment and install dependencies into that same environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Tesseract cannot be found

Check that Tesseract is installed, that its executable path matches `DEFAULT_TESSERACT_PATH` in `pipeline/ocr.py`, and that the English and Persian language data are installed.

### The medicine name or dosage is not recognized correctly

The app depends on image quality, OCR accuracy, and a limited built-in medicine list. Try a clearer photo and inspect the raw OCR output. Do not guess a medicine name or dosage from a low-confidence result.

### Language-model rephrasing does not work

Check that Ollama is installed and running and that `qwen2.5:3b` has been downloaded. You can turn off the rephrasing option to use the template-based answer instead.

### Audio is not generated

The `edge-tts` speech step needs network access. If speech generation fails, the app may still show the text answer; use that text only after checking it against the medicine package.

## Safety and privacy

- This application provides informational assistance only. It does not diagnose conditions, prescribe medicines, or confirm that a medicine is appropriate for a person.
- The medicine dictionary is limited and must not be treated as a complete drug database.
- OCR errors can change medicine names or numbers. Always verify all details from the physical package or the official leaflet.
- The optional Ollama text model is intended to rephrase the prepared response, not independently validate medical facts.
- Speech generation requires an internet connection. Do not submit sensitive personal or medical information unless you have reviewed the relevant service and privacy terms.

## License

This project is distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

## Author

**Milad Noori** — [GitHub](https://github.com/Milad-Noori)
