import base64
import json
import requests
import sys

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def send_image_to_ollama(image_path, prompt="What's in this image?", model="llava"):
    url = "http://localhost:11434/api/generate"
    image_b64 = encode_image_to_base64(image_path)

    payload = {
        "model": model,
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        print("Response:\n", data.get("response", "[No response found]"))
    else:
        print(f"Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} path/to/image.jpg [prompt]")
        sys.exit(1)

    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "What is in this image?"

    send_image_to_ollama(image_path, prompt)

