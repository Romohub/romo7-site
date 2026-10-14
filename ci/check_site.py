from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

html_files = sorted(ROOT.rglob("*.html"))
if not html_files:
    errors.append("No HTML files found.")

for path in html_files:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()

    if rel == "index.html" and 'name="robots" content="noindex' in text.lower():
        errors.append("Root index.html must not be noindex.")

    for href in re.findall(r'href=["\']([^"\']+)["\']', text, flags=re.I):
        if href.startswith(("#", "http://", "https://", "mailto:", "tel:", "javascript:")):
            continue
        clean = urlsplit(href).path
        if not clean:
            continue
        target = (path.parent / clean).resolve()
        if clean.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            errors.append(f"{rel}: missing internal target {href}")

sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
for required in (
    "https://romohub.github.io/romo7-site/en/",
    "https://romohub.github.io/romo7-site/fa/",
    "https://romohub.github.io/romo7-site/en/collaborate.html",
    "https://romohub.github.io/romo7-site/fa/collaborate.html",
    "https://romohub.github.io/romo7-site/en/ai-qa.html",
    "https://romohub.github.io/romo7-site/fa/ai-qa.html",
    "https://romohub.github.io/romo7-site/en/work/research-sprint-sample.html",
    "https://romohub.github.io/romo7-site/fa/work/research-sprint-sample.html",
):
    if required not in sitemap:
        errors.append(f"sitemap.xml missing {required}")

lastmods = re.findall(r"<lastmod>([^<]+)</lastmod>", sitemap)
if not lastmods:
    errors.append("sitemap.xml has no lastmod entries.")
for value in lastmods:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        errors.append(f"sitemap.xml has invalid lastmod date: {value}")

# Sales readiness must be backed by real case-study evidence and a visible inquiry route.
for lang in ("en", "fa"):
    page = ROOT / lang / "ai-qa.html"
    if not page.exists():
        errors.append(f"Missing PAIB landing page for {lang}")
        continue
    html = page.read_text(encoding="utf-8")
    for required in ("https://github.com/Romohub/paib/blob/main/RESULTS.md",
                     "https://github.com/Romohub/romo7-site/issues/new?template=ai-qa.yml",
                     "https://x.com/trita_a", 'href="#contact"'):
        if required not in html:
            errors.append(f"Missing PAIB proof link in {lang} landing: {required}")
    if "mailto:" in html or "<form" in html:
        errors.append(f"{lang} PAIB page must not claim untested automatic lead submission.")

for homepage in ("index.html", "en/index.html", "fa/index.html"):
    html = (ROOT / homepage).read_text(encoding="utf-8")
    target = "en/ai-qa.html#contact" if homepage == "index.html" else "ai-qa.html#contact"
    if target not in html:
        errors.append(f"{homepage} missing primary qualified AI QA sales CTA")
    if "48 benchmark cases" not in html and "۴۸ سناریوی بنچمارک" not in html:
        errors.append(f"{homepage} does not surface the verifiable PAIB evidence")

ai_qa_issue_form = ROOT / ".github" / "ISSUE_TEMPLATE" / "ai-qa.yml"
if not ai_qa_issue_form.exists():
    errors.append("Dedicated non-confidential AI QA inquiry issue form is missing.")
else:
    issue_text = ai_qa_issue_form.read_text(encoding="utf-8")
    for required in ("No work", "confidential", "authorized test environment"):
        if required.lower() not in issue_text.lower():
            errors.append(f"AI QA issue template lacks safety language: {required}")

issue_form = ROOT / ".github" / "ISSUE_TEMPLATE" / "collaboration.yml"
if not issue_form.exists():
    errors.append("Structured collaboration issue form is missing.")

analytics_config = ROOT / "analytics-config.json"
try:
    analytics = json.loads(analytics_config.read_text(encoding="utf-8"))
    if not isinstance(analytics.get("enabled"), bool):
        errors.append("analytics-config.json enabled must be boolean.")
    if "cloudflareWebAnalyticsToken" not in analytics:
        errors.append("analytics-config.json missing cloudflareWebAnalyticsToken.")
except Exception as exc:
    errors.append(f"analytics-config.json invalid: {exc}")

if errors:
    print("Site checks failed:")
    for error in errors:
        print(f"- {error}")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            # Escape workflow-command data so filenames/messages stay literal.
            message = error.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::error title=Static site validation::{message}")
    sys.exit(1)

print(f"Site checks passed ({len(html_files)} HTML files checked).")
