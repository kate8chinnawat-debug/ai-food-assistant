"""
Phase 3 — 6-Category Weighted Scoring Model (100 pts)
Weights are LOCKED — do not modify.
"""
import json

WEIGHTS = {
    "ratingReview": 25,
    "groupSuitability": 20,
    "priceSuitability": 15,
    "travelConvenience": 15,
    "dataCompleteness": 15,
    "uniqueness": 10,
}
assert sum(WEIGHTS.values()) == 100, "Weight sum must be 100!"

UNIQUENESS_SCORES = {
    # AI-assigned 1-10 based on review sentiment keywords: unique, special, must-visit, best-in-class
    "r01": 9,  # The Commons - iconic Bangkok destination
    "r02": 9,  # The Never Ending Summer - heritage building, river views
    "r03": 7,  # Soul Food - local institution
    "r04": 6,  # Roast - good but not unique
    "r05": 8,  # Broccoli Revolution - unique healthy concept in Thonglor
    "r06": 5,  # Grease - standard American
    "r07": 5,  # Kuppa - reliable but not special
    "r08": 8,  # Cocotte - French rotisserie, memorable
    "r09": 4,  # Little Monster - good burger, not unique
    "r10": 8,  # Appia - authentic Roman, hard to find in BKK
    "r11": 7,  # Quince - solid Mediterranean
    "r12": 10, # Akira Back - celebrity chef, world-class
    "r13": 10, # Bo.lan - Michelin, iconic
    "r14": 10, # Sühring - World's 50 Best
    "r15": 6,  # Kaizen - mall Japanese
    "r16": 7,  # Rabbit Hole - speakeasy vibe
    "r17": 7,  # Trattoria da Antonio - authentic Italian
    "r18": 6,  # Meatlicious - fun BBQ
    "r19": 7,  # Mia Dining - modern concept
    "r20": 7,  # Teens of Thailand - unique gin cocktails
    "r21": 4,  # Mr. Jones - dessert cafe, not for dinner
    "r22": 3,  # Factory Coffee - just coffee
    "r23": 6,  # Ekkamai 63 - authentic street food
    "r24": 8,  # Kikusui - traditional kaiseki
    "r25": 9,  # Paste - Michelin Thai
}

def score_rating_review(rating, review_count):
    """Max 25: (rating/5)*15 + min(10, reviewCount/100)"""
    if rating is None: return 0
    r_score = (rating / 5.0) * 15
    rv_score = min(10, (review_count or 0) / 100)
    return round(min(25, r_score + rv_score), 2)

def score_group(group):
    """Max 20"""
    if group is True:        return 20
    if group == "partial":   return 10
    if group == "unknown":   return 5
    return 0  # False

def score_price(price_thb):
    """Max 15 — per person THB"""
    if price_thb is None: return 0
    if price_thb <= 300:  return 15
    if price_thb <= 500:  return 12
    if price_thb <= 800:  return 8
    return 3  # > 800

def score_travel(bts_dist_m):
    """Max 15 — meters to nearest BTS/MRT"""
    if bts_dist_m is None:  return 7   # unknown
    if bts_dist_m <= 500:   return 15
    if bts_dist_m <= 1000:  return 10
    return 5

def score_completeness(missing_count, total=11):
    """Max 15"""
    filled = total - missing_count
    return round((filled / total) * 15, 2)

def score_uniqueness(restaurant_id):
    """Max 10 — AI-assigned"""
    return UNIQUENESS_SCORES.get(restaurant_id, 5)

with open('/sessions/serene-sleepy-brahmagupta/mnt/TEST3 RESTAURANT/ai-food-assistant/phase2_clean_data.json') as f:
    clean = json.load(f)

scored = []
for r in clean['restaurants']:
    s_rating    = score_rating_review(r['googleRating'], r['reviewCount'])
    s_group     = score_group(r['suitableForGroup'])
    s_price     = score_price(r['pricePerPersonTHB'])
    s_travel    = score_travel(r['btsMrtDistanceM'])
    s_complete  = score_completeness(r['missingFieldCount'])
    s_unique    = score_uniqueness(r['id'])
    total       = round(s_rating + s_group + s_price + s_travel + s_complete + s_unique, 2)

    scored.append({**r,
        "scoreRatingReview":   s_rating,
        "scoreGroupSuit":      s_group,
        "scorePriceSuit":      s_price,
        "scoreTravelConv":     s_travel,
        "scoreCompleteness":   s_complete,
        "scoreUniqueness":     s_unique,
        "totalScore":          total,
        "rank": None  # assigned after sort
    })

scored.sort(key=lambda x: x['totalScore'], reverse=True)
for i, r in enumerate(scored):
    r['rank'] = i + 1

output = {
    "meta": {
        "scoredAt": "2026-05-29T11:00:00+07:00",
        "weights": WEIGHTS,
        "weightSum": sum(WEIGHTS.values()),
        "recordCount": len(scored),
    },
    "restaurants": scored
}

with open('/sessions/serene-sleepy-brahmagupta/mnt/TEST3 RESTAURANT/ai-food-assistant/phase3_scored_data.json','w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Scoring complete. Weight sum:", sum(WEIGHTS.values()))
print("\nTop 10:")
for r in scored[:10]:
    print(f"  #{r['rank']:2} {r['restaurantName']:<35} | Total: {r['totalScore']:5.1f} "
          f"| Rating:{r['scoreRatingReview']:4.1f} Group:{r['scoreGroupSuit']:2} "
          f"Price:{r['scorePriceSuit']:2} Travel:{r['scoreTravelConv']:2} "
          f"Complete:{r['scoreCompleteness']:4.1f} Unique:{r['scoreUniqueness']}")
