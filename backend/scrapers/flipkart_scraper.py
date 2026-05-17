"""
ReviewIQ — Flipkart Review Scraper
Uses requests + BeautifulSoup with rotating user agents.
Falls back silently to mock data if scraping is blocked.
"""
import logging
import re
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]


def _get_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def _extract_flipkart_pid(url: str) -> Optional[str]:
    """Extract product ID / pid from Flipkart URL."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "pid" in qs:
        return qs["pid"][0]
    # Try to get from path: /product-name/p/ITEMCODE
    m = re.search(r"/p/([A-Z0-9]+)", parsed.path)
    if m:
        return m.group(1)
    return None


def _build_reviews_url(base_url: str, page: int = 1) -> str:
    """Build Flipkart reviews URL from product URL."""
    parsed = urlparse(base_url)
    path_parts = parsed.path.rstrip("/").split("/")

    # Flipkart reviews URL pattern: /product-name/product-reviews/ITEMID
    if "product-reviews" not in parsed.path:
        # Insert product-reviews segment
        if len(path_parts) >= 3:
            path_parts.insert(-1, "product-reviews")
        path = "/".join(path_parts)
    else:
        path = parsed.path

    qs = parse_qs(parsed.query)
    qs["page"] = [str(page)]
    new_query = urlencode({k: v[0] for k, v in qs.items()})
    return urlunparse((parsed.scheme, parsed.netloc, path, "", new_query, ""))


def _parse_flipkart_rating(rating_str: str) -> int:
    try:
        m = re.search(r"(\d+(\.\d+)?)", rating_str)
        if m:
            return round(float(m.group(1)))
    except Exception:
        pass
    return 3


def _scrape_flipkart_live(url: str, max_reviews: int) -> Optional[Dict]:
    """Attempt live scraping of Flipkart reviews. Returns None on failure."""
    try:
        import requests
        from bs4 import BeautifulSoup

        all_reviews: List[Dict] = []
        product_name = "Flipkart Product"

        pages = min((max_reviews // 10) + 1, 5)

        for page in range(1, pages + 1):
            if len(all_reviews) >= max_reviews:
                break

            review_url = _build_reviews_url(url, page)
            time.sleep(random.uniform(1.0, 2.5))

            resp = requests.get(review_url, headers=_get_headers(), timeout=10)

            if resp.status_code != 200:
                logger.info(f"[Flipkart] HTTP {resp.status_code}, using fallback")
                return None

            if "robot" in resp.text.lower() or "captcha" in resp.text.lower():
                logger.info("[Flipkart] Bot detection triggered, using fallback")
                return None

            soup = BeautifulSoup(resp.content, "lxml")

            # Extract product name
            if page == 1:
                name_el = soup.select_one("a.a-link-normal[title]") or soup.select_one("h1._9E25nV")
                if name_el:
                    product_name = name_el.get("title") or name_el.get_text(strip=True)

            # Flipkart review selectors (multiple fallbacks for different layouts)
            review_containers = (
                soup.select("div._1AtVbE div.col.epCmJX") or
                soup.select("div[class*='review'] div[class*='col']") or
                soup.select("div.t-ZTKy") or
                soup.select("div._27M-vq")
            )

            if not review_containers and page == 1:
                # Try alternative selectors
                review_containers = soup.select("div.EKFha-")
                if not review_containers:
                    logger.info("[Flipkart] No review containers found, using fallback")
                    return None

            for container in review_containers:
                if len(all_reviews) >= max_reviews:
                    break
                try:
                    # Text selectors
                    text_el = (
                        container.select_one("div.t-ZTKy div") or
                        container.select_one("p[class*='review']") or
                        container.select_one("div._6K-7Co")
                    )
                    rating_el = (
                        container.select_one("div[class*='star'] span") or
                        container.select_one("span._2_R_DZ")
                    )
                    date_el = container.select_one("p._2sc7ZR span")

                    if not text_el:
                        continue

                    review_text = text_el.get_text(separator=" ", strip=True)
                    if len(review_text) < 10:
                        continue

                    rating_text = rating_el.get_text(strip=True) if rating_el else "3"
                    rating = _parse_flipkart_rating(rating_text)

                    date_str = date_el.get_text(strip=True) if date_el else ""
                    date_match = re.search(r"(\w+\s+\d{4}|\d{1,2}\s+\w+\s+\d{4})", date_str)
                    if date_match:
                        raw = date_match.group(1)
                        for fmt in ("%B %Y", "%d %B %Y"):
                            try:
                                dt = datetime.strptime(raw, fmt)
                                review_date = dt.strftime("%Y-%m-%d")
                                break
                            except ValueError:
                                review_date = datetime.now().strftime("%Y-%m-%d")
                    else:
                        review_date = datetime.now().strftime("%Y-%m-%d")

                    all_reviews.append({
                        "review_text": review_text,
                        "rating": rating,
                        "review_date": review_date,
                        "product_name": product_name,
                        "category": "electronics",
                        "platform": "flipkart",
                    })
                except Exception as e:
                    logger.debug(f"[Flipkart] Review parse error: {e}")
                    continue

        if not all_reviews:
            return None

        return {
            "reviews": all_reviews[:max_reviews],
            "product_name": product_name,
            "platform": "flipkart",
            "scraped_count": len(all_reviews[:max_reviews]),
            "used_fallback": False,
        }

    except ImportError:
        logger.warning("[Flipkart] requests/BeautifulSoup not available, using fallback")
        return None
    except Exception as e:
        logger.info(f"[Flipkart] Scraping failed ({type(e).__name__}): {e}, using fallback")
        return None


def scrape_flipkart(url: str, max_reviews: int = 50) -> Dict[str, Any]:
    """
    Scrape Flipkart product reviews.
    Always returns valid data — falls back to realistic mock data if scraping fails.
    """
    logger.info(f"[Flipkart] Scraping URL: {url} (max={max_reviews})")

    result = _scrape_flipkart_live(url, max_reviews)

    if result and result.get("reviews"):
        logger.info(f"[Flipkart] Live scrape succeeded: {result['scraped_count']} reviews")
        return result

    logger.info("[Flipkart] Using mock fallback data")
    from .mock_data import get_mock_reviews
    return get_mock_reviews(url, max_reviews=max_reviews, platform="flipkart")
