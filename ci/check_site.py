from __future__ import annotations

import json
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
):
    if required not in sitemap:
        errors.append(f"sitemap.xml missing {required}")

if "<lastmod>2026-10-09</lastmod>" not in sitemap:
    errors.append("sitemap.xml does not contain the current update date.")

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
    sys.exit(1)

print(f"Site checks passed ({len(html_files)} HTML files checked).")
