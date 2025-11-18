from mcp.server.fastmcp import FastMCP
import signal
import sys
import requests
import hashlib
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Initialize MCP
HOST = "127.0.0.1"
PORT = 8080
mcp = FastMCP(name="favicon-hasher", host=HOST, port=PORT)

# Graceful shutdown
def signal_handler(sig, frame):
    print("Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; favicon-hasher/1.0; +https://example.local)",
    "Accept": "text/html,application/xhtml+xml,application/xml,image/*;q=0.9,*/*;q=0.8",
}

MAX_FAVICON_BYTES = 2 * 1024 * 1024  # 2MB safety cap


def sanitize_url(raw_url: str) -> str:
    """
    Extract a clean scheme+netloc from a possibly messy input string.
    Returns normalized base URL with trailing slash.
    """
    # Prefer first HTTP/HTTPS token
    for token in raw_url.split():
        if token.startswith(("http://", "https://")):
            p = urlparse(token)
            if p.scheme and p.netloc:
                return f"{p.scheme}://{p.netloc}/"

    # Fallback: try to parse whole string
    p = urlparse(raw_url.strip())
    if p.scheme and p.netloc:
        return f"{p.scheme}://{p.netloc}/"

    # Last resort: assume https and treat first segment as host
    host = raw_url.strip().split()[0].split("/")[0]
    return f"https://{host}/"


def discover_favicon_links(html: str, base_url: str) -> list[str]:
    """
    Parse HTML to find favicon-related <link> tags and return absolute URLs,
    ordered by typical preference.
    """
    soup = BeautifulSoup(html or "", "html.parser")
    icon_candidates = []

    # Collect all link tags with rel containing 'icon' variants
    for link in soup.find_all("link"):
        rel = link.get("rel")
        if not rel:
            continue
        rel_lower = [r.lower() for r in rel] if isinstance(rel, list) else [str(rel).lower()]
        if any("icon" in r for r in rel_lower) or any(r in ("shortcut icon", "apple-touch-icon") for r in rel_lower):
            href = link.get("href")
            if not href:
                continue
            abs_url = urljoin(base_url, href)
            typ = (link.get("type") or "").lower()
            sizes = (link.get("sizes") or "").lower()

            # Score preference: ICO > PNG > SVG > others; larger sizes often preferred
            score = 0
            if typ.endswith("x-icon") or typ.endswith("ico"):
                score += 30
            elif typ.endswith("png"):
                score += 20
            elif typ.endswith("svg+xml") or abs_url.endswith(".svg"):
                score += 10
            elif abs_url.endswith(".ico"):
                score += 25
            elif abs_url.endswith(".png"):
                score += 18

            if "any" in sizes:
                score += 3
            elif sizes:
                # rough size preference boost (e.g., 180x180, 32x32)
                score += 2

            icon_candidates.append((score, abs_url))

    # Sort by score descending, unique while preserving order
    seen = set()
    ordered = []
    for score, u in sorted(icon_candidates, key=lambda x: x[0], reverse=True):
        if u not in seen:
            seen.add(u)
            ordered.append(u)

    return ordered


def try_fetch_binary(url: str, timeout: float = 8.0) -> bytes | None:
    """
    Fetch binary content with headers, redirects, content-length guarding,
    and reasonable timeouts.
    """
    try:
        # HEAD first to check existence and size
        head = requests.head(url, headers=DEFAULT_HEADERS, allow_redirects=True, timeout=timeout)
        if head.status_code >= 400:
            return None

        content_length = head.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > MAX_FAVICON_BYTES:
                    return None
            except ValueError:
                pass

        # GET the content
        resp = requests.get(url, headers=DEFAULT_HEADERS, allow_redirects=True, timeout=timeout)
        if resp.status_code >= 400 or not resp.content:
            return None

        # Additional guard on actual bytes
        if len(resp.content) > MAX_FAVICON_BYTES:
            return None

        return resp.content
    except Exception:
        return None


def fetch_favicon_url_and_bytes(base_url: str) -> tuple[str | None, bytes | None]:
    """
    Discover favicon URL via HTML and fallbacks, then fetch bytes.
    Returns (favicon_url, content) or (None, None).
    """
    # 1) Fetch homepage HTML (follows 301 redirects)
    try:
        html_resp = requests.get(base_url, headers=DEFAULT_HEADERS, allow_redirects=True, timeout=8.0)
        html_text = html_resp.text if html_resp.status_code == 200 else ""
        # Use final URL after redirects for relative link resolution
        final_base_url = html_resp.url
    except Exception:
        html_text = ""
        final_base_url = base_url

    # 2) Parse <link> icons
    for icon_url in discover_favicon_links(html_text, final_base_url):
        content = try_fetch_binary(icon_url)
        if content:
            return icon_url, content

    # 3) Common fallbacks
    fallbacks = [
        urljoin(base_url, "/favicon.ico"),
        urljoin(base_url, "/favicon.png"),
        urljoin(base_url, "/apple-touch-icon.png"),
    ]
    for fb in fallbacks:
        content = try_fetch_binary(fb)
        if content:
            return fb, content

    return None, None


def compute_hashes(content: bytes) -> dict:
    """
    Compute MD5 and SHA1 hashes of binary content.
    """
    return {
        "md5": hashlib.md5(content).hexdigest(),
        "sha1": hashlib.sha1(content).hexdigest(),
    }


@mcp.tool()
def get_favicon_hash(url: str) -> dict:
    """
    Fetches a website's favicon (from HTML or fallbacks) and returns MD5 and SHA1 hashes.
    Returns {'md5': None, 'sha1': None} if it cannot be discovered or fetched.
    """
    try:
        clean_url = sanitize_url(url)
        favicon_url, content = fetch_favicon_url_and_bytes(clean_url)
        if not content:
            return {"md5": None, "sha1": None}

        hashes = compute_hashes(content)
        # If you want to also report which URL was used, you can add it here
        # return {"md5": hashes["md5"], "sha1": hashes["sha1"], "source": favicon_url}
        return hashes
    except Exception:
        return {"md5": None, "sha1": None}


if __name__ == "__main__":
    print(f"Starting favicon-hasher MCP server at PORT {PORT}...")
    mcp.run()
