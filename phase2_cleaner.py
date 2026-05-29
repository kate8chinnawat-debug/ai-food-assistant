"""
Phase 2 — Data Cleaning & Normalization
AI Prompt used: 'Normalize the following restaurant records to a clean schema.
Merge duplicates, standardize food type to enum, convert price to THB per person numeric,
flag null/missing fields, and mark suitableForGroup as boolean or unknown.'
"""
import json, re

FOOD_TYPE_MAP = {
    "mixed / food hall": "Mixed/Food Hall",
    "thai contemporary": "Thai",
    "thai": "Thai",
    "thai fine dining": "Thai Fine Dining",
    "thai / bar": "Thai",
    "thai street food": "Thai Street Food",
    "cafe / western": "Cafe",
    "cafe": "Cafe",
    "western / international": "Western",
    "western / dessert": "Western",
    "american / burger": "Western",
    "burger / western": "Western",
    "bbq / western": "Western",
    "bar / western": "Western",
    "healthy / vegetarian": "Healthy/Vegan",
    "french / european": "French",
    "german fine dining": "German Fine Dining",
    "italian": "Italian",
    "japanese fusion": "Japanese Fusion",
    "japanese": "Japanese",
    "mediterranean": "Mediterranean",
}

def normalize_food_type(raw):
    return FOOD_TYPE_MAP.get(raw.lower().strip(), "Other")

def normalize_price(raw_price_str):
    """Return estimated THB per person as integer"""
    s = raw_price_str.lower()
    # extract numbers from string like '200–400 THB/person'
    nums = re.findall(r'\d+', s)
    if nums:
        vals = [int(n) for n in nums if int(n) > 50]
        if vals:
            return round(sum(vals) / len(vals))
    # baht symbols
    if '฿฿฿฿฿' in raw_price_str: return 3500
    if '฿฿฿฿'  in raw_price_str: return 1200
    if '฿฿฿'   in raw_price_str: return 550
    if '฿฿'    in raw_price_str: return 320
    if '฿'     in raw_price_str: return 180
    return None

def normalize_group(raw):
    if raw is True or raw == "true": return True
    if raw is False or raw == "false": return False
    if isinstance(raw, str) and raw.lower() == "partial": return "partial"
    return "unknown"

def parse_bts_distance(note):
    """Return estimated meters to nearest BTS/MRT"""
    note_lower = note.lower()
    nums = re.findall(r'(\d+)\s*m\b', note_lower)
    if nums:
        return int(nums[0])
    if 'km' in note_lower:
        km_nums = re.findall(r'([\d.]+)\s*km', note_lower)
        if km_nums: return int(float(km_nums[0]) * 1000)
    if 'taxi' in note_lower or 'grab' in note_lower:
        return 2000  # assume far
    return None

REQUIRED_FIELDS = ["restaurantName","area","foodType","googleRating","reviewCount",
                   "pricePerPersonTHB","location","distanceTravelNote","openingHours",
                   "suitableForGroup","sourceUrl"]

with open('/sessions/serene-sleepy-brahmagupta/mnt/TEST3 RESTAURANT/ai-food-assistant/phase1_raw_data.json') as f:
    raw = json.load(f)

seen_names = {}
clean = []
duplicates_removed = 0

for r in raw['restaurants']:
    key = re.sub(r'\s+','', r['restaurantName'].lower())
    if key in seen_names:
        duplicates_removed += 1
        continue
    seen_names[key] = True

    price_normalized = normalize_price(r.get('priceRange',''))
    group_normalized = normalize_group(r.get('suitableForGroup'))
    food_normalized  = normalize_food_type(r.get('foodType',''))
    bts_dist         = parse_bts_distance(r.get('distanceTravelNote',''))

    record = {
        "id":               r['id'],
        "source":           r['source'],
        "restaurantName":   r['restaurantName'],
        "area":             r['area'],
        "foodType":         food_normalized,
        "googleRating":     r.get('googleRating'),
        "reviewCount":      r.get('reviewCount'),
        "priceRangeRaw":    r.get('priceRange'),
        "pricePerPersonTHB": price_normalized,
        "priceCategory":    "Low" if price_normalized and price_normalized<=300 else ("Mid" if price_normalized and price_normalized<=800 else "High"),
        "location":         r.get('location'),
        "distanceTravelNote": r.get('distanceTravelNote'),
        "btsMrtDistanceM":  bts_dist,
        "openingHours":     r.get('openingHours'),
        "suitableForGroup": group_normalized,
        "sourceUrl":        r.get('sourceUrl'),
        "notes":            r.get('notes',''),
    }

    # data quality
    null_count = sum(1 for f in REQUIRED_FIELDS if record.get(f) is None)
    record['missingFieldCount'] = null_count
    record['dataQualityScore']  = round((len(REQUIRED_FIELDS) - null_count) / len(REQUIRED_FIELDS) * 100, 1)
    record['duplicateFlag']     = False

    clean.append(record)

output = {
    "meta": {
        "cleanedAt": "2026-05-29T10:00:00+07:00",
        "rawRecords": len(raw['restaurants']),
        "cleanRecords": len(clean),
        "duplicatesRemoved": duplicates_removed,
        "aiPromptUsed": "Claude claude-sonnet-4-6: Normalize restaurant records — deduplicate, standardize food types, parse prices to THB numeric, detect missing fields, normalize group suitability to boolean/partial/unknown.",
    },
    "restaurants": clean
}

with open('/sessions/serene-sleepy-brahmagupta/mnt/TEST3 RESTAURANT/ai-food-assistant/phase2_clean_data.json','w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Clean records: {len(clean)} (removed {duplicates_removed} duplicates)")
for r in clean[:3]:
    print(f"  {r['restaurantName']} | {r['foodType']} | {r['pricePerPersonTHB']} THB | group={r['suitableForGroup']} | missing={r['missingFieldCount']}")
