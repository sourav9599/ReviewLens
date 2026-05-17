"""
Pre-loaded mock review data for scraper fallback.
Realistic, varied reviews for common product categories.
"""
import random
from datetime import datetime, timedelta


def _random_date(days_back=365):
    """Generate a random date within the last N days."""
    dt = datetime.now() - timedelta(days=random.randint(1, days_back))
    return dt.strftime("%Y-%m-%d")


def _pick(lst):
    return random.choice(lst)


# ─── Category keyword detection ────────────────────────────────────────────────

CATEGORY_KEYWORDS = {
    "headphones": ["headphone", "earphone", "earbuds", "headset", "buds", "airpods", "neckband", "tws"],
    "phone":      ["phone", "mobile", "smartphone", "iphone", "galaxy", "redmi", "poco", "realme", "oneplus", "pixel"],
    "laptop":     ["laptop", "notebook", "macbook", "thinkpad", "vivobook", "zenbook", "aspire", "inspiron", "pavilion"],
    "tv":         ["tv", "television", "oled", "qled", "smart-tv", "smarttv"],
    "camera":     ["camera", "dslr", "mirrorless", "gopro", "webcam", "nikon", "canon", "sony-a"],
    "watch":      ["watch", "smartwatch", "fitbit", "garmin", "amazfit", "strap"],
    "speaker":    ["speaker", "soundbar", "bluetooth-speaker", "bose", "jbl", "harman"],
    "tablet":     ["tablet", "ipad", "tab", "galaxy-tab"],
    "charger":    ["charger", "powerbank", "power-bank", "adapter", "usb-c"],
    "shoes":      ["shoe", "sneaker", "running", "sports-shoe", "boot", "sandal"],
}


def detect_category_from_url(url: str) -> str:
    url_lower = url.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in url_lower for kw in keywords):
            return category
    return "electronics"


# ─── Mock review banks per category ───────────────────────────────────────────

MOCK_REVIEWS = {
    "headphones": {
        "product_name": "ProSound Elite ANC Wireless Earbuds",
        "reviews": [
            ("Sound quality is outstanding, the bass is punchy without being overwhelming. Highly recommend!", 5),
            ("Noise cancellation works great in office environments. Worth every rupee.", 5),
            ("Battery life is excellent — easily lasts 8 hours on a single charge.", 5),
            ("Very comfortable to wear even during long work calls. The fit is snug.", 4),
            ("Great value for money. Sound signature is balanced and detailed.", 4),
            ("Touch controls take getting used to but are responsive once you learn them.", 4),
            ("ANC is decent but not class-leading. Works well for commuting though.", 4),
            ("Pairing is seamless with both Android and iPhone. Love the multipoint feature.", 5),
            ("The case feels premium and charges the buds quickly. Good build quality overall.", 4),
            ("Microphone quality is surprisingly good for video calls.", 4),
            ("Sound quality could be better at this price. My old wired headphones sounded fuller.", 3),
            ("Ear tips hurt after about 2 hours of continuous use. Need better tip options.", 3),
            ("Bass is too overpowering. Would prefer a more neutral sound profile.", 2),
            ("One earbud stopped charging after 2 weeks. Contacted support but no response.", 2),
            ("Delivery was fast but packaging was damaged. Product itself seems fine.", 3),
            ("Connectivity drops occasionally when walking around. Not ideal for workouts.", 2),
            ("The app keeps crashing on my phone. Cannot access EQ settings at all.", 1),
            ("Returned the product. Sound quality was not worth the asking price.", 1),
            ("Expected better. My previous earbuds at half the price performed better.", 2),
            ("Water resistance is a joke. Got splashed lightly and one earbud malfunctioned.", 1),
            ("Amazing product! Using it for 3 months and it's still going strong.", 5),
            ("Perfect for gym use. Stays in place even during intense workouts.", 5),
            ("Customer service resolved my issue quickly. Good after-sales support.", 4),
            ("Volume control is intuitive. Sound leakage is minimal at high volumes.", 4),
            ("Great for the price. Not perfect but does the job well.", 4),
            ("Yaar ye earbuds bahut acha hai! Bass bilkul tighthai aur sound crisp lagta hai.", 5),
            ("Mast product hai bhai. Office mein noise cancellation se concentrate kar pata hoon.", 5),
            ("Thoda sa tight fit hai but sound quality ekdum top notch. Happy purchase!", 4),
            ("Packaging bohot acha tha. Product bhi genuine lag raha hai. 4 stars.", 4),
            ("Pehle se better headphones use kiya tha, but iske liye price sahi hai.", 3),
        ]
    },
    "phone": {
        "product_name": "TechPro Ultra 5G Smartphone",
        "reviews": [
            ("Camera quality is stunning in daylight. Night mode is also impressive.", 5),
            ("Battery easily lasts a full day with heavy usage. Fast charging is a bonus.", 5),
            ("Performance is smooth on MIUI. No lags even with multiple apps open.", 5),
            ("Display is crisp and bright. Colors look natural and vibrant.", 5),
            ("Build quality feels premium. The glass back looks and feels great.", 4),
            ("Gaming performance is top notch. Plays BGMI at max settings without heating.", 5),
            ("Fingerprint sensor is fast and accurate. Face unlock works in dim light too.", 4),
            ("MIUI ads are annoying but overall phone experience is great.", 4),
            ("Camera app has many modes and options. Portrait mode is my favorite.", 4),
            ("Phone gets slightly warm during long gaming sessions but nothing extreme.", 3),
            ("Expected better low-light camera performance at this price point.", 3),
            ("Software updates are slow to arrive. Security patches are outdated.", 2),
            ("Speaker quality is average. Would have preferred stereo speakers.", 3),
            ("Charging brick not included in box. Not acceptable at this price.", 2),
            ("Phone slipped from my hands due to glass back. No case provided either.", 2),
            ("Screen protector peeled off in a month. Poor quality included protector.", 2),
            ("Call quality is below average. Earpiece volume is too low on calls.", 2),
            ("Phone restarted randomly twice in the first week. Bit worrying.", 1),
            ("Returned it. Competitor offers better specs at similar price.", 1),
            ("Heating issues in summer. Cannot use for extended periods outdoors.", 2),
            ("Perfect daily driver. Using it for 6 months with zero issues.", 5),
            ("Value for money is incredible. Best phone under this budget.", 5),
            ("Highly recommend to anyone looking for a reliable midrange phone.", 5),
            ("Camera updates keep improving the quality. Love the continuous improvement.", 4),
            ("Great phone for students. Handles everything I throw at it.", 4),
            ("Bhai is phone ka camera toh zabardast hai! BGMI bhi smooth chal raha hai.", 5),
            ("Ekdum mast phone hai yaar. Battery life bhi bahut acha hai.", 5),
            ("Samsung se switch kiya. Iss phone ki camera quality better hai bhai.", 4),
            ("Price ke hisaab se best option hai market mein. Recommend karunga.", 4),
            ("Display sundar hai. Raat ko bhi achhe se dikh raha hai screen.", 4),
        ]
    },
    "laptop": {
        "product_name": "PowerBook Pro 15 Laptop",
        "reviews": [
            ("Battery life is exceptional. 8+ hours easily on moderate workload.", 5),
            ("Performance is snappy. Boots in under 10 seconds. SSD is blazing fast.", 5),
            ("Display is gorgeous. IPS panel with great color accuracy for design work.", 5),
            ("Build quality is solid. Feels premium and durable for daily use.", 4),
            ("Keyboard is comfortable to type on for long periods. Good key travel.", 4),
            ("Lightweight design is perfect for frequent travelers. Fits in any bag.", 5),
            ("Handles multitasking well. No slowdowns with 15+ tabs in Chrome.", 4),
            ("Thermals are well managed. Fans are quiet even under load.", 4),
            ("Wi-Fi connectivity is strong and stable. No drops even far from router.", 4),
            ("Good port selection. HDMI, USB-A, USB-C all included. No dongles needed.", 4),
            ("Speaker quality is average for a laptop at this price.", 3),
            ("Trackpad is decent but not as smooth as MacBook. Some jitter noticed.", 3),
            ("RAM is not upgradeable. Sealed unit is a design flaw.", 2),
            ("Heating under load is noticeable. Fan noise increases significantly.", 3),
            ("Webcam quality is poor. 720p is not acceptable in 2024.", 2),
            ("Fingerprint sensor is unreliable in humid weather.", 2),
            ("Pre-installed bloatware took time to clean up. Annoying.", 2),
            ("Display has poor viewing angles. Colors shift when looking from side.", 1),
            ("Hinges feel loose after 6 months. Build quality declined.", 1),
            ("Battery degraded to 80% in 8 months. Not acceptable.", 1),
            ("Perfect for college students and working professionals.", 5),
            ("Handles video editing smoothly. Rendering times are reasonable.", 5),
            ("Best laptop I have owned. Would buy again without hesitation.", 5),
            ("Customer service sorted my issue in 2 days. Great support experience.", 4),
            ("Very happy with this purchase. Meets all my work requirements.", 4),
            ("Coding pe use karta hoon. PyCharm aur VS Code dono smooth chalte hain.", 5),
            ("Office work ke liye perfect hai. Battery bhi full day chalti hai.", 4),
            ("Price thoda jyada hai but quality ke hisaab se justified hai.", 3),
            ("Laptop bohot fast hai. Startup time 10 seconds se bhi kam hai.", 5),
            ("Graphic design ke liye use karta hoon. Display colors bahut accurate hain.", 4),
        ]
    },
    "electronics": {
        "product_name": "TechGear Pro Electronics",
        "reviews": [
            ("Excellent product. Works exactly as described. Very happy with the purchase.", 5),
            ("Great value for money. Quality exceeds expectations at this price point.", 5),
            ("Fast delivery and well packaged. Product is genuine and works well.", 5),
            ("Good build quality. Feels premium and durable.", 4),
            ("Setup was easy. Instructions are clear and product worked right away.", 4),
            ("Performance is consistent. No issues after 2 months of regular use.", 4),
            ("Design is sleek and modern. Looks good in my home setup.", 4),
            ("Customer support was helpful when I had a query.", 4),
            ("Solid product overall. A few minor quirks but nothing deal-breaking.", 3),
            ("Battery or power consumption is reasonable. Energy efficient.", 4),
            ("Quality control seems inconsistent. Got a unit with minor defects.", 3),
            ("Expected more features at this price. Feels basic.", 2),
            ("Instructions are poorly written. Hard to set up without online help.", 2),
            ("Product stopped working after 3 months. Quality is questionable.", 2),
            ("Packaging was damaged on arrival. Seller should improve shipping.", 2),
            ("Returns process was smooth. Got a replacement quickly.", 3),
            ("Heating issue noticed during extended use. Concerning.", 2),
            ("Not worth the price. Better alternatives available.", 1),
            ("Product doesn't match the description. Misleading listing.", 1),
            ("Worst purchase this year. Do not recommend.", 1),
            ("Amazing product! Zero complaints after daily use.", 5),
            ("Highly recommended. Best in its category.", 5),
            ("Repeat buyer. This is my second unit and it's equally good.", 5),
            ("Exactly what I needed. No fuss, just works.", 4),
            ("Happy with the purchase. Would recommend to friends.", 4),
            ("Bahut acha product hai. Delivery bhi fast thi.", 5),
            ("Quality ke hisaab se price bilkul sahi hai.", 4),
            ("Genuine product mila hai. Seller trustworthy lag raha hai.", 4),
            ("Mast experience raha. Dobara khareedunga zaroor.", 5),
            ("Decent product. Expectations meet kiya.", 3),
        ]
    },
    "shoes": {
        "product_name": "RunFast Athletic Shoes",
        "reviews": [
            ("Super comfortable from day one. No break-in period required.", 5),
            ("Cushioning is excellent for long runs. Knees feel much better.", 5),
            ("Lightweight design reduces fatigue during workouts.", 5),
            ("Grip is excellent on wet surfaces. Very safe for running.", 4),
            ("True to size. Ordered my regular size and it fit perfectly.", 4),
            ("Breathable upper keeps feet cool during summer workouts.", 4),
            ("Great for both gym and casual wear. Versatile design.", 4),
            ("Arch support is good. My plantar fasciitis hasn't flared up.", 5),
            ("Looks premium. Got many compliments on these shoes.", 4),
            ("Value for money. Performs like shoes twice the price.", 4),
            ("Sole started separating after 3 months. Quality issue.", 2),
            ("Sizing runs small. Should have ordered half a size up.", 3),
            ("Color faded after washing. Not as advertised.", 2),
            ("Toe box is too narrow for wide feet. Uncomfortable.", 2),
            ("Squeaking sound while walking on smooth floors. Embarrassing.", 2),
            ("Not waterproof as claimed. Feet got wet in light drizzle.", 1),
            ("Stitching came undone in 6 weeks. Poor durability.", 1),
            ("Cushioning deflated quickly. Lost comfort after 2 months.", 2),
            ("Return was smooth but wasted 2 weeks. Disappointed.", 2),
            ("Not recommended for serious runners. Heel support is lacking.", 2),
            ("Best running shoes I have ever owned. Worth every rupee.", 5),
            ("Using for marathon training. No blisters or discomfort.", 5),
            ("My whole family now uses this brand. Loyal customer.", 5),
            ("Gym trainer recommended these. Best recommendation ever.", 5),
            ("Perfect for morning walks. Comfortable and supportive.", 4),
        ]
    }
}


def get_mock_reviews(url: str, max_reviews: int = 30, platform: str = "amazon") -> dict:
    """
    Return realistic mock reviews for a given URL.
    Detects category from URL keywords and returns appropriate reviews.
    """
    category = detect_category_from_url(url)
    bank = MOCK_REVIEWS.get(category, MOCK_REVIEWS["electronics"])

    product_name = bank["product_name"]
    raw_reviews = bank["reviews"]

    # Shuffle and limit
    pool = list(raw_reviews) * 3  # allow repetition for larger requests
    random.shuffle(pool)
    selected = pool[:max_reviews]

    result = []
    for text, rating in selected:
        result.append({
            "review_text": text,
            "rating": rating,
            "review_date": _random_date(180),
            "product_name": product_name,
            "category": category,
            "platform": platform,
        })

    return {
        "reviews": result,
        "product_name": product_name,
        "platform": platform,
        "scraped_count": len(result),
        "used_fallback": True,
        "category": category,
    }
