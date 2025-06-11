__code_desc__ = "Fetch and display an XKCD comic by number. If no number is provided, a random one will be chosen."
__code_version__ = 'v0.0.1'
__code_debug__ = False
MODEL = "llava"

## Standard Libraries
import io, sys
import argparse
import random

## 3P Libraries
# pip install requests, pillow, ollama
import requests
from PIL import Image
from ollama import generate

def get_latest_comic_number():
    response = requests.get('https://xkcd.com/info.0.json')
    response.raise_for_status()
    return response.json().get('num')

def get_comic_info(num):
    response = requests.get(f'https://xkcd.com/{num}/info.0.json')
    response.raise_for_status()
    return response.json()

def fetch_image_content(image_url):
    response = requests.get(image_url)
    response.raise_for_status()
    return response.content

def display_image(image_content):
    image = Image.open(io.BytesIO(image_content))
    image.show()

def get_args():
    parser = argparse.ArgumentParser(description=__code_desc__)
    parser.add_argument("comic_number", nargs="?", type=int,
        help="The comic number to fetch (default: random)"
    )
    return parser.parse_args()

def main():
    args = get_args()
    if args.comic_number is not None:
        num = args.comic_number
    else:
        num = random.randint(1, get_latest_comic_number())

    try:
        comic = get_comic_info(num)

        print(f'xkcd #{comic["num"]}: {comic["alt"]}')
        print(f'link: https://xkcd.com/{num}')
        print('---')

        raw_image_content = fetch_image_content(comic['img'])
        display_image(raw_image_content)

        # Generate explanation
        for response in generate(MODEL, 'explain this comic:', images=[raw_image_content], stream=True):
            print(response['response'], end='', flush=True)

    except requests.exceptions.HTTPError as e:
        print(f'Error fetching comic: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

if __name__ == "__main__":
    main()
