import requests
import csv
import time
import sys
import os

BASE_URL = "https://api.bazaarvoice.com/data/batch.json"

PARAMS = {
    "passkey": "canCX9lvC812oa4Y6HYf4gmWK5uszkZCKThrdtYkZqcYE",
    "apiversion": "5.5",
    "displaycode": "14883-en_us",
    "resource.q0": "reviews",
    "filter.q0": [
        "isratingsonly:eq:false",
        "productid:eq:LONCH",
        "contentlocale:eq:zh*,en*,fr*,de*,ja*,pt*,ru*,es*,en_US",
    ],
    "sort.q0": "submissiontime:desc",
    "stats.q0": "reviews",
    "filteredstats.q0": "reviews",
    "include.q0": "authors,products,comments",
    "filter_reviews.q0": "contentlocale:eq:zh*,en*,fr*,de*,ja*,pt*,ru*,es*,en_US",
    "filter_reviewcomments.q0": "contentlocale:eq:zh*,en*,fr*,de*,ja*,pt*,ru*,es*,en_US",
    "filter_comments.q0": "contentlocale:eq:zh*,en*,fr*,de*,ja*,pt*,ru*,es*,en_US",
}

HEADERS = {
    "sec-ch-ua-platform": '"macOS"',
    "Referer": "https://www.marriott.com/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
    "sec-ch-ua": '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
}

RATING_KEYS = ["Cleanliness", "Location", "Amenities", "Dining", "Service", "Value"]
CSV_COLUMNS = [
    "HotelId",
    "HotelName",
    "ContentLocale",
    "Cleanliness",
    "Location",
    "Amenities",
    "Dining",
    "Service",
    "Value",
    "Title",
    "ReviewText",
    "UserName",
    "SubmissionTime",
]

PAGE_SIZE = 100


def fetch_page(offset, limit):
    params = dict(PARAMS)
    params["limit.q0"] = str(limit)
    params["offset.q0"] = str(offset)
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_rows(results):
    rows = []
    for review in results:
        secondary = review.get("SecondaryRatings") or {}
        row = {
            "HotelId": review.get("ProductId", ""),
            "HotelName": review.get("OriginalProductName", ""),
            "ContentLocale": review.get("ContentLocale", ""),
            "Title": review.get("Title", ""),
            "ReviewText": review.get("ReviewText", ""),
            "UserName": review.get("UserNickname", ""),
            "SubmissionTime": review.get("SubmissionTime", ""),
        }
        for key in RATING_KEYS:
            rating_obj = secondary.get(key)
            row[key] = rating_obj["Value"] if rating_obj else ""
        rows.append(row)
    return rows


def main():
    output_file = "hotel_reviews.csv"

    file_exists = os.path.isfile(output_file) and os.path.getsize(output_file) > 0

    print("Fetching first page to determine total results...")
    data = fetch_page(offset=0, limit=PAGE_SIZE)
    q0 = data["BatchedResults"]["q0"]
    total_results = q0["TotalResults"]
    print(f"Total reviews to fetch: {total_results}")

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()

        results = q0.get("Results", [])
        rows = extract_rows(results)
        writer.writerows(rows)
        fetched = len(results)
        print(f"Page 1: fetched {fetched}/{total_results} reviews")

        offset = PAGE_SIZE
        page = 2
        while offset < total_results:
            time.sleep(1)
            try:
                data = fetch_page(offset=offset, limit=PAGE_SIZE)
                q0 = data["BatchedResults"]["q0"]
                results = q0.get("Results", [])
                if not results:
                    print(f"Page {page}: no results returned, stopping.")
                    break
                rows = extract_rows(results)
                writer.writerows(rows)
                fetched += len(results)
                print(f"Page {page}: fetched {fetched}/{total_results} reviews")
            except requests.exceptions.RequestException as e:
                print(f"Error on page {page} (offset={offset}): {e}", file=sys.stderr)
                print("Retrying in 5 seconds...")
                time.sleep(5)
                continue
            offset += PAGE_SIZE
            page += 1

    print(f"\nDone! {fetched} reviews saved to {output_file}")


if __name__ == "__main__":
    main()
