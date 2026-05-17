"""
Synthetic Review Data Generator
- 3 product categories: Smartphones, Protein Powder, Bluetooth Earphones
- 200+ reviews with real-world noise
- Seeded complaint trend: packaging complaints spike in last 50 earphone reviews
- Hindi+English (Hinglish) reviews included
- Bot-like repetitive reviews included
- Mixed sentiments within single reviews
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

random.seed(42)

SMARTPHONE_REVIEWS = [
    # Positive
    ("The battery life on this phone is absolutely incredible! Easily lasts 2 days with heavy usage.", 4.5, "positive"),
    ("Camera quality is outstanding, especially in low light conditions. Colors are vibrant and natural.", 5.0, "positive"),
    ("Smooth performance even with 20+ apps open. The 12GB RAM really makes a difference.", 4.5, "positive"),
    ("Screen display is gorgeous. AMOLED with 120Hz refresh rate is buttery smooth.", 5.0, "positive"),
    ("Build quality is premium. Glass back and metal frame feel solid in hand.", 4.0, "positive"),
    ("Fast charging is a game changer - 0 to 100% in just 45 minutes!", 5.0, "positive"),
    ("Face unlock and fingerprint sensor both work flawlessly.", 4.5, "positive"),
    
    # Negative
    ("Battery drains super fast! Goes from 100% to 20% in just 4 hours of normal use. Very disappointed.", 1.5, "negative"),
    ("The camera app keeps crashing every time I try to use portrait mode. Software is buggy.", 2.0, "negative"),
    ("Phone heats up a lot during gaming or video calls. Can barely hold it after 30 minutes.", 2.0, "negative"),
    ("Display has dead pixels after 2 months. Quality control is terrible.", 1.5, "negative"),
    ("Speaker quality is tinny and too low. Can't hear calls in crowded places.", 2.0, "negative"),
    ("Fingerprint sensor fails 3 out of 5 times. Very frustrating.", 2.5, "negative"),
    ("Customer support was absolutely useless. Took 3 weeks just to get a response.", 1.0, "negative"),
    ("The charging cable stopped working after 1 week. Cheap accessories bundled.", 2.0, "negative"),
    
    # Mixed
    ("Good camera but battery life is terrible. Love the design, hate the performance.", 3.0, "mixed"),
    ("Fast processor but gets extremely hot. Display is amazing though.", 3.5, "mixed"),
    ("Excellent build quality and premium feel but software has too many bugs and crashes.", 3.0, "mixed"),
    
    # Hinglish
    ("Bahut acha phone hai! Battery backup toh kamaal ka hai, pura din chalta hai. Camera bhi zabardast.", 4.5, "positive"),
    ("Yaar ye phone toh bekaar nikla. Itne paison mein itni kharab battery? Ek din bhi nahi chalta.", 1.5, "negative"),
    ("Phone ka design toh bahut acha hai, but performance thoda slow hai. Mixed feelings hain.", 3.0, "mixed"),
    ("Screen quality ekdum mast hai! AMOLED display bahut sharp aur vibrant hai. Happy purchase.", 5.0, "positive"),
    ("Charging speed bahut slow hai yaar. 3 ghante mein bhi full charge nahi hota. Frustrating.", 2.0, "negative"),
    ("Phone accha hai overall. Camera mein thoda improvement chahiye tha but acceptable.", 3.5, "positive"),
    
    # Sarcastic
    ("Oh wow, the battery dies in 3 hours. Absolutely PERFECT for a premium flagship phone.", 1.0, "negative"),
    ("Yeah sure, 'flagship performance' that lags on basic apps. Great investment.", 1.5, "negative"),
]

PROTEIN_POWDER_REVIEWS = [
    # Positive
    ("Chocolate flavor tastes amazing! Mixes perfectly with both milk and water, no clumps at all.", 5.0, "positive"),
    ("Results are visible in just 3 weeks. Gained 2kg muscle mass with regular training.", 4.5, "positive"),
    ("Protein content is excellent for the price. 25g per scoop is great value.", 4.5, "positive"),
    ("Digestion is smooth, no bloating or gas issues unlike other brands I've tried.", 5.0, "positive"),
    ("Packaging is very secure and the scoop measurement is accurate.", 4.0, "positive"),
    ("Chocolate and vanilla both taste good. Vanilla is slightly better in my opinion.", 4.0, "positive"),
    ("Delivery was fast and the product was well sealed. No issues.", 4.5, "positive"),
    
    # Negative
    ("Terrible taste - artificial sweetener aftertaste is unbearable. Couldn't finish even 1 bag.", 1.5, "negative"),
    ("Clumps massively even with a shaker. Lumpy texture is disgusting.", 2.0, "negative"),
    ("Caused severe stomach cramps and bloating. Had to stop after 3 days.", 1.5, "negative"),
    ("Scoop size has gotten smaller but price increased. Cheating loyal customers.", 2.0, "negative"),
    ("Protein content doesn't match what's on the label. Very suspicious.", 1.0, "negative"),
    ("Packaging arrived completely damaged. Powder was spilling everywhere in the box.", 2.0, "negative"),
    ("Expiry date was just 1 month away when delivered. Very poor stock management.", 2.0, "negative"),
    
    # Mixed
    ("Great protein content and results, but the taste in vanilla flavor is quite bad. Chocolate is fine.", 3.5, "mixed"),
    ("Good results but causes some bloating in the beginning. Taste is acceptable.", 3.0, "mixed"),
    
    # Hinglish
    ("Yeh protein powder bahut acha hai! Taste bilkul natural sa hai, koi artificial flavour nahi.", 5.0, "positive"),
    ("Stomach upset hua pehle week mein. Baad mein theek ho gaya. Results toh dikh rahe hain.", 3.5, "mixed"),
    ("Packaging bekar thi, box toot ke aaya. Powder theek tha thankfully.", 3.0, "mixed"),
    ("Chocolate flavor bahut mast hai! Gym ke baad perfect recovery drink.", 5.0, "positive"),
    ("Khaali paisa barbad. Na taste acha, na results. Dusra brand le lena.", 1.5, "negative"),
    
    # Sarcastic
    ("'Premium quality' protein powder that clumps like cement. So premium.", 1.0, "negative"),
]

# Earphone reviews WITH SEEDED PACKAGING COMPLAINT TREND in last 50 reviews
EARPHONE_REVIEWS_EARLY = [
    ("Sound quality is phenomenal! Deep bass and crystal clear treble.", 5.0, "positive"),
    ("ANC is excellent, blocks out all office noise completely.", 5.0, "positive"),
    ("Battery lasts 8 hours with ANC on, 12 hours without. Very good.", 4.5, "positive"),
    ("Comfortable fit, wore them for 4 hours straight without discomfort.", 4.5, "positive"),
    ("Bluetooth connection is stable and range is impressive.", 4.0, "positive"),
    ("Touch controls are intuitive and responsive.", 4.5, "positive"),
    ("Call quality is clear on both ends. Microphone picks up voice well.", 4.0, "positive"),
    ("Great value for money compared to Sony and Bose.", 4.5, "positive"),
    ("Easy pairing with multiple devices.", 4.0, "positive"),
    ("Bass is good but slightly overdone for classical music listeners.", 3.5, "mixed"),
    ("Left earbud sometimes disconnects from the right one. Annoying.", 2.5, "negative"),
    ("ANC is average, not as good as the premium brands.", 3.0, "mixed"),
    ("Sound is good but mic quality during calls is poor.", 3.0, "mixed"),
    ("Earbuds fit well but the case feels cheap.", 3.5, "mixed"),
    ("Battery life decreased after 6 months of use.", 3.0, "negative"),
    ("Sound quality amazing, packaging was standard, everything intact.", 4.5, "positive"),
    ("Great earphones, packaging was neat and presentable.", 4.5, "positive"),
    ("Music experience is superb. No complaints about unboxing.", 5.0, "positive"),
    ("ANC toh ekdum kamaal hai! Sab noise block ho jaata hai.", 5.0, "positive"),
    ("Sound bahut acha hai, comfortable bhi hai. Highly recommend.", 4.5, "positive"),
    ("Thoda overpriced hai for the features, but quality is good.", 3.5, "mixed"),
    ("Connectivity issues sometimes. Music cuts out randomly.", 2.5, "negative"),
    ("Perfect for gym workouts. Stays in ear even during running.", 4.5, "positive"),
    ("Very disappointed with battery backup. Only 4 hours actual usage.", 2.0, "negative"),
    ("Great product for the price. Would recommend to friends.", 4.0, "positive"),
]

# SEEDED: Packaging complaints spike - last 50 reviews will show 35-40% packaging complaint rate
EARPHONE_REVIEWS_SEEDED_PACKAGING_ISSUES = [
    ("Earphones sound great but packaging was completely crushed when I received it. Had to check if product was damaged.", 3.0, "mixed"),
    ("Sound is good. BUT the packaging - absolute disaster. Box was torn, no protective wrapping.", 3.0, "mixed"),
    ("Worst unboxing experience! The case was scratched because packaging had no protection.", 2.5, "negative"),
    ("Product seems fine but packaging was a joke. Just a thin cardboard with no padding.", 3.0, "mixed"),
    ("Packaging damaged in transit. Lucky the earphones weren't broken. Needs better packaging.", 3.5, "mixed"),
    ("Great sound quality! But packaging was terrible, arrived in a crushed box.", 3.5, "mixed"),
    ("Love the earphones but packaging needs major improvement. Arrived with dents.", 4.0, "positive"),
    ("Packaging toh bekar hai, box toot ke aaya. Earphones theek hain thankfully.", 3.0, "mixed"),
    ("ANC is superb but packaging quality is very poor. Not worthy of this price.", 3.5, "mixed"),
    ("Earbuds work great but the packaging was ripped. Seller should use better materials.", 3.0, "mixed"),
    ("Nice product, terrible packaging. Box had water damage clearly.", 2.5, "negative"),
    ("Why is the packaging so bad? Third time ordering and each time box arrives damaged.", 2.0, "negative"),
    ("Sound quality 10/10. Packaging 1/10. Company needs to fix their shipping packaging.", 3.0, "mixed"),
    ("Received with packaging damage. Luckily earphones ok. Please use more padding.", 3.5, "mixed"),
    ("Bahut gussa aaya packaging dekh ke! Sundar box mein aana chahiye tha. Product theek hai.", 3.0, "mixed"),
    ("Battery amazing, sound quality great, but packaging was really poor, no bubble wrap.", 4.0, "positive"),
    ("Another order, another damaged packaging. The earphones are good but this is unacceptable.", 2.5, "negative"),
    ("Great earphones. One request - please improve packaging, box arrives dented every time.", 4.0, "positive"),
    ("ANC awesome! Bass amazing! But packaging kept delaying my excitement - was damaged.", 4.0, "positive"),
    ("The earphones are fantastic. Packaging however is consistently bad in every order I've seen.", 3.5, "mixed"),
    ("Sound quality is top notch! Touch controls very responsive. Packaging though arrived squished.", 4.5, "positive"),
    ("Package arrived completely open - not sealed properly. Product inside was fine though.", 3.0, "mixed"),
    ("Third order from this brand. Sound quality never disappoints. Packaging always disappoints.", 4.0, "positive"),
    ("Earphones perfect. Packaging literally had someone's boot print on it.", 3.5, "mixed"),
    ("Love the product. Hate the packaging experience. Please switch to proper protective casing.", 4.0, "positive"),
]

# Fill remaining earphone reviews (normal)
EARPHONE_REVIEWS_NORMAL_FILLER = [
    ("Excellent earphones! Great sound, great battery, great overall.", 5.0, "positive"),
    ("Good earphones for daily commute use.", 4.0, "positive"),
    ("Sound could be better at high volumes. Slight distortion.", 3.0, "mixed"),
    ("Connectivity keeps dropping. Need to fix firmware.", 2.5, "negative"),
    ("Best earphones in this price range. Highly recommend.", 5.0, "positive"),
    ("Comfortable and good sound, happy with purchase.", 4.5, "positive"),
    ("Mic is poor, rest is great.", 3.5, "mixed"),
    ("ANC could be stronger but overall good.", 3.5, "mixed"),
    ("Perfect gift for music lovers.", 5.0, "positive"),
    ("Battery life is fantastic. No other complaints.", 4.5, "positive"),
]

# Emoji-rich reviews (tests emoji analysis agent)
EMOJI_REVIEWS = [
    ("❤️ Absolutely love this phone! 😍 Battery life is insane 🔋 and camera is stunning 📸", "Smartphone", "TechPro X12", 5.0),
    ("😡 This is terrible!! Battery dies so fast 💀 Complete waste of money 🗑️", "Smartphone", "TechPro X12", 1.0),
    ("😊 Great protein powder! 💪 Mixes perfectly and tastes amazing 😄 Buy it! 👍", "Protein Powder", "MuscleMax Pro", 5.0),
    ("🤮 Worst taste ever! Made me feel sick 🤢 Don't waste your money 👎 Zero stars!", "Protein Powder", "MuscleMax Pro", 1.0),
    ("🎉 These earphones are AMAZING 🎊 Sound quality is out of this world 🌟 100% recommend 💯", "Bluetooth Earphones", "SoundWave Elite", 5.0),
    ("😭 Packaging destroyed 😤 Earphones scratched on arrival ❌ Very disappointed 💔", "Bluetooth Earphones", "SoundWave Elite", 2.0),
    ("😎 Premium feel, premium sound 🔥 Worth every rupee! ⭐⭐⭐⭐⭐", "Bluetooth Earphones", "SoundWave Elite", 5.0),
    ("🤔 Mixed feelings honestly... good build 👍 but battery is meh 😑", "Smartphone", "TechPro X12", 3.0),
    ("🏆 Best earphones in the market! Unbelievable ANC 🙌 Crystal clear audio ✨", "Bluetooth Earphones", "SoundWave Elite", 5.0),
    ("😞 Expected more for this price. Performance is below average 😟 not recommending", "Protein Powder", "MuscleMax Pro", 2.0),
    ("Wow!! 🤩 Great camera! Great screen! Great battery! This phone has it all! 💯", "Smartphone", "TechPro X12", 5.0),
    ("Awful 😠 Broke after 2 weeks 💀 Customer service 🚫 was zero help", "Smartphone", "TechPro X12", 1.0),
]

# Bot-like reviews (to be detected)
BOT_REVIEWS = [
    {"review_text": "Good product good product good product", "category": "Smartphone", "product_name": "TechPro X12", "rating": 5.0},
    {"review_text": "Best product highly recommend", "category": "Protein Powder", "product_name": "MuscleMax Pro", "rating": 5.0},
    {"review_text": "Worst product do not buy waste of money", "category": "Bluetooth Earphones", "product_name": "SoundWave Elite", "rating": 1.0},
    {"review_text": "Good product good product", "category": "Smartphone", "product_name": "TechPro X12", "rating": 5.0},
    {"review_text": "Five stars five stars amazing product five stars", "category": "Protein Powder", "product_name": "MuscleMax Pro", "rating": 5.0},
    {"review_text": "love it love it love it love it", "category": "Bluetooth Earphones", "product_name": "SoundWave Elite", "rating": 5.0},
]

# Exact duplicates (to be detected)
DUPLICATE_REVIEWS = [
    {"review_text": "Battery drains super fast! Goes from 100% to 20% in just 4 hours of normal use. Very disappointed.", "category": "Smartphone", "product_name": "TechPro X12", "rating": 1.5},
    {"review_text": "Chocolate flavor tastes amazing! Mixes perfectly with both milk and water, no clumps at all.", "category": "Protein Powder", "product_name": "MuscleMax Pro", "rating": 5.0},
]


def generate_synthetic_dataset() -> List[Dict[str, Any]]:
    """Generate the full synthetic review dataset."""
    reviews = []
    base_date = datetime(2024, 1, 1)
    
    def make_review(text, category, product_name, rating, idx, days_offset=0):
        review_date = (base_date + timedelta(days=days_offset + idx // 3)).strftime("%Y-%m-%d")
        return {
            "id": str(uuid.uuid4())[:8],
            "review_text": text,
            "category": category,
            "product_name": product_name,
            "rating": rating,
            "review_date": review_date,
            "helpful_votes": random.randint(0, 50),
            "verified_purchase": random.choice([True, True, True, False]),
        }
    
    # Smartphones (70 reviews)
    for i, (text, rating, _) in enumerate(SMARTPHONE_REVIEWS * 3):
        # Add slight variation to avoid exact duplicates in the non-duplicate set
        if i > len(SMARTPHONE_REVIEWS):
            text = text + random.choice(["", " Overall decent product.", " Would consider again.", " Use with caution."])
        reviews.append(make_review(text, "Smartphone", "TechPro X12", rating, i, 0))
    
    # Protein Powder (60 reviews)
    for i, (text, rating, _) in enumerate(PROTEIN_POWDER_REVIEWS * 3):
        if i > len(PROTEIN_POWDER_REVIEWS):
            text = text + random.choice(["", " Good value.", " Mixed results.", ""])
        reviews.append(make_review(text, "Protein Powder", "MuscleMax Pro", rating, i, 100))
    
    # Earphones - early batch (25 reviews, normal)
    for i, (text, rating, _) in enumerate(EARPHONE_REVIEWS_EARLY):
        reviews.append(make_review(text, "Bluetooth Earphones", "SoundWave Elite", rating, i, 200))
    
    # Earphones - filler normal (10 reviews)
    for i, (text, rating, _) in enumerate(EARPHONE_REVIEWS_NORMAL_FILLER):
        reviews.append(make_review(text, "Bluetooth Earphones", "SoundWave Elite", rating, i, 220))
    
    # Earphones - SEEDED PACKAGING COMPLAINTS (25 reviews, last batch)
    for i, (text, rating, _) in enumerate(EARPHONE_REVIEWS_SEEDED_PACKAGING_ISSUES):
        reviews.append(make_review(text, "Bluetooth Earphones", "SoundWave Elite", rating, i, 230))
    
    # Add bot reviews
    for bot in BOT_REVIEWS:
        bot["id"] = str(uuid.uuid4())[:8]
        bot["review_date"] = "2024-06-01"
        bot["helpful_votes"] = 0
        bot["verified_purchase"] = False
        reviews.append(bot)
    
    # Add duplicates
    for dup in DUPLICATE_REVIEWS:
        dup["id"] = str(uuid.uuid4())[:8]
        dup["review_date"] = "2024-03-15"
        dup["helpful_votes"] = 1
        dup["verified_purchase"] = True
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
        cats[r["category"]] = cats.get(r["category"], 0) + 1
    print(f"Categories: {cats}")
    
    with open("synthetic_reviews.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print("Saved to synthetic_reviews.json")
