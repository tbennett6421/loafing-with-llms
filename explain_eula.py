__code_desc__ = "Explain EULA's in plain English"
__code_version__ = 'v0.0.1'
__code_debug__ = False

import argparse
import ollama

MODEL = "llama3.1"
SPINNER_STOP = False

def read_eula(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def explain_eula_stream(text, model=MODEL):
    prompt = f"""Explain the following End User License Agreement in plain English.
List the important rights, restrictions, and obligations in bullet points. Be concise and clear.

EULA:
{text[:8000]}"""

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
        print(f"\n❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description=__code_desc__)
    parser.add_argument("eula_file", help="Path to the EULA text file")
    parser.add_argument("-m", "--model", default=MODEL, help=f"Ollama model to use (default: {MODEL})")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__code_version__}")
    args = parser.parse_args()

    try:
        eula_text = read_eula(args.eula_file)
        explain_eula_stream(eula_text, model=args.model)
    except FileNotFoundError:
        print(f"❌ File not found: {args.eula_file}")
    except Exception as e:
        print(f"❌ Failed to process EULA: {e}")

if __name__ == "__main__":
    main()
