# Prompt History — AI Food Assistant
**Project:** AI Restaurant Finder — Thonglor, Bangkok
**Author:** Kate Chinnawat
**Date:** 29 May 2026
**Model Used:** Claude claude-sonnet-4-6

---

## STEP 1 — Problem Framing Prompt

**Prompt:**
> I need to find the best restaurant for a team dinner of 10 people in Thonglor, Bangkok.
> The team has mixed food preferences. Budget is around ฿300–500 per person.
> We need a place that is group-friendly, close to BTS Thonglor, and open for dinner (6–10pm).
> Help me define clear decision criteria I can use to objectively score restaurants.

**Claude Response:**
> Here are your structured decision criteria for scoring restaurants:
> 1. Rating & Review Quality (25%) — Google rating + review volume signals trust
> 2. Group Suitability (20%) — Physical space, reservation policy, group menu availability
> 3. Price Suitability (15%) — Per-person budget ≤ ฿500 preferred, ≤ ฿300 ideal
> 4. Travel Convenience (15%) — Walking distance from BTS Thonglor
> 5. Data Completeness (15%) — Quality of information available for decision
> 6. Uniqueness / Experience (10%) — Memorable factor for team morale
> Total: 100 points. These weights ensure group logistics and accessibility matter
> as much as food quality — crucial for team dinners.

---

## STEP 2 — Data Collection (Apify)

**Tool Used:** Apify Actor: apify/google-maps-scraper
**API Call:**
```json
{
  "searchString": "restaurants near Thonglor Bangkok",
  "maxCrawledPlaces": 20,
  "language": "en"
}
```
**Result:** 15 records exported from Google Maps
**Second Source:** Wongnai.com via Browse AI robot → 10 additional records
**Total:** 25 raw records saved to Google Sheets raw_data tab

---

## STEP 3 — Data Storage

**Action:** Used Google Sheets API v4 to write 25 records to raw_data tab
**Columns:** Restaurant Name, Area, Food Type, Google Rating, Review Count, Price Range,
Location, Distance/Travel Note, Opening Hours, Suitable for Group, Source URL, Notes

---

## STEP 4 — Data Cleaning Prompt

**Prompt:**
> I have 25 raw restaurant records from Google Maps and Wongnai scraping.
> Please normalize them to this schema:
> - foodType → enum: Thai, Japanese, Italian, Western, French, Mediterranean, Cafe, Healthy/Vegan, Mixed/Food Hall, Other
> - pricePerPersonTHB → extract numeric midpoint from strings like '฿฿ (200-400 THB/person)'
> - suitableForGroup → boolean true/false or 'partial' if mentioned conditionally
> - Flag records with more than 3 missing required fields
> - Merge any duplicate restaurants (same name, similar address)
>
> Return cleaned records as JSON array.

**Claude Response (Summary):**
> Processed 25 records:
> - 0 exact duplicates found and merged
> - Food types normalized to enum (e.g., "American / Burger" → "Western")
> - Prices parsed: "฿฿ (200–400 THB/person)" → 300 THB/person midpoint
> - Group suitability: 15 marked true, 6 partial, 3 unknown, 1 false
> - All records have ≥ 9/11 required fields — data quality high
> - Flagged: r22 (Factory Coffee) has suitableForGroup=false — recommend excluding from top candidates

---

## STEP 5 — Scoring Model Prompt

**Prompt:**
> Apply this 100-point scoring model to my 25 cleaned restaurant records.
> Weights are locked — do not modify them:
> - Rating & Review Quality: 25 pts — formula: min(25, (rating/5)*15 + min(10, reviewCount/100))
> - Group Suitability: 20 pts — true=20, partial=10, unknown=5, false=0
> - Price Suitability: 15 pts — ≤300 THB=15, 301-500=12, 501-800=8, >800=3
> - Travel Convenience: 15 pts — <500m BTS=15, 500-1000m=10, >1km=5, unknown=7
> - Data Completeness: 15 pts — nonNullFields/11 × 15
> - Uniqueness/Experience: 10 pts — assign 1-10 based on review text keywords (unique, must-visit, best-in-class, special)
>
> Return JSON array sorted by totalScore descending.

**Claude Response (Summary):**
> Scored all 25 restaurants. Top 5 results:
> 1. The Commons Thonglor — 97.8 pts (flexibility + accessibility + value)
> 2. Ekkamai 63 Street Food — 93.6 pts (ultra-budget, high group fit, BTS proximity)
> 3. The Never Ending Summer — 90.1 pts (best rating in top 3, heritage venue)
> 4. Meatlicious BBQ — 89.4 pts (communal BBQ, close to BTS)
> 5. Grease Restaurant & Bar — 89.3 pts (large capacity, American comfort food)
> Fine dining options (Bo.lan, Sühring) scored 60-67 due to price penalty.

---

## STEP 6 — AI Analysis Prompt

**Prompt:**
> Analyze the Top 10 scored restaurants for a team of 10 having dinner in Thonglor.
> For the Top 3, provide:
> 1. A 3-4 sentence recommendation explaining why it's the right choice
> 2. Why it ranks where it does (key differentiators)
> 3. 3-4 specific trade-offs (honest weaknesses, not just positives)
> 4. Who this restaurant is "Best For" (1 sentence)
> Also write a 2-3 sentence overall insight summary about patterns in the data.
> Return as structured JSON.

**Claude Response:** See phase4_analysis.json for full structured output.

---

## STEP 7 — Automation (n8n)

**Workflow Built:** Google Sheets Watch → Claude Haiku (uniqueness score) → Compute Total → Write to Scoring Tab
**Nodes:** 5 (Trigger + Code + HTTP + Code + Sheets Write)
**Test:** Added 1 row to clean_data manually → workflow ran in 8 seconds → score written to scoring tab
**Workflow JSON:** See phase5_n8n_workflow.json

---

## STEP 8 — HTML Generation Prompt

**Prompt:**
> Build a complete single-file HTML report with these 9 sections (use these exact IDs):
> #header, #objective, #workflow, #tools, #sources, #scoring-criteria, #top10, #top3, #comparison
> Embed the restaurant JSON data directly in a <script> block.
> Include: sticky navigation, sortable Top 10 table, Top 3 recommendation cards,
> side-by-side comparison, overall insight box.
> Make it responsive (desktop + mobile). No external CDN dependencies.

**Claude Response:** Generated complete index.html — 51KB, all 9 section IDs verified present.

