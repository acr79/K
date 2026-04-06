"""Web page reader — fetches URL content and extracts readable text."""

import re
import urllib.request
from dataclasses import dataclass


@dataclass
class PageContent:
    url: str
    title: str
    text: str
    word_count: int


# Sites that block scraping — skip them
SKIP_DOMAINS = {
    "reddit.com", "twitter.com", "x.com",
    "instagram.com", "facebook.com", "tiktok.com",
    "wsj.com", "nytimes.com",  # paywalls
}

MAX_CHARS = 8000   # max chars to extract per page (~2k tokens)


def read_url(url: str) -> PageContent | None:
    """Fetch a URL and extract clean readable text."""
    domain = _get_domain(url)
    if any(skip in domain for skip in SKIP_DOMAINS):
        return None

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception:
        return None

    title, text = _extract_text(html)
    text = text[:MAX_CHARS]

    if len(text) < 100:
        return None

    return PageContent(
        url=url,
        title=title,
        text=text,
        word_count=len(text.split())
    )


def _extract_text(html: str) -> tuple[str, str]:
    """Extract title and body text from HTML without BeautifulSoup dependency."""
    # Title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = _clean(title_match.group(1)) if title_match else ""

    # Remove scripts, styles, nav, footer, ads
    html = re.sub(r"<(script|style|nav|footer|header|aside|iframe)[^>]*>.*?</\1>",
                  " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)

    # Extract text from remaining tags
    text = re.sub(r"<[^>]+>", " ", html)
    text = _clean(text)

    # Collapse whitespace and short lines (navigation remnants)
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 40]
    text = "\n".join(lines)

    return title, text


def _clean(text: str) -> str:
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&#\d+;", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _get_domain(url: str) -> str:
    match = re.search(r"https?://([^/]+)", url)
    return match.group(1).lower() if match else ""
