"""
Synthetic Hotel Review Data Generator
- 3 hotel categories: Luxury, Business, Budget
- 200+ reviews with real-world noise
- Seeded complaint trend: housekeeping/cleanliness complaints spike in last 50 luxury hotel reviews
- Hindi+English (Hinglish) reviews included
- Bot-like repetitive reviews included
- Mixed sentiments within single reviews
- Sub-ratings: Cleanliness, Location, Amenities, Dining, Service & Staff, Value for Money
"""
import random
import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

random.seed(42)
np.random.seed(42)

SUB_RATING_KEYS = ["Cleanliness", "Location", "Amenities", "Dining", "Service & Staff", "Value for Money"]


def _generate_sub_ratings(overall: float) -> Dict[str, float]:
    """Generate sub-ratings that average close to overall rating."""
    target = float(overall)
    raw = np.random.normal(loc=target, scale=0.8, size=6)
    raw = np.clip(raw, 1.0, 5.0)
    diff = target - raw.mean()
    raw = np.clip(raw + diff, 1.0, 5.0)
    raw = np.round(raw, 1)
    return dict(zip(SUB_RATING_KEYS, raw.tolist()))


# ─── LUXURY HOTEL REVIEWS (Hotel Monaco Seattle) ────────────────────────────

LUXURY_REVIEWS = [
    # Positive
    ("Absolutely stunning hotel with impeccable service. The concierge arranged a private dinner and the spa was divine. Room had gorgeous city views and the bed was like sleeping on a cloud.", 5.0, "positive"),
    ("The lobby is breathtaking with its modern art collection. Staff remembered our names by day two. Rooftop pool was pristine and the cocktails were perfectly crafted.", 5.0, "positive"),
    ("Room service was exceptional - arrived within 15 minutes and the food was restaurant quality. The marble bathroom with heated floors was a wonderful touch.", 4.5, "positive"),
    ("Location is unbeatable - walking distance to Pike Place Market and the waterfront. The evening wine reception in the lobby was a lovely surprise.", 5.0, "positive"),
    ("Suite was enormous with a separate living area. Turndown service included chocolates and a handwritten welcome note. Truly five-star experience.", 5.0, "positive"),
    ("The hotel spa treatments were phenomenal. Deep tissue massage was the best I've ever had. Pool area immaculate and never crowded.", 4.5, "positive"),
    ("Valet parking was seamless, bellhop had our bags up before we finished check-in. The pet-friendly policy with goldfish in room was charming.", 4.5, "positive"),

    # Negative
    ("For $400 a night, I expected much better. Room was dated, carpet had stains, and the AC unit rattled all night. Not worth the premium price at all.", 2.0, "negative"),
    ("Terrible noise insulation. Could hear every conversation in the hallway and music from the bar until 2am. Complained twice, nothing was done.", 1.5, "negative"),
    ("Front desk was dismissive and unhelpful. Asked for restaurant recommendations three times and got a shrug each time. Concierge was always 'busy'.", 2.0, "negative"),
    ("Valet lost our car keys for 45 minutes when we needed to leave for the airport. No apology, no compensation. Absolutely unacceptable for a luxury property.", 1.0, "negative"),
    ("Room wasn't ready at 3pm check-in despite booking months ahead. Had to wait 90 minutes in the lobby. Then found hair in the bathtub.", 1.5, "negative"),
    ("The restaurant was overpriced and mediocre. $65 steak was tough and sides were cold. Room service breakfast took 50 minutes.", 2.0, "negative"),
    ("WiFi kept dropping constantly. For a hotel charging this rate, basic connectivity should work. Business center was closed half the time.", 2.5, "negative"),

    # Mixed
    ("Beautiful property and great location, but service has really declined. Staff seemed overwhelmed and disorganized. Room was lovely though.", 3.5, "mixed"),
    ("The suite was gorgeous but housekeeping missed our room twice. Had to call for fresh towels. Dining was excellent when we finally got seated.", 3.0, "mixed"),
    ("Love the quirky decor and personality of this hotel. However, for the price point, the amenities feel dated. Pool is tiny.", 3.5, "mixed"),

    # Hinglish
    ("Bahut hi shaandaar hotel hai! Room spacious aur clean tha. Staff ne bahut acha welcome kiya. Location bhi perfect hai market ke paas.", 5.0, "positive"),
    ("Itne mehenge hotel mein aisa experience? Room mein cockroach mila! Manager se baat ki toh bas sorry bol diya. Paisa barbaad.", 1.5, "negative"),
    ("Hotel ka ambience toh bahut acha hai. Staff bhi friendly hai. But food quality average thi dinner mein. Breakfast was good though.", 3.5, "mixed"),
    ("Check-in mein 1 ghanta laga. Room theek tha but view bilkul nahi tha. Parking charges alag se 40 dollar! Location acha hai but expensive.", 3.0, "mixed"),
    ("Kamaal ka stay! Pool area ekdum mast, spa services excellent. Wife ko bahut pasand aaya. Anniversary ke liye perfect.", 5.0, "positive"),
    ("AC kharab tha room mein. Maintenance wale 2 ghante baad aaye. Bathroom mein garam paani bhi nahi aa raha tha subah.", 2.0, "negative"),

    # Sarcastic
    ("Ah yes, paying $450 a night to hear the elevator ding every 30 seconds. Truly the luxury experience I was promised.", 1.5, "negative"),
    ("'Five-star service' where it takes 3 calls to get extra pillows. The bar was lovely though - needed it after dealing with the front desk.", 2.0, "negative"),
]

# ─── BUSINESS HOTEL REVIEWS ────────────────────────────────────────────────

BUSINESS_REVIEWS = [
    # Positive
    ("Perfect for business travel. Fast WiFi, spacious desk, excellent meeting rooms. Coffee shop in lobby opens at 5:30am which is a lifesaver.", 4.5, "positive"),
    ("Clean, efficient, no-nonsense hotel. Check-in took 2 minutes. Room had everything I needed. Will definitely book again for client meetings.", 4.0, "positive"),
    ("The business center is well-equipped with printers and private phone rooms. Location is ideal - 5 minutes from the convention center.", 4.5, "positive"),
    ("Comfortable bed, quiet room, reliable WiFi. As a frequent business traveler, these are my three requirements and this hotel nails all three.", 4.5, "positive"),
    ("Express checkout saved me when I had an early flight. Breakfast buffet starts at 6am and has good variety. Staff was professional.", 4.0, "positive"),
    ("Room was modern with USB outlets everywhere. Blackout curtains worked perfectly. The gym was small but well-maintained.", 4.0, "positive"),
    ("Great value for a downtown business hotel. Meeting rooms are well-equipped with AV setup. Front desk handled my printing request quickly.", 4.5, "positive"),

    # Negative
    ("WiFi was painfully slow during a crucial video conference. Had to use my phone hotspot. Unacceptable for a business hotel.", 2.0, "negative"),
    ("Conference room booking was a disaster. Double-booked our room and the replacement was a closet with no projector.", 1.5, "negative"),
    ("Thin walls meant I could hear the TV from next door all night. Showed up exhausted to my morning presentation.", 2.0, "negative"),
    ("Parking garage was full by 7pm every night. Had to park 3 blocks away and walk in the rain. No valet option available.", 2.5, "negative"),
    ("Room smelled of cigarette smoke despite being a non-smoking floor. Requested room change and was told nothing was available.", 2.0, "negative"),
    ("Checkout line was insane. 20 minutes wait with only one person at the desk at 7am on a weekday. They know it's a business hotel, right?", 2.5, "negative"),
    ("Breakfast was overpriced and portions were tiny. $18 for toast and eggs is highway robbery.", 2.0, "negative"),

    # Mixed
    ("Location is A+ for business, walking distance to financial district. But the rooms are dated and could use renovation.", 3.5, "mixed"),
    ("Good functional hotel but lacks personality. Rooms are clean but sterile. Perfect for 1-2 nights, wouldn't want to stay longer.", 3.0, "mixed"),

    # Hinglish
    ("Business travel ke liye perfect hotel hai. WiFi fast hai, room mein desk spacious hai. Meeting rooms bhi achhe hain.", 4.5, "positive"),
    ("Office ke paas hai toh convenience ke liye stay kiya. Room average tha, nothing special. Food bilkul bland.", 3.0, "mixed"),
    ("Conference ke liye book kiya tha. AV setup mein problem aayi, IT support ne 30 min laga diya fix karne mein.", 2.5, "negative"),
    ("Achha hotel hai business trip ke liye. Gym mein equipment kam hai but room comfortable hai.", 4.0, "positive"),

    # Sarcastic
    ("A 'business hotel' where the WiFi runs on dial-up speeds. Very on-brand for 2005.", 2.0, "negative"),
]

# ─── BUDGET HOTEL REVIEWS ──────────────────────────────────────────────────

BUDGET_REVIEWS = [
    # Positive
    ("You get what you pay for, and honestly I was pleasantly surprised! Room was small but clean, bed was comfortable enough. Great location near transit.", 4.0, "positive"),
    ("Best value in the city center. Nothing fancy but perfectly clean, friendly staff, and the free breakfast saved us money.", 4.5, "positive"),
    ("For $79 a night downtown, I'm not complaining. Room was basic but had everything needed. Hot shower worked great.", 4.0, "positive"),
    ("Surprised by how clean and well-maintained everything was. Staff was genuinely friendly. Will stay here again to save money.", 4.5, "positive"),
    ("Perfect for a quick overnight stay. Check-in was fast, room was clean, WiFi worked. No frills but no complaints either.", 4.0, "positive"),
    ("The free breakfast was actually decent - fresh fruit, eggs, toast. Room was tight but the location makes up for it.", 4.0, "positive"),

    # Negative
    ("Disgusting. Found bed bugs on the mattress. Hair in the sink. Stains on the carpet. Reported it and got a half-hearted apology.", 1.0, "negative"),
    ("Toilet wouldn't flush properly the entire stay. Hot water ran out by 8am. The 'free breakfast' was stale bread and watered-down coffee.", 1.5, "negative"),
    ("Room smelled like mold. Towels were threadbare and had mysterious stains. The lock on the door felt flimsy and insecure.", 1.5, "negative"),
    ("Noisy all night. Could hear people arguing, doors slamming, and the ice machine grinding right outside my room.", 2.0, "negative"),
    ("Elevator was broken for 3 days (room was on 8th floor). No housekeeping came once during a 4-night stay.", 1.5, "negative"),
    ("The photos online are completely misleading. Room was half the size shown and the 'city view' was a brick wall.", 2.0, "negative"),

    # Mixed
    ("Location is fantastic for the price, literally across from the train station. Room was clean but extremely small. Walls paper thin.", 3.0, "mixed"),
    ("Decent budget option. Don't expect luxury but it's clean and functional. Breakfast is edible. Staff tries their best.", 3.5, "mixed"),
    ("Fine for sleeping. Don't spend time in the room and you'll be happy. The neighborhood has great restaurants nearby.", 3.0, "mixed"),

    # Hinglish
    ("Budget mein best option hai city center mein. Room chota hai but saaf tha. Staff helpful tha.", 4.0, "positive"),
    ("Itna ganda room kabhi nahi dekha. Bedsheet pe daag the, bathroom mein cockroach. Paisa waste.", 1.0, "negative"),
    ("Theek hai budget ke hisaab se. Zyada expect mat karo. Breakfast free mein mil raha hai toh acha hai.", 3.0, "mixed"),
    ("Location achhi hai bus stand ke paas. Room basic hai but ek raat ke liye chalega. AC theek kaam karta hai.", 3.5, "mixed"),

    # Sarcastic
    ("The 'complimentary breakfast' was one banana and instant coffee. Living the high life for sure.", 2.0, "negative"),
]

# ─── SEEDED: Housekeeping/Cleanliness complaints spike (last 50 luxury reviews) ────

LUXURY_SEEDED_CLEANLINESS = [
    ("Beautiful hotel but housekeeping was shocking. Room wasn't cleaned for 2 days despite multiple requests. Found dust everywhere.", 2.5, "mixed"),
    ("Love the property but cleanliness has really gone downhill. Bathroom had soap scum, mirror had fingerprints. Not what I expect here.", 2.5, "negative"),
    ("Third stay here and first time disappointed. Dirty towels left in room, bed wasn't made until 4pm. Housekeeping understaffed clearly.", 2.0, "negative"),
    ("Gorgeous lobby and great location BUT the room had crumbs on the desk, hair on the bathroom floor, and a stained duvet.", 2.5, "mixed"),
    ("Checked in to find the previous guest's coffee cup still on the nightstand. Sheets had wrinkles suggesting they weren't changed.", 1.5, "negative"),
    ("Room was stunning design-wise but the carpet had visible stains and the minibar hadn't been restocked. Housekeeping is slipping.", 3.0, "mixed"),
    ("Love this hotel but the cleanliness standards have dropped significantly. Dusty surfaces, streaky mirrors, and musty smell in closet.", 2.5, "negative"),
    ("Housekeeping dekh ke lagta hai staff kam ho gaya hai. Room saaf nahi tha check-in pe. Bathroom mein baal the. Disappointed.", 2.0, "negative"),
    ("Great hotel otherwise but room cleaning was below par this visit. Had to request clean towels twice. Bin wasn't emptied for 2 days.", 3.0, "mixed"),
    ("The restaurant and spa are still wonderful but rooms are not being maintained properly. Found a used tissue under the bed.", 2.5, "negative"),
    ("Lovely property losing its shine. Literally - dusty lampshades, fingerprint-covered glass tables, soap residue in shower.", 2.5, "negative"),
    ("Why is housekeeping coming at 5pm now? Previously it was always done by noon. Room service trays sat in hallway for hours.", 3.0, "mixed"),
    ("Front desk apologized for the state of the room and offered a discount. Appreciated, but shouldn't happen in the first place.", 2.5, "mixed"),
    ("Bathroom floor was sticky, shower drain had buildup, toilet had water marks. For this price I expect spotless.", 2.0, "negative"),
    ("Saaf safai ka standard bahut gir gaya hai. Pehle aisa nahi tha. Room mein cobweb thi corner mein. Unacceptable.", 2.0, "negative"),
    ("Staff is still friendly and food is great, but they need more housekeeping staff urgently. My room was missed completely one day.", 3.0, "mixed"),
    ("Another visit, another dirty room at check-in. This is becoming a pattern. Management needs to address the housekeeping situation.", 2.0, "negative"),
    ("Beautiful suite with a spectacular view, marred by dusty curtains and a bathrobe that smelled of the previous guest's perfume.", 2.5, "mixed"),
    ("The mini fridge had spills from a previous guest. Housekeeping clearly just wiped surfaces and missed everything else.", 2.5, "negative"),
    ("Hotel is lovely but hygiene standards are concerning post-pandemic. Saw the same housekeeper rush through 3 rooms in 10 minutes.", 2.0, "negative"),
    ("Cleaners came while we were in the room, spent 5 minutes, left dirty towels and never vacuumed. Disappointing.", 2.5, "negative"),
    ("Premium rate hotel with budget-level housekeeping. Trash from yesterday still in the bin, bed just smoothed not changed.", 2.0, "negative"),
    ("Love the location and dining options but the room hygiene has deteriorated noticeably since my last visit 6 months ago.", 3.0, "mixed"),
    ("Found leftover room service menu under the bed that wasn't ours. Sheets looked clean but who knows at this point.", 2.5, "mixed"),
    ("Management please note: your housekeeping team needs reinforcement. Long-time guest and I've never seen standards this low.", 2.5, "negative"),
]

LUXURY_NORMAL_FILLER = [
    ("Exceptional stay as always. Room was perfect, staff outstanding, location ideal.", 5.0, "positive"),
    ("Great hotel for special occasions. Romantic setup was beautiful.", 4.5, "positive"),
    ("Solid luxury option in the city. Would return without hesitation.", 4.5, "positive"),
    ("The renovation looks fantastic. Modern touches while keeping the character.", 5.0, "positive"),
    ("Wonderful anniversary weekend. Everything was perfect from check-in to checkout.", 5.0, "positive"),
    ("Pool area is the best in the city. Great cocktails by the pool.", 4.5, "positive"),
    ("Consistently great stays. This is our go-to hotel in Seattle.", 5.0, "positive"),
    ("Room upgrade was a lovely surprise. King suite was enormous and beautifully furnished.", 5.0, "positive"),
    ("Average stay, nothing wrong but nothing exceptional either.", 3.5, "mixed"),
    ("Good hotel but the restaurant needs a better menu.", 3.5, "mixed"),
]

# ─── EMOJI-RICH REVIEWS ────────────────────────────────────────────────────

EMOJI_REVIEWS = [
    ("❤️ Absolutely love this hotel! 😍 Room was gorgeous and the spa was heavenly ✨ Best anniversary trip ever! 🥂", "Hotel", "Grand Monaco Seattle", 5.0),
    ("😡 Worst hotel experience ever!! Room was FILTHY 🤮 Found hair everywhere 💀 Never coming back!", "Hotel", "Grand Monaco Seattle", 1.0),
    ("😊 Great value for money! 💰 Clean rooms, friendly staff 😄 Perfect location near market 🏪", "Hotel", "City Business Inn", 4.5),
    ("🤮 Bed bugs!!! 🐛 Disgusting bathroom 🚽 This place should be shut down 👎 Zero stars!", "Hotel", "Downtown Budget Stay", 1.0),
    ("🎉 The rooftop bar is AMAZING 🍸 Views are incredible 🌃 Staff made us feel like VIPs 👑", "Hotel", "Grand Monaco Seattle", 5.0),
    ("😭 Paid $400 for a room with no hot water 🥶 AC broken ❌ Very disappointed 💔", "Hotel", "Grand Monaco Seattle", 1.5),
    ("😎 Sleek modern rooms 🔥 Perfect for business travel ⭐ WiFi was lightning fast 💻", "Hotel", "City Business Inn", 4.5),
    ("🤔 Mixed feelings honestly... great location 👍 but room was tiny 😑 and walls thin", "Hotel", "Downtown Budget Stay", 3.0),
    ("🏆 Best hotel in Seattle hands down! Unbelievable service 🙌 The suite was pure luxury ✨", "Hotel", "Grand Monaco Seattle", 5.0),
    ("😞 Expected more for this price. Housekeeping didn't come for 2 days 😟 not acceptable", "Hotel", "Grand Monaco Seattle", 2.0),
    ("Wow!! 🤩 Beautiful lobby! Great breakfast! Comfy bed! This hotel has it all! 💯🏨", "Hotel", "City Business Inn", 5.0),
    ("Awful 😠 Elevator broken for 3 days 💀 Staff didn't care 🚫 Total waste of money 💸", "Hotel", "Downtown Budget Stay", 1.0),
]

# ─── BOT-LIKE REVIEWS ──────────────────────────────────────────────────────

BOT_REVIEWS = [
    {"review_text": "Good hotel good hotel good hotel", "category": "Hotel", "product_name": "Grand Monaco Seattle", "rating": 5.0},
    {"review_text": "Best hotel highly recommend best hotel", "category": "Hotel", "product_name": "City Business Inn", "rating": 5.0},
    {"review_text": "Worst hotel do not stay waste of money", "category": "Hotel", "product_name": "Downtown Budget Stay", "rating": 1.0},
    {"review_text": "Amazing stay amazing stay amazing stay", "category": "Hotel", "product_name": "Grand Monaco Seattle", "rating": 5.0},
    {"review_text": "Five stars five stars excellent hotel five stars", "category": "Hotel", "product_name": "City Business Inn", "rating": 5.0},
    {"review_text": "love it love it love it love it perfect", "category": "Hotel", "product_name": "Grand Monaco Seattle", "rating": 5.0},
]

# ─── EXACT DUPLICATES ──────────────────────────────────────────────────────

DUPLICATE_REVIEWS = [
    {"review_text": "For $400 a night, I expected much better. Room was dated, carpet had stains, and the AC unit rattled all night. Not worth the premium price at all.", "category": "Hotel", "product_name": "Grand Monaco Seattle", "rating": 2.0},
    {"review_text": "Best value in the city center. Nothing fancy but perfectly clean, friendly staff, and the free breakfast saved us money.", "category": "Hotel", "product_name": "Downtown Budget Stay", "rating": 4.5},
]


def generate_synthetic_dataset() -> List[Dict[str, Any]]:
    """Generate the full synthetic hotel review dataset."""
    reviews = []
    base_date = datetime(2024, 1, 1)

    def make_review(text, category, product_name, rating, idx, days_offset=0):
        review_date = (base_date + timedelta(days=days_offset + idx // 3)).strftime("%Y-%m-%d")
        sub_ratings = _generate_sub_ratings(rating)
        return {
            "id": str(uuid.uuid4())[:8],
            "review_text": text,
            "category": category,
            "product_name": product_name,
            "rating": rating,
            "review_date": review_date,
            "helpful_votes": random.randint(0, 50),
            "verified_purchase": random.choice([True, True, True, False]),
            **sub_ratings,
        }

    # Luxury Hotel (70 reviews)
    for i, (text, rating, _) in enumerate(LUXURY_REVIEWS * 3):
        if i > len(LUXURY_REVIEWS):
            text = text + random.choice(["", " Overall lovely property.", " Would book again.", " Great for special occasions."])
        reviews.append(make_review(text, "Hotel", "Grand Monaco Seattle", rating, i, 0))

    # Business Hotel (60 reviews)
    for i, (text, rating, _) in enumerate(BUSINESS_REVIEWS * 3):
        if i > len(BUSINESS_REVIEWS):
            text = text + random.choice(["", " Good for work trips.", " Functional and clean.", ""])
        reviews.append(make_review(text, "Hotel", "City Business Inn", rating, i, 100))

    # Budget Hotel - early batch (25 reviews)
    for i, (text, rating, _) in enumerate(BUDGET_REVIEWS):
        reviews.append(make_review(text, "Hotel", "Downtown Budget Stay", rating, i, 200))

    # Luxury - filler normal (10 reviews)
    for i, (text, rating, _) in enumerate(LUXURY_NORMAL_FILLER):
        reviews.append(make_review(text, "Hotel", "Grand Monaco Seattle", rating, i, 220))

    # Luxury - SEEDED CLEANLINESS COMPLAINTS (25 reviews, last batch)
    for i, (text, rating, _) in enumerate(LUXURY_SEEDED_CLEANLINESS):
        reviews.append(make_review(text, "Hotel", "Grand Monaco Seattle", rating, i, 230))

    # Add bot reviews
    for bot in BOT_REVIEWS:
        bot["id"] = str(uuid.uuid4())[:8]
        bot["review_date"] = "2024-06-01"
        bot["helpful_votes"] = 0
        bot["verified_purchase"] = False
        bot.update(_generate_sub_ratings(bot["rating"]))
        reviews.append(bot)

    # Add duplicates
    for dup in DUPLICATE_REVIEWS:
        dup["id"] = str(uuid.uuid4())[:8]
        dup["review_date"] = "2024-03-15"
        dup["helpful_votes"] = 1
        dup["verified_purchase"] = True
        dup.update(_generate_sub_ratings(dup["rating"]))
        reviews.append(dup)

    # Add emoji-rich reviews
    for i, (text, cat, product, rating) in enumerate(EMOJI_REVIEWS):
        reviews.append(make_review(text, cat, product, rating, i, 300))

    random.shuffle(reviews)
    return reviews


if __name__ == "__main__":
    import json
    dataset = generate_synthetic_dataset()
    print(f"Generated {len(dataset)} reviews")

    cats = {}
    for r in dataset:
        cats[r.get("product_name", "unknown")] = cats.get(r.get("product_name", "unknown"), 0) + 1
    print(f"Hotels: {cats}")

    ratings = [r["rating"] for r in dataset]
    print(f"Avg rating: {sum(ratings)/len(ratings):.2f}")

    with open("synthetic_reviews.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print("Saved to synthetic_reviews.json")
