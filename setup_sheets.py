"""
Bonus B — Google Sheets Auto-Setup Script
=========================================
One-command script that:
  1. Creates a new Google Sheets workbook named "AI Food Assistant — Thonglor"
  2. Creates 5 tabs: config, raw_data, clean_data, scoring, analysis
  3. Writes correct column headers to each tab
  4. Bulk-writes raw_data, clean_data, and scoring from local JSON files
  5. Prints the public share URL

Usage:
  pip install google-auth google-auth-oauthlib google-api-python-client
  export GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/service_account.json
  python3 setup_sheets.py
"""

import json, os, sys

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("❌ Missing dependencies. Run: pip install google-auth google-api-python-client")
    sys.exit(1)

BASE = os.path.dirname(os.path.abspath(__file__))
KEY_FILE = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY', 'service_account.json')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# ── Auth ───────────────────────────────────────────────────
creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
sheets_svc = build('sheets', 'v4', credentials=creds)
drive_svc  = build('drive',  'v3', credentials=creds)

# ── Create workbook ────────────────────────────────────────
print("Creating Google Sheets workbook...")
wb = sheets_svc.spreadsheets().create(body={
    'properties': {'title': 'AI Food Assistant — Thonglor'},
    'sheets': [
        {'properties': {'title': 'config'}},
        {'properties': {'title': 'raw_data'}},
        {'properties': {'title': 'clean_data'}},
        {'properties': {'title': 'scoring'}},
        {'properties': {'title': 'analysis'}},
    ]
}).execute()

SPREADSHEET_ID = wb['spreadsheetId']
print(f"✅ Created: {SPREADSHEET_ID}")

# ── Share publicly (view-only) ─────────────────────────────
drive_svc.permissions().create(
    fileId=SPREADSHEET_ID,
    body={'type': 'anyone', 'role': 'reader'},
    fields='id'
).execute()
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit?usp=sharing"
print(f"✅ Shared (view-only): {SHEET_URL}")

def write(tab, values):
    sheets_svc.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{tab}!A1",
        valueInputOption='RAW',
        body={'values': values}
    ).execute()

# ── config tab ─────────────────────────────────────────────
write('config', [
    ['Key', 'Value'],
    ['area', 'Thonglor'],
    ['teamSize', 10],
    ['minRestaurants', 20],
    ['minSources', 2],
    ['weightSum', 100],
    ['deadline', '2026-06-08T23:59:59+07:00'],
    ['htmlUrl', 'https://glittering-granita-4b9e17.netlify.app/'],
    ['scoredAt', '2026-05-29T11:00:00+07:00'],
])
print("✅ config tab written")

# ── raw_data tab ───────────────────────────────────────────
RAW_HEADERS = ['id','source','restaurantName','area','foodType','googleRating',
               'reviewCount','priceRange','location','distanceTravelNote',
               'openingHours','suitableForGroup','sourceUrl','notes']
raw_data = json.load(open(f'{BASE}/phase1_raw_data.json'))
rows = [RAW_HEADERS]
for r in raw_data['restaurants']:
    rows.append([str(r.get(h,'')) for h in RAW_HEADERS])
write('raw_data', rows)
print(f"✅ raw_data tab: {len(rows)-1} rows")

# ── clean_data tab ─────────────────────────────────────────
CLEAN_HEADERS = ['id','source','restaurantName','area','foodType','googleRating',
                 'reviewCount','priceRangeRaw','pricePerPersonTHB','priceCategory',
                 'location','distanceTravelNote','btsMrtDistanceM','openingHours',
                 'suitableForGroup','sourceUrl','notes','missingFieldCount','dataQualityScore']
clean_data = json.load(open(f'{BASE}/phase2_clean_data.json'))
rows = [CLEAN_HEADERS]
for r in clean_data['restaurants']:
    rows.append([str(r.get(h,'')) for h in CLEAN_HEADERS])
write('clean_data', rows)
print(f"✅ clean_data tab: {len(rows)-1} rows")

# ── scoring tab ────────────────────────────────────────────
SCORE_HEADERS = ['rank','restaurantName','area','foodType','totalScore',
                 'scoreRatingReview','scoreGroupSuit','scorePriceSuit',
                 'scoreTravelConv','scoreCompleteness','scoreUniqueness',
                 'googleRating','reviewCount','pricePerPersonTHB','btsMrtDistanceM','sourceUrl']
scored_data = json.load(open(f'{BASE}/phase3_scored_data.json'))
rows = [SCORE_HEADERS]
for r in scored_data['restaurants']:
    rows.append([str(r.get(h,'')) for h in SCORE_HEADERS])
write('scoring', rows)
print(f"✅ scoring tab: {len(rows)-1} rows")

# ── analysis tab ───────────────────────────────────────────
analysis = json.load(open(f'{BASE}/phase4_analysis.json'))
analysis_rows = [
    ['Section', 'Content'],
    ['Analyzed At', analysis['meta']['analyzedAt']],
    ['Model', analysis['meta']['model']],
    ['Insight Summary', analysis['insightSummary']],
    ['', ''],
    ['Rank', 'Restaurant Name', 'Score', 'Recommendation', 'Trade-offs', 'Best For'],
]
for c in analysis['top3Cards']:
    analysis_rows.append([
        c['rank'], c['name'], c['totalScore'],
        c['recommendation'],
        ' | '.join(c['tradeoffs']),
        c['bestFor']
    ])
write('analysis', analysis_rows)
print("✅ analysis tab written")

print(f"\n{'='*60}")
print(f"🎉 All tabs populated!")
print(f"📊 Sheet URL: {SHEET_URL}")
print(f"\nAdd this to submission.json > 2_sheetsUrl:")
print(f'  "{SHEET_URL}"')
print(f"\nAdd SPREADSHEET_ID to n8n workflow:")
print(f'  {SPREADSHEET_ID}')
