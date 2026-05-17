"""
ReviewIQ — Amazon.in Review Scraper
Uses requests + BeautifulSoup with rotating user agents.
Falls back silently to mock data if scraping is blocked.
"""
import logging
import re
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# User agent pool (no dependency on fake-useragent for robustness)
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]


def _get_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }


def _extract_asin(url: str) -> Optional[str]:
    """Extract ASIN from Amazon URL."""
    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"/product/([A-Z0-9]{10})",
        r"ASIN=([A-Z0-9]{10})",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


def _parse_rating(rating_str: str) -> int:
    """Parse rating string like '4.0 out of 5 stars' → 4"""
    try:
        m = re.search(r"(\d+(\.\d+)?)", rating_str)
        if m:
            return round(float(m.group(1)))
    except Exception:
        pass
    return 3


def _scrape_amazon_live(url: str, max_reviews: int) -> Optional[Dict]:
    """Attempt live scraping of Amazon reviews. Returns None on failure."""
    try:
        import requests
        from bs4 import BeautifulSoup

        asin = _extract_asin(url)
        if not asin:
            logger.warning("[Amazon] Could not extract ASIN from URL")
            return None

        reviews_url = f"https://www.amazon.in/product-reviews/{asin}?reviewerType=all_reviews&pageSize=10"
        product_name = "Amazon Product"
        all_reviews: List[Dict] = []

        pages = min((max_reviews // 10) + 1, 5)

        for page in range(1, pages + 1):
            if len(all_reviews) >= max_reviews:
                break

            page_url = f"{reviews_url}&pageNumber={page}"
            time.sleep(random.uniform(1.0, 2.5))

            resp = requests.get(page_url, headers=_get_headers(), timeout=10)

            # Detect block
            if resp.status_code != 200:
                logger.info(f"[Amazon] HTTP {resp.status_code} on page {page}, using fallback")
                return None

            soup = BeautifulSoup(resp.content, "lxml")

            # Check for CAPTCHA / robot check page
            if "robot" in resp.text.lower() or "captcha" in resp.text.lower():
                logger.info("[Amazon] CAPTCHA detected, using fallback")
                return None

            # Extract product name once
            if page == 1:
                title_el = soup.select_one("a[data-hook='product-link']")
                if title_el:
                    product_name = title_el.get_text(strip=True)

            # Extract reviews
            review_divs = soup.select("div[data-hook='review']")
            if not review_divs and page == 1:
                logger.info("[Amazon] No review divs found, using fallback")
                return None

            for div in review_divs:
                if len(all_reviews) >= max_reviews:
                    break
                try:
                    text_el = div.select_one("span[data-hook='review-body'] span")
                    rating_el = div.select_one("i[data-hook='review-star-rating'] span")
                    date_el = div.select_one("span[data-hook='review-date']")

                    if not text_el:
                        continue

                    review_text = text_el.get_text(strip=True)
                    if len(review_text) < 10:
                        continue

                    rating = _parse_rating(rating_el.get_text(strip=True) if rating_el else "3")
                    date_str = date_el.get_text(strip=True) if date_el else ""
                    # Parse "Reviewed in India on 5 January 2024"
                    date_match = re.search(r"(\d{1,2}\s+\w+\s+\d{4})", date_str)
                    if date_match:
                        try:
                            dt = datetime.strptime(date_match.group(1), "%d %B %Y")
                            review_date = dt.strftime("%Y-%m-%d")
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
                        "platform": "amazon",
                    })
                except Exception as e:
                    logger.debug(f"[Amazon] Review parse error: {e}")
                    continue

        if not all_reviews:
            return None

        return {
            "reviews": all_reviews[:max_reviews],
            "product_name": product_name,
            "platform": "amazon",
            "scraped_count": len(all_reviews[:max_reviews]),
            "used_fallback": False,
        }

    except ImportError:
        logger.warning("[Amazon] requests/BeautifulSoup not available, using fallback")
        return None
    except Exception as e:
        logger.info(f"[Amazon] Scraping failed ({type(e).__name__}): {e}, using fallback")
        return None


def scrape_amazon(url: str, max_reviews: int = 50) -> Dict[str, Any]:
    """
    Scrape Amazon.in product reviews.
    Always returns valid data — falls back to realistic mock data if scraping fails.
    """
    logger.info(f"[Amazon] Scraping URL: {url} (max={max_reviews})")

    # Try live scraping first
    result = _scrape_amazon_live(url, max_reviews)

    if result and result.get("reviews"):
        logger.info(f"[Amazon] Live scrape succeeded: {result['scraped_count']} reviews")
        return result

    # Silent fallback to mock data
    logger.info("[Amazon] Using mock fallback data")
    from .mock_data import get_mock_reviews
    return get_mock_reviews(url, max_reviews=max_reviews, platform="amazon")
