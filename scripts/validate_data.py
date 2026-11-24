#!/usr/bin/env python3
"""Validate published datasets and direct public-source links."""

import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def check(condition, message, errors):
    if not condition:
        errors.append(message)


def valid_https(url):
    parts = urlsplit(url or "")
    return parts.scheme == "https" and bool(parts.hostname)


def validate():
    errors = []
    events = load(ROOT / "events.json")
    sources = load(ROOT / "data/sources.json")
    medicines = load(ROOT / "data/medications.json")
    indicators = load(ROOT / "data/indicators.json")
    institutions = load(ROOT / "data/institutions.json")
    research = load(ROOT / "data/research.json")
    pending = load(ROOT / "data/pending.json")
    coverage = load(ROOT / "data/coverage.json")
    stakeholders = load(ROOT / "data/stakeholders.json")
    media = load(ROOT / "data/media.json")
    social_posts = load(ROOT / "data/social-posts.json")
    checks = ((stakeholders, "stakeholders"), (media, "media"), (social_posts, "social_posts"), (coverage, "coverage"), (events, "events"), (sources, "sources"), (medicines, "medications"), (indicators, "indicators"), (institutions, "institutions"), (research, "research"), (pending, "pending"))
    for records, label in checks:
        check(isinstance(records, list), label + " must be an array", errors)
        if not isinstance(records, list):
            continue
        ids = [item.get("id") for item in records if isinstance(item, dict)]
        check(all(ids), label + " records must have ids", errors)
        check(len(ids) == len(set(ids)), label + " contains duplicate ids", errors)
    check({x.get("code") for x in coverage if x.get("regime") == "GES"} == {str(i) for i in range(1,91)}, "GES catalog must contain codes 1–90", errors)
    check(sum(x.get("regime") == "LRS" for x in coverage) == 27, "LRS catalog must contain 27 rows", errors)
    check(len(coverage) == 117, "coverage catalog must contain 117 rows", errors)
    for x in coverage:
        check(bool(x.get("name")) and valid_https(x.get("url")) and valid_https(x.get("source_url")), "coverage row has incomplete provenance", errors)
    for actor in stakeholders:
        check(bool(actor.get("name")) and valid_https(actor.get("source_url")), "stakeholder without provenance", errors)
        for channel in actor.get("channels", []):
            check(channel.get("platform") in ("LinkedIn", "X") and valid_https(channel.get("url")) and valid_https(channel.get("source_url")), "invalid stakeholder channel", errors)
    for item in media:
        check(valid_https(item.get("url")) and (not item.get("feed") or valid_https(item["feed"])), "invalid media link", errors)
    for post in social_posts:
        check(post.get("source_type") in ("LinkedIn", "X") and valid_https(post.get("url")) and bool(post.get("status")), "invalid social post", errors)
    epof_path = ROOT / "data/epof.json"
    if epof_path.exists():
        catalog = load(epof_path)
        rows = catalog.get("rows", [])
        codes = [r.get("code") for r in rows]
        check(len(rows) == catalog.get("count") == catalog.get("declared_count") == 9784, "EPOF catalogue count mismatch", errors)
        check(len(codes) == len(set(codes)) and all(isinstance(c,int) and c>0 for c in codes), "EPOF invalid or duplicate ORPHA codes", errors)
        check(all(bool(r.get("name")) for r in rows) and valid_https(catalog.get("source_url")), "EPOF missing names or provenance", errors)
    isp = load(ROOT / "data/isp-registry.json")
    isp_rows = isp.get("rows", [])
    regs = [r.get("registration") for r in isp_rows]
    check(len(isp_rows) == isp.get("count") and len(regs) == len(set(regs)), "ISP count or duplicate registrations", errors)
    check(valid_https(isp.get("source_url")) and bool(isp.get("scope")), "ISP provenance missing", errors)
    check(all(r.get("registration") and r.get("name") and r.get("holder") and r.get("checked_at") for r in isp_rows), "ISP row incomplete", errors)
    budget = load(ROOT / "data/budget-history.json")
    check(len(budget["rows"]) == budget["count"] == 10 and {x["year"] for x in budget["rows"]} == set(range(2017,2027)), "Budget coverage mismatch", errors)
    for dataset in ("clinical-trials","patents","procurement"):
        path = ROOT / ("data/"+dataset+".json")
        check(path.exists(), dataset+" dataset missing", errors)
        if path.exists():
            obj = load(path)
            records = obj.get("rows", [])
            keys = [x.get("id") for x in records]
            check(len(records) == obj.get("count") and len(set(keys)) == len(keys) and all(keys), dataset+" count or identifier mismatch", errors)
            check(valid_https(obj.get("source_url")) and bool(obj.get("scope")), dataset+" missing provenance", errors)
    for record in coverage:
        if record.get("treatments"):
            check(record.get("treatment_source")==record.get("url") and bool(record.get("treatment_checked_at")), "Treatment requires direct evidence and review date", errors)
    for row in budget["rows"]:
        check(row["initial_thousand_clp"]>0 and 0<=row["expense_pct"]<=200 and valid_https(row["source_url"]), "Budget invalid values", errors)
    event_urls = set()
    for i, event in enumerate(events):
        prefix = "events[" + str(i) + "]"
        check(event.get("status") == "Verificado", prefix + " must have status Verificado", errors)
        check(valid_https(event.get("url")), prefix + " must link to an HTTPS source", errors)
        check(bool(event.get("title")) and bool(event.get("authority")) and bool(event.get("summary")), prefix + " is missing editorial fields", errors)
        try:
            date.fromisoformat(event.get("date", ""))
            date.fromisoformat(event.get("published", ""))
        except ValueError:
            errors.append(prefix + " has an invalid ISO date")
        normalized = event.get("url", "").split("#", 1)[0].rstrip("/").lower()
        check(normalized not in event_urls, prefix + " duplicates a source URL", errors)
        event_urls.add(normalized)
    source_ids = {item.get("id") for item in sources}
    automated = [item for item in sources if item.get("automated") is True]
    check(len(automated) >= 3, "At least three automated sources must be configured", errors)
    for i, source in enumerate(sources):
        prefix = "sources[" + str(i) + "]"
        check(valid_https(source.get("url")), prefix + " must have an HTTPS URL", errors)
        if source.get("automated"):
            check(valid_https(source.get("monitor_url")), prefix + " must have an HTTPS monitor URL", errors)
            check(source.get("monitor_format") in ("rss", "isp-alert-table"), prefix + " has an unknown monitor format", errors)
    for i, record in enumerate(medicines + indicators + institutions + research + pending):
        if "url" in record:
            check(valid_https(record.get("url")), "linked record " + str(i) + " must use HTTPS", errors)
    for item in pending:
        check(item.get("status") == "Pendiente de revisión", "pending records must remain unpublished", errors)
        check(item.get("source_id") in source_ids, "pending record references an unknown source", errors)
    if errors:
        return errors, {name: len(value) for value, name in checks if isinstance(value, list)}
    return [], {name: len(value) for value, name in checks if isinstance(value, list)}


if __name__ == "__main__":
    errors, counts = validate()
    if errors:
        for error in errors:
            print("ERROR: " + error)
        raise SystemExit(1)
    print("Validación correcta: " + ", ".join(key + "=" + str(value) for key, value in counts.items()))
