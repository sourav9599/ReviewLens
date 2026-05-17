"""
ReviewIQ Scrapers Package
Amazon.in and Flipkart review scrapers with smart mock fallback.
"""
from .amazon_scraper import scrape_amazon
from .flipkart_scraper import scrape_flipkart

__all__ = ["scrape_amazon", "scrape_flipkart"]
