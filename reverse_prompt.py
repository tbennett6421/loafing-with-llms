__code_desc__ = "Attempt to infer the prompt from the contents of a target file"
__code_version__ = 'v0.0.1'
__code_debug__ = False

import argparse
import ollama

MODEL = "llama3.1"
SPINNER_STOP = False

def read_target(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def infer(text, model=MODEL):
    prompt = f"""You are a reverse prompt engineer. Given an output from a language model, your job is to infer the original prompt or describe the intent, structure, and content that might have led to this output. Be precise and technical."

TEXT:
{text[:8000]}"""

    try:
        stream = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        print("\n📜 Inferrence:\n")
        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)

    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(description=__code_desc__)
    parser.add_argument("target", help="Path to a target text file")
    parser.add_argument("-m", "--model", default=MODEL, help=f"Ollama model to use (default: {MODEL})")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__code_version__}")
    args = parser.parse_args()

    try:
        target_text = read_target(args.target)
        infer(target_text, model=args.model)
    except FileNotFoundError:
        print(f"❌ File not found: {args.target}")
    except Exception as e:
        print(f"❌ Failed to process target: {e}")

if __name__ == "__main__":
    main()
