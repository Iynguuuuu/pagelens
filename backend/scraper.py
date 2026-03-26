import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def scrape_page(url: str) -> tuple[dict, str]:
    """
    Scrape a single page and return:
    - metrics dict (factual, no AI)
    - page_text for AI context
    """
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc

    # --- Meta ---
    meta_title = ""
    if soup.title:
        meta_title = soup.title.get_text(strip=True)

    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if meta_tag:
        meta_desc = meta_tag.get("content", "").strip()

    # --- Headings ---
    h1_count = len(soup.find_all("h1"))
    h2_count = len(soup.find_all("h2"))
    h3_count = len(soup.find_all("h3"))

    # --- Word count (visible text only) ---
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    visible_text = soup.get_text(separator=" ", strip=True)
    words = [w for w in visible_text.split() if w.strip()]
    word_count = len(words)

    # --- Images ---
    images = soup.find_all("img")
    image_count = len(images)
    missing_alt = sum(
        1 for img in images
        if not img.get("alt") or not img.get("alt", "").strip()
    )
    missing_alt_pct = round((missing_alt / image_count * 100), 1) if image_count > 0 else 0

    # --- Links ---
    all_links = soup.find_all("a", href=True)
    internal_links = []
    external_links = []
    for a in all_links:
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full_url = urljoin(url, href)
        link_domain = urlparse(full_url).netloc
        if link_domain == base_domain or not link_domain:
            internal_links.append(full_url)
        else:
            external_links.append(full_url)

    # --- CTAs ---
    # Buttons + links with CTA-like text
    cta_keywords = re.compile(
        r"\b(get started|sign up|contact|book|demo|free trial|buy|shop|subscribe|"
        r"learn more|download|try|start|join|request|schedule|apply|get a quote|"
        r"talk to us|reach out|see pricing)\b",
        re.IGNORECASE
    )
    buttons = soup.find_all("button")
    cta_links = [a for a in soup.find_all("a") if cta_keywords.search(a.get_text(strip=True))]
    cta_count = len(buttons) + len(cta_links)

    # Fresh visible text for AI (after decompose above soup is already cleaned)
    page_text_for_ai = " ".join(words[:3000])  # cap to ~3k words for token efficiency

    metrics = {
        "meta_title": meta_title,
        "meta_description": meta_desc,
        "word_count": word_count,
        "headings": {
            "h1": h1_count,
            "h2": h2_count,
            "h3": h3_count
        },
        "cta_count": cta_count,
        "links": {
            "internal": len(internal_links),
            "external": len(external_links)
        },
        "images": {
            "total": image_count,
            "missing_alt": missing_alt,
            "missing_alt_pct": missing_alt_pct
        }
    }

    return metrics, page_text_for_ai