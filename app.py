"""
SCHEMESATHI — Government Scheme Eligibility & Recommendation Assistant
======================================================================

ONE-FILE VERSION: Upload only this app.py file to GitHub.

ABOUT
-----
A Flask web application that accepts a citizen profile and recommends
potentially relevant Indian government schemes.

TECHNOLOGIES
------------
Python, Flask, Pandas, Scikit-learn (TF-IDF), rule-based filtering,
HTML/CSS (embedded in this file), and a MySQL starter schema (below).

INSTALL
-------
pip install flask pandas scikit-learn

RUN
---
python app.py

Open http://127.0.0.1:5000

GITHUB
------
Create a public repository and upload this single app.py file.

IMPORTANT
---------
This is an academic prototype. The eligibility filters and income limits
are simplified demo rules, not official government eligibility criteria.
Always verify current eligibility, benefits, documents and application
conditions on the official government portal. The app does not store
submitted profile details in a database.

MYSQL STARTER SCHEMA (future integration)
-----------------------------------------
CREATE DATABASE scheme_sathi;
USE scheme_sathi;
CREATE TABLE schemes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  min_age INT,
  max_age INT,
  max_income BIGINT,
  occupation VARCHAR(100),
  benefit TEXT,
  official_url VARCHAR(500)
);

The current one-file version uses an in-memory Pandas dataset so it can
run immediately without MySQL configuration.
"""

from flask import Flask, request, render_template_string
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load scheme records from the CSV file in this same folder.
# Demo filters are simplified and are NOT official eligibility rules.
schemes_df = pd.read_csv(Path(__file__).with_name("schemes.csv")).fillna("")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
:root{--bg:#0b1020;--panel:#121a2d;--line:#26334d;--text:#eef3ff;--muted:#a5b1c9;--lime:#c5f36b;--cyan:#70d6d1}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 80% 0%,#1b3150 0,transparent 36%),var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;min-height:100vh}
.wrap{max-width:900px;margin:auto;padding:28px 22px 50px}header{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:20px}
.brand{font:800 19px Manrope;letter-spacing:2px}.brand span{color:var(--lime)}.tag,.eyebrow{font-size:10px;letter-spacing:2px;color:var(--cyan);font-weight:700}
.hero{padding:54px 0 28px}.hero h1{font:800 clamp(38px,7vw,64px)/1.08 Manrope;margin:14px 0}.hero h1 em{color:var(--lime);font-style:normal}
.sub{color:var(--muted);max-width:570px;line-height:1.7}.panel,.scheme{background:linear-gradient(145deg,#151f34,#10182a);border:1px solid var(--line);border-radius:18px;padding:26px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}label{display:flex;flex-direction:column;gap:8px;color:#dce5f7;font-size:13px;font-weight:600}
.wide{grid-column:1/-1}input,select{width:100%;padding:13px 14px;border-radius:9px;border:1px solid #34425c;background:#0b1324;color:white;font:14px 'DM Sans';outline:none}
input:focus,select:focus{border-color:var(--cyan)}button{margin-top:24px;width:100%;padding:15px;border:0;border-radius:10px;background:var(--lime);color:#101827;font:700 15px Manrope;cursor:pointer}
.fine,footer{color:#8492ad;font-size:11px;line-height:1.6}.fine{margin-bottom:0}footer{text-align:center;margin-top:35px}.error{background:#522c35;color:#ffdce1;padding:12px;border-radius:9px}
.back,.source{color:var(--lime);text-decoration:none;font-weight:700;font-size:13px}.compact{padding:38px 0 18px}.profile{padding:14px 18px;border:1px solid var(--line);border-radius:10px;color:var(--muted);font-size:13px}
.profile b{color:white}.count{color:var(--cyan);font-weight:700;font-size:13px;margin:26px 0 12px}.scheme{margin:14px 0}.scheme-top{display:flex;justify-content:space-between;align-items:center}
.score{font-size:11px;color:var(--lime)}h2{font:700 22px Manrope;margin:12px 0}.scheme p,.scheme li{color:#b6c2d7;line-height:1.6;font-size:13px}
.benefit{background:#1b2b38;border-left:3px solid var(--lime);padding:13px 15px;margin:16px 0;color:#dce9df;font-size:13px;line-height:1.6}
.smallhead{font-size:12px}.scheme ul{padding-left:20px}.warning{color:#ffd28a!important;background:#3c3020;padding:10px;border-radius:8px}
.apply{border-top:1px solid var(--line);padding-top:12px}.notice{margin-top:22px;padding:16px;border:1px solid #62512e;background:#2b261c;border-radius:12px;color:#dfd2b3;font-size:12px;line-height:1.7}
@media(max-width:600px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}.wrap{padding:20px 15px}.tag{font-size:8px}.panel,.scheme{padding:19px}}
"""

BASE = """
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SchemeSathi | Government Scheme Assistant</title><style>{{ css|safe }}</style></head><body><main class="wrap">
<header><div class="brand">SCHEME<span>SATHI</span></div><span class="tag">GOVERNMENT SCHEME DISCOVERY</span></header>
{{ body|safe }}
<footer>SchemeSathi · Academic prototype · Verify every scheme with its official authority.</footer>
</main></body></html>
"""

FORM = """
<section class="hero"><p class="eyebrow">SMART • SIMPLE • ACCESSIBLE</p><h1>Find schemes that<br><em>fit your profile.</em></h1>
<p class="sub">Enter a few details to discover potentially relevant Indian government schemes and benefits.</p></section>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST" class="panel"><div class="grid">
<label>Full name<input name="name" placeholder="Your name"></label>
<label>Age<input type="number" name="age" min="1" max="120" required placeholder="e.g. 22"></label>
<label>Annual family income (₹)<input type="number" name="income" min="0" required placeholder="e.g. 250000"></label>
<label>Occupation<select name="occupation" required><option value="">Select occupation</option><option>student</option><option>farmer</option><option>artisan</option><option>street vendor</option><option>self-employed</option><option>salaried</option><option>unemployed</option></select></label>
<label>State / UT<input name="state" required placeholder="e.g. Uttar Pradesh"></label>
<label>Category<select name="category"><option value="general">General</option><option value="obc">OBC</option><option value="sc">SC</option><option value="st">ST</option><option value="ews">EWS</option><option value="other">Other</option></select></label>
<label>Gender<select name="gender"><option value="male">Male</option><option value="female">Female</option><option value="other">Other / Prefer not to say</option></select></label>
<label class="wide">What support are you looking for?<input name="need" placeholder="e.g. education scholarship, business loan, pension"></label>
</div><button type="submit">Find eligible schemes →</button>
<p class="fine">Your details are used only for this demo recommendation and are not stored.</p></form>
"""

RESULTS = """
<section class="hero compact"><p class="eyebrow">YOUR RESULTS</p><h1>Hi {{ user.name }},<br><em>here's your shortlist.</em></h1>
<p class="sub">Based on your details. These are potential matches, not official eligibility decisions.</p></section>
<div class="profile">Age <b>{{ user.age }}</b> · Income <b>₹{{ "{:,}".format(user.income) }}</b> · {{ user.occupation|title }} · {{ user.state }}</div>
{% if results %}<p class="count">{{ results|length }} potential match(es) found</p>
{% for s in results %}<article class="scheme"><div class="scheme-top"><span class="eyebrow">POTENTIAL MATCH</span><span class="score">Relevance {{ (s.score*100)|round|int }}%</span></div>
<h2>{{ s.name }}</h2><p>{{ s.description }}</p><div class="benefit"><b>Potential benefit</b><br>{{ s.benefit }}</div>
<b class="smallhead">Why it appeared</b><ul>{% for reason in s.reasons %}<li>{{ reason }}</li>{% endfor %}</ul>
{% if s.warning %}<p class="warning">{{ s.warning }}</p>{% endif %}
<p class="apply"><b>Next step:</b> {{ s.how }}</p><a class="source" href="{{ s.url }}" target="_blank" rel="noopener">Official scheme website ↗</a></article>{% endfor %}
{% else %}<div class="panel"><h2>No matches found</h2><p>Try reviewing your profile or selecting another occupation. This demo contains a limited set of schemes.</p><a class="source" href="/">Try again</a></div>{% endif %}
<div class="notice"><b>Important disclaimer</b><br>This is an academic prototype. Rules and income limits are simplified demo filters, not official criteria. Final eligibility, documents and benefits must be confirmed on the linked government portal or with the relevant department.</div>
<a class="back" href="/">← Check another profile</a>
"""

def find_recommendations(user):
    found = []
    for _, s in schemes_df.iterrows():
        age = user["age"]
        if not (int(s["min_age"]) <= age <= int(s["max_age"])):
            continue
        if user["income"] > int(s["max_income"]):
            continue
        occupations = [x.strip() for x in s["occupations"].lower().split(";")]
        categories = [x.strip() for x in s["categories"].lower().split(";")]
        genders = [x.strip() for x in s["genders"].lower().split(";")]
        if "any" not in occupations and user["occupation"] not in occupations:
            continue
        if "any" not in categories and user["category"] not in categories:
            continue
        if "any" not in genders and user["gender"] not in genders:
            continue

        reasons = ["Age and annual income match this prototype's demo filters."]
        if "any" not in occupations:
            reasons.append("Your occupation matches the scheme's demo target group.")
        if "any" not in categories:
            reasons.append("Your category matches the scheme's demo filter.")
        if "any" not in genders:
            reasons.append("Your gender matches the scheme's demo filter.")
        found.append({
            "name": s["name"], "description": s["description"],
            "benefit": s["benefit"], "how": s["how"], "url": s["url"],
            "reasons": reasons, "text": s["description"] + " " + s["benefit"],
            "warning": ""
        })

    need = user["need"].strip()
    if found and need:
        corpus = [need] + [x["text"] for x in found]
        matrix = TfidfVectorizer(stop_words="english").fit_transform(corpus)
        scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        for item, score in zip(found, scores):
            item["score"] = float(score)
        found.sort(key=lambda x: x["score"], reverse=True)
    else:
        for item in found:
            item["score"] = 0.0
    return found

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            user = {
                "name": request.form.get("name", "").strip() or "User",
                "age": int(request.form["age"]),
                "income": int(request.form["income"]),
                "occupation": request.form["occupation"].strip().lower(),
                "state": request.form["state"].strip(),
                "category": request.form.get("category", "general").lower(),
                "gender": request.form.get("gender", "other").lower(),
                "need": request.form.get("need", "")
            }
            if not 1 <= user["age"] <= 120 or user["income"] < 0:
                raise ValueError
        except (ValueError, KeyError):
            body = render_template_string(FORM, error="Please enter a valid age (1–120) and non-negative annual income.")
            return render_template_string(BASE, css=CSS, body=body)
        results = find_recommendations(user)
        body = render_template_string(RESULTS, user=user, results=results)
        return render_template_string(BASE, css=CSS, body=body)
    body = render_template_string(FORM, error=None)
    return render_template_string(BASE, css=CSS, body=body)

if __name__ == "__main__":
    app.run(debug=True)
