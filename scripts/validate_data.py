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
    checks = ((events, "events"), (sources, "sources"), (medicines, "medications"), (indicators, "indicators"), (institutions, "institutions"), (research, "research"), (pending, "pending"))
    for records, label in checks:
        check(isinstance(records, list), label + " must be an array", errors)
        if not isinstance(records, list):
            continue
        ids = [item.get("id") for item in records if isinstance(item, dict)]
        check(all(ids), label + " records must have ids", errors)
        check(len(ids) == len(set(ids)), label + " contains duplicate ids", errors)
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
