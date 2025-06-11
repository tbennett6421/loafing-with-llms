__code_desc__ = ""
__code_version__ = 'v0.0.1'
__code_debug__ = False
MODEL = "llava"

## Standard Libraries
import io, os, sys

## 3P Libraries
# pip install requests, pillow, ollama
import requests
from PIL import Image
from ollama import generate

def fetch_url_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content, response.headers.get('Content-Type')

def display_image(image_content):
    image = Image.open(io.BytesIO(image_content))
    image.show()

def explain_image(image_content):
    print("Generating explanation for the image...")
    for response in generate(MODEL, 'describe this image:', images=[image_content], stream=True):
        print(response['response'], end='', flush=True)

def main(url):
    try:
        content, content_type = fetch_url_content(url)
        if 'image' in content_type:
            print("Image content detected.")
            display_image(content)
            explain_image(content)
        else:
            print("The provided URL does not point to an image.")
    except requests.HTTPError as e:
        print(f'Error fetching URL: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {os.path.basename(__file__)} <IMAGE_URL>")
    else:
        url = sys.argv[1]
        main(url)
