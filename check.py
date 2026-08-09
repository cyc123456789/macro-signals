#!/usr/bin/env python3
"""StratWatch data validator. Run before every commit: python3 check.py"""
import json, os, re, sys

SECTIONS   = {"cyber", "military", "geo", "tech", "nexus"}
KINDS      = {"brief", "weekly", "monthly"}
SEVERITY   = {"critical", "high", "medium", "warning", "info"}   # index.html CSS knows only these
CONFIDENCE = {"confirmed", "likely", "unverified"}
CATEGORY   = {"military", "cyber", "geo", "tech"}
DATE       = re.compile(r"^\d{4}-\d{2}-\d{2}$")

errs = []
def bad(m): errs.append(m)

def bilingual(obj, where, required=True):
    """{zh, en} — both languages are the whole point of this site."""
    if obj is None:
        if required: bad(f"{where}: missing")
        return
    if not isinstance(obj, dict): return bad(f"{where}: must be an object with zh+en")
    for k in ("zh", "en"):
        if not obj.get(k, "").strip(): bad(f"{where}.{k}: empty")

def load(p):
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except Exception as e:
        bad(f"{p}: unreadable ({e})"); return None

manifest = load("manifest.json")
glossary = load("glossary.json")
if manifest is None or glossary is None:
    print("\n".join(errs)); sys.exit(1)

known_terms = {t.get("term") for t in glossary.get("terms", [])}

# ---- glossary ----
if not DATE.match(glossary.get("updated", "")): bad("glossary.updated: bad date")
seen = set()
for i, t in enumerate(glossary.get("terms", [])):
    w = f"glossary.terms[{i}]"
    term = t.get("term", "").strip()
    if not term: bad(f"{w}.term: empty")
    if term in seen: bad(f"{w}.term: duplicate '{term}'")
    seen.add(term)
    if not t.get("zh", "").strip(): bad(f"{w}.zh: empty (中文對照是必填)")
    bilingual(t.get("def"), f"{w}.def")
    if t.get("category") not in CATEGORY: bad(f"{w}.category: {t.get('category')!r} not in {sorted(CATEGORY)}")
    if not DATE.match(t.get("first_seen", "")): bad(f"{w}.first_seen: bad date")

# ---- manifest ----
if not DATE.match(manifest.get("updated", "")): bad("manifest.updated: bad date")
reports = manifest.get("reports", [])
dates = []
for i, r in enumerate(reports):
    w = f"manifest.reports[{i}]"
    f_ = r.get("file", "")
    if not f_.startswith("reports/"): bad(f"{w}.file: must live under reports/")
    if not os.path.exists(f_): bad(f"{w}.file: {f_} does not exist")
    if r.get("kind") not in KINDS: bad(f"{w}.kind: {r.get('kind')!r} not in {sorted(KINDS)}")
    if not DATE.match(r.get("date", "")): bad(f"{w}.date: bad date")
    else: dates.append(r["date"])
    bilingual(r.get("title"), f"{w}.title")
if dates != sorted(dates, reverse=True): bad("manifest.reports: must be sorted newest-first")

listed = {r.get("file") for r in reports}
for f_ in sorted(os.listdir("reports")) if os.path.isdir("reports") else []:
    if f_.endswith(".json") and f"reports/{f_}" not in listed:
        bad(f"reports/{f_}: on disk but not in manifest")

# ---- reports ----
for r in reports:
    p = r.get("file", "")
    if not os.path.exists(p): continue
    d = load(p)
    if d is None: continue
    if d.get("date") != r.get("date"): bad(f"{p}: date disagrees with manifest")
    if d.get("kind") != r.get("kind"): bad(f"{p}: kind disagrees with manifest")
    bilingual(d.get("title"), f"{p}.title")
    bilingual(d.get("focus"), f"{p}.focus")
    n_items = 0
    for si, s in enumerate(d.get("sections", [])):
        w = f"{p}.sections[{si}]"
        if s.get("id") not in SECTIONS: bad(f"{w}.id: {s.get('id')!r} not in {sorted(SECTIONS)}")
        for ii, it in enumerate(s.get("items", [])):
            n_items += 1
            w2 = f"{w}.items[{ii}]"
            if it.get("severity") not in SEVERITY: bad(f"{w2}.severity: {it.get('severity')!r} not in {sorted(SEVERITY)}")
            if it.get("confidence") not in CONFIDENCE: bad(f"{w2}.confidence: {it.get('confidence')!r} not in {sorted(CONFIDENCE)}")
            bilingual(it.get("title"), f"{w2}.title")
            bilingual(it.get("summary"), f"{w2}.summary")
            bilingual(it.get("implication"), f"{w2}.implication")
            if not it.get("source", "").strip(): bad(f"{w2}.source: empty")
            if not str(it.get("url", "")).startswith("http"): bad(f"{w2}.url: needs a real link")
            for term in it.get("terms", []):
                if term not in known_terms: bad(f"{w2}.terms: '{term}' is not in glossary.json")
    if d.get("kind") == "brief" and not 4 <= n_items <= 8:
        bad(f"{p}: brief should carry 4-8 items, got {n_items}")
    if d.get("kind") in ("weekly", "monthly"):
        bilingual(d.get("narrative"), f"{p}.narrative")
    if d.get("kind") == "monthly":
        acts = d.get("actions", [])
        if not 2 <= len(acts) <= 5: bad(f"{p}: monthly needs 2-5 actions, got {len(acts)}")
        for ai, a in enumerate(acts): bilingual(a, f"{p}.actions[{ai}]")

if errs:
    print(f"FAIL ({len(errs)})"); print("\n".join(" - " + e for e in errs)); sys.exit(1)
print(f"OK — {len(reports)} reports, {len(known_terms)} glossary terms")
