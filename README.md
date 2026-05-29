# 🍜 AI Food Assistant — Thonglor Bangkok

**AI Workflow: Restaurant Finder for Team Dinners**
Built for the AI Workflow Exam — 29 May 2026
Author: Kate Chinnawat · kate8chinnawat@gmail.com

---

## 🌐 Live Demo

**[https://glittering-granita-4b9e17.netlify.app/](https://glittering-granita-4b9e17.netlify.app/)**

---

## 🗺️ Project Overview

An end-to-end AI pipeline that finds the best restaurants for a team of 10 in **Thonglor, Bangkok**. The workflow collects real restaurant data via web scraping, normalizes and cleans it with AI, scores every restaurant against a 100-point weighted model, automates scoring via n8n, and renders everything as a single deployable HTML report.

### Top 3 Results

| Rank | Restaurant | Score |
|------|-----------|-------|
| 🥇 1 | The Commons Thonglor | 97.8 |
| 🥈 2 | Ekkamai 63 Street Food | 93.6 |
| 🥉 3 | The Never Ending Summer | 90.1 |

---

## 📁 File Structure

```
ai-food-assistant/
├── index.html                # Final HTML report (THE deliverable)
├── setup_sheets.py           # Bonus: auto-creates Google Sheets with all data
├── phase2_cleaner.py         # Data cleaning & normalization script
├── phase3_scorer.py          # 100-point weighted scoring model
├── phase4_analysis.py        # AI analysis output generator
├── phase1_raw_data.json      # Raw scraped restaurant data (25 records)
├── phase2_clean_data.json    # Cleaned & normalized data
├── phase3_scored_data.json   # Scored & ranked data
├── phase4_analysis.json      # AI recommendations & trade-offs
├── phase5_n8n_workflow.json  # n8n automation workflow (importable)
├── prompt_history.md         # Full AI prompt history (all steps)
├── submission.json           # Submission checklist & deliverable links
├── vercel.json               # One-click Vercel deployment config
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## ⚙️ How to Run the Full Pipeline

### Prerequisites

```bash
pip install -r requirements.txt
```

Set environment variables:
```bash
export APIFY_API_TOKEN=your_apify_token
export ANTHROPIC_API_KEY=your_claude_api_key
export GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/service_account.json
```

### Step-by-step

```bash
# Step 1: Data is already in phase1_raw_data.json (from Apify + Wongnai)
# To re-scrape: trigger Apify actor 'apify/google-maps-scraper' via API

# Step 2: Clean the data
python3 phase2_cleaner.py

# Step 3: Score all restaurants
python3 phase3_scorer.py

# Step 4: Generate AI analysis
python3 phase4_analysis.py

# Step 5: Set up Google Sheets (Bonus)
python3 setup_sheets.py

# Step 6: Open index.html in browser — all data is embedded
open index.html
```

---

## 🤖 Automation (n8n)

Import `phase5_n8n_workflow.json` into n8n:

1. Go to n8n → Workflows → **Import from File**
2. Select `phase5_n8n_workflow.json`
3. Replace `{{GOOGLE_SPREADSHEET_ID}}` with your Sheet ID
4. Set up credentials:
   - Google Sheets OAuth2 (n8n built-in)
   - HTTP Header Auth: `x-api-key: your_anthropic_api_key`
5. **Activate** the workflow

**What it does:** Watches `clean_data` sheet for new rows → calls Claude Haiku for uniqueness score → computes total → writes scoring breakdown back to `scoring` tab automatically.

---

## 📊 Scoring Model (100 pts — Locked Weights)

| Category | Weight | Formula |
|----------|--------|---------|
| Rating & Review Quality | 25 | min(25, rating/5×15 + min(10, reviews/100)) |
| Group Suitability | 20 | true=20, partial=10, unknown=5, false=0 |
| Price Suitability | 15 | ≤300 THB=15, 301–500=12, 501–800=8, >800=3 |
| Travel Convenience | 15 | <500m BTS=15, 500m–1km=10, >1km=5, unknown=7 |
| Data Completeness | 15 | nonNullFields / 11 × 15 |
| Uniqueness / Experience | 10 | AI-assigned 1–10 (Claude sentiment) |

---

## 🚀 Deploy

### Netlify (already live)
Deployed at: https://glittering-granita-4b9e17.netlify.app/

### Vercel (one-click)
```bash
npm install -g vercel
vercel --prod
```
(uses `vercel.json` in this repo)

### GitHub Pages
```bash
git init && git add . && git commit -m "AI Food Assistant"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-food-assistant.git
git push -u origin main
# Enable Pages: Settings → Pages → Branch: main → /root
```

---

## 🛠️ Tech Stack

| Layer | Tool |
|-------|------|
| Web Scraping | Apify (google-maps-scraper actor) |
| Secondary Data | Wongnai via Browse AI |
| Data Storage | Google Sheets API v4 |
| AI / LLM | Claude claude-sonnet-4-6 (Anthropic) |
| Automation | n8n (5-node workflow) |
| Frontend | HTML5 + CSS3 + Vanilla JS (single file) |
| Deployment | Netlify (live) / Vercel / GitHub Pages |

---

## 📋 Deliverables

| # | Item | Status |
|---|------|--------|
| 1 | HTML Page | ✅ [Live](https://glittering-granita-4b9e17.netlify.app/) |
| 2 | Google Sheets | ✅ (run setup_sheets.py) |
| 3 | Scraping Evidence | ✅ phase1_raw_data.json |
| 4 | Prompt History | ✅ prompt_history.md |
| 5 | Automation Evidence | ✅ phase5_n8n_workflow.json |
| 6 | Top 3 Recommendation | ✅ submission.json |
| 7 | Reflection | ✅ submission.json |
| 8 | Code Repo (Bonus) | ✅ This repository |

---

## 📝 Reflection

Building this AI workflow taught me that data quality gates matter more than expected. The biggest challenge was normalizing price strings — `฿฿` vs `200–400 THB/person` vs just `฿` — requiring a robust parser before scoring was meaningful. The locked scoring weights forced disciplined thinking: I couldn't adjust weights to favour a restaurant I personally preferred, which surfaced The Commons as the clear #1 despite not being the 'fanciest' option. The n8n automation was simpler than expected once the API structure was understood. Future improvement: add a second AI pass to cross-validate uniqueness scores against multiple review sources, and auto-rebuild HTML whenever new data arrives.

---

*Submission deadline: 8 June 2026 · Area: Thonglor · Team size: 10*
