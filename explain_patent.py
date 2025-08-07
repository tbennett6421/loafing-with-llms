__code_desc__ = "Explain EULA's in plain English"
__code_version__ = 'v0.0.1'
__code_debug__ = False

import argparse
import ollama

import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract

MODEL = "llama3.1"
SPINNER_STOP = False

def ocr_pdf(filename):
    print("🔍 Running OCR on scanned or encoded PDF...")
    images = convert_from_path(filename)
    text = ""
    for i, img in enumerate(images):
        print(f"OCR page {i+1}/{len(images)}...")
        text += pytesseract.image_to_string(img)
    return text

def extract_text_from_pdf(filename):
    try:
        doc = fitz.open(filename)
        text = "\n".join(page.get_text() for page in doc)
        if text.strip():
            print("📄 Extracted text with PyMuPDF.")
            return text
    except Exception:
        pass
    # If no text, fall back to OCR
    return ocr_pdf(filename)

def simplify_patent_text(text, model):
    prompt = f"""Explain the following patent in plain English.

Patent:
{text[:8000]}"""  # Truncate for prompt length safety

    try:
        stream = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        print("\n📜 Plain English Summary:\n")
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)

    except Exception as e:
        print(f"\n❌ Error while simplifying: {e}")

def main():
    parser = argparse.ArgumentParser(description="Summarize patent PDF text using Ollama.")
    parser.add_argument("filename", help="Path to the patent PDF file")
    parser.add_argument("-m", "--model", default=MODEL, help=f"Ollama model to use (default: {MODEL})")
    args = parser.parse_args()

    print(f"📄 Reading patent from {args.filename}...")
    text = extract_text_from_pdf(args.filename)
    if not text.strip():
        print("❗ No readable text found in PDF.")
        return

    simplify_patent_text(text, args.model)

if __name__ == "__main__":
    main()

