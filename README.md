# SchemeSathi — Government Scheme Eligibility & Recommendation Assistant

A small Flask academic prototype that recommends potentially relevant Indian government schemes from a user profile.

## Files
- `app.py` — Flask application, rule-based eligibility filtering, TF-IDF ranking, and embedded HTML/CSS.
- `schemes.csv` — sample scheme dataset loaded using Pandas.
- `requirements.txt` — Python dependencies.
- `schema.sql` — starter MySQL table for future database integration.

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Demo profile
- Age: 22
- Annual income: 180000
- Occupation: farmer
- State: Uttar Pradesh
- Category: General
- Gender: Male
- Need: farmer income support

## GitHub browser upload
Create a repository, choose **Add file → Upload files**, open this folder, select all four/five files (including `app.py`, `schemes.csv`, `requirements.txt`, `README.md`, `schema.sql`, `.gitignore` if present), and upload them together. They are all in this one folder; there are no nested folders.

## MySQL status
`schema.sql` is a starter schema only. The running MVP reads `schemes.csv` directly and does not yet connect to MySQL.

## Important disclaimer
This is an academic prototype, not an official eligibility checker. Scheme rules and income limits in the CSV are simplified demo filters; some are illustrative, not official criteria. Actual eligibility may depend on household status, documents, land ownership, trade, education, exclusions, state rules and current notifications. Verify details with the relevant government department or official portal before applying.
