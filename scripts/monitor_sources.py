#!/usr/bin/env python3
"""Collect recent records from official health sources for editorial review."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
LOCAL_TZ = ZoneInfo("America/Santiago")
MAX_BYTES = 3_000_000
MAX_PENDING = 250
RECENT_DAYS = 120
CUTS = ((8, 0), (12, 0), (16, 30))


def read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    temp.replace(path)


def strip_markup(value: str) -> str:
    class TextOnly(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
            self.skip = 0

        def handle_starttag(self, tag, attrs):
            if tag.lower() in {"style", "script"}: self.skip += 1

        def handle_endtag(self, tag):
            if tag.lower() in {"style", "script"} and self.skip: self.skip -= 1

        def handle_data(self, data):
            if not self.skip: self.parts.append(data)

    parser = TextOnly()
    parser.feed(value or "")
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def canonical_url(url: str) -> str:
    parts = urlsplit((url or "").strip())
    if parts.scheme.lower() != "https" or not parts.hostname:
        return ""
    host = parts.hostname.lower()
    if parts.port:
        host += ":" + str(parts.port)
    path = re.sub(r"/{2,}", "/", parts.path or "/").rstrip("/") or "/"
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not k.lower().startswith("utm_") and k.lower() not in {"utm", "fbclid", "gclid"}))
    return urlunsplit(("https", host, path, query, ""))


def stable_id(url: str) -> str:
    return hashlib.sha256(canonical_url(url).encode("utf-8")).hexdigest()[:18]


def chile_date(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(LOCAL_TZ).date().isoformat()


def parse_rss(content: bytes, source: dict, now: datetime | None = None) -> list[dict]:
    """Parse RSS items into review records; the records remain unpublished."""
    now_local = (now or datetime.now(timezone.utc)).astimezone(LOCAL_TZ)
    cutoff = now_local.date() - timedelta(days=RECENT_DAYS)
    root = ET.fromstring(content)
    items = []
    for item in root.iter():
        if item.tag.rsplit("}", 1)[-1].lower() != "item":
            continue
        fields = {child.tag.rsplit("}", 1)[-1].lower(): child for child in list(item)}
        title = strip_markup("".join(fields.get("title", ET.Element("title")).itertext()))
        link = "".join(fields.get("link", ET.Element("link")).itertext()).strip()
        pub = "".join(fields.get("pubdate", ET.Element("pubDate")).itertext()).strip()
        description = "".join(fields.get("description", ET.Element("description")).itertext())
        if not title or not canonical_url(link) or not pub:
            continue
        keywords = source.get("keywords", [])
        def fold(value):
            return "".join(c for c in unicodedata.normalize("NFD", value.lower()) if not unicodedata.combining(c))
        if keywords and not any(fold(word) in fold(title + " " + strip_markup(description)) for word in keywords):
            continue
        try:
            published = parsedate_to_datetime(pub)
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError, OverflowError):
            continue
        published_date = published.astimezone(LOCAL_TZ).date()
        if published_date < cutoff or published_date > now_local.date() + timedelta(days=1):
            continue
        items.append({
            "id": source["id"] + "-" + stable_id(link),
            "source_id": source["id"],
            "authority": source["name"],
            "date": published_date.isoformat(),
            "published": published_date.isoformat(),
            "category": source.get("category", "actualidad"),
            "title": title,
            "source_type": source.get("source_type", "Fuente oficial"),
            "summary": "" if source.get("source_type") == "Prensa" else strip_markup(description)[:1200],
            "medication": "",
            "status": "Pendiente de revisión",
            "captured_at": now_local.isoformat(timespec="seconds"),
            "url": canonical_url(link),
        })
    return items


class AlertTableParser(HTMLParser):
    """Read the public ANAMED alert table without loading or executing scripts."""

    DATE_RE = re.compile(r"^\d{2}[-/]\d{2}[-/]\d{4}$")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_row = False
        self.in_cell = False
        self.cells = []
        self.cell_parts = []
        self.links = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "tr":
            self.in_row = True
            self.cells = []
            self.links = []
        elif self.in_row and tag.lower() == "td":
            self.in_cell = True
            self.cell_parts = []
        elif self.in_row and tag.lower() == "a" and attrs.get("href"):
            self.links.append(attrs["href"])

    def handle_data(self, data):
        if self.in_row and self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.in_row and tag == "td" and self.in_cell:
            self.cells.append(re.sub(r"\s+", " ", " ".join(self.cell_parts)).strip())
            self.in_cell = False
        elif tag == "tr" and self.in_row:
            if len(self.cells) >= 4 and self.DATE_RE.match(self.cells[0]):
                self.rows.append((self.cells[:], self.links[:]))
            self.in_row = False
            self.in_cell = False


def parse_isp_alerts(content: bytes, source: dict, now: datetime | None = None) -> list[dict]:
    now_local = (now or datetime.now(timezone.utc)).astimezone(LOCAL_TZ)
    cutoff = now_local.date() - timedelta(days=RECENT_DAYS)
    parser = AlertTableParser()
    parser.feed(content.decode("utf-8", errors="replace"))
    records = []
    for cells, links in parser.rows:
        try:
            published_date = datetime.strptime(cells[0].replace("/", "-"), "%d-%m-%Y").date()
        except ValueError:
            continue
        if published_date < cutoff or published_date > now_local.date() + timedelta(days=1):
            continue
        link = next((canonical_url(item) for item in links if canonical_url(item) and "/alerta/" in urlsplit(item).path), "")
        if not link:
            link = next((canonical_url(item) for item in links if canonical_url(item) and "/wp-content/" not in item), "")
        if not link:
            continue
        title = cells[3]
        if not title:
            continue
        category = source.get("category", "farmaceutico")
        issue_type = cells[1] if len(cells) > 1 else "Alerta sanitaria"
        product = cells[2] if len(cells) > 2 else ""
        records.append({
            "id": source["id"] + "-" + stable_id(link),
            "source_id": source["id"],
            "authority": source["name"],
            "date": published_date.isoformat(),
            "published": published_date.isoformat(),
            "category": category,
            "title": title,
            "summary": "".join(part for part in (issue_type, product) if part),
            "medication": "",
            "status": "Pendiente de revisión",
            "captured_at": now_local.isoformat(timespec="seconds"),
            "url": link,
        })
    return records


def in_santiago_cut_window(now: datetime, tolerance_minutes: int = 20) -> bool:
    local = now.astimezone(LOCAL_TZ)
    minute_of_day = local.hour * 60 + local.minute
    return any(abs(minute_of_day - (hour * 60 + minute)) <= tolerance_minutes for hour, minute in CUTS)


def fetch_url(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "HealthScopeChile/0.7 (public-source-monitor; contact: repository owner)", "Accept": "application/rss+xml, application/xml, text/html;q=0.9, */*;q=0.5"})
    with urllib.request.urlopen(request, timeout=25) as response:
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("La respuesta supera el límite de 3 MB")
        return response.status, data


def is_recent(record: dict, today: date) -> bool:
    try:
        published_date = date.fromisoformat(record.get("date", ""))
    except ValueError:
        return False
    return today - timedelta(days=RECENT_DAYS) <= published_date <= today + timedelta(days=1)


def collect(now: datetime | None = None) -> tuple[list[dict], dict]:
    now_utc = now or datetime.now(timezone.utc)
    now_local = now_utc.astimezone(LOCAL_TZ)
    sources = read_json(ROOT / "data" / "sources.json", [])
    pending = read_json(ROOT / "data" / "pending.json", [])
    events = read_json(ROOT / "events.json", [])
    seen = {canonical_url(item.get("url", "")) for item in events + pending if canonical_url(item.get("url", ""))}
    new_items = []
    source_results = []
    successful = 0
    for source in sources:
        if not source.get("automated"):
            continue
        status = {"id": source["id"], "name": source["name"], "monitor_url": source["monitor_url"], "checked_at": now_local.isoformat(timespec="seconds"), "items_seen": 0}
        try:
            code, body = fetch_url(source["monitor_url"])
            if source.get("monitor_format") == "rss":
                records = parse_rss(body, source, now_utc)
            elif source.get("monitor_format") == "isp-alert-table":
                records = parse_isp_alerts(body, source, now_utc)
            else:
                raise ValueError("Formato de fuente sin parser registrado")
            successful += 1
            status["http_status"] = code
            status["status"] = "ok"
            status["items_seen"] = len(records)
            for record in records:
                key = canonical_url(record["url"])
                if key not in seen:
                    record["url"] = key
                    new_items.append(record)
                    seen.add(key)
        except (OSError, urllib.error.URLError, ET.ParseError, UnicodeError, ValueError) as exc:
            status["status"] = "error"
            status["error"] = str(exc)[:300]
            print("Fuente con error: " + source["id"] + " · " + status["error"], file=sys.stderr)
        source_results.append(status)

    all_pending = pending + new_items
    today = now_local.date()
    all_pending = [item for item in all_pending if is_recent(item, today)]
    all_pending.sort(key=lambda item: (item.get("date", ""), item.get("published", ""), item.get("id", "")), reverse=True)
    all_pending = all_pending[:MAX_PENDING]
    monitor = read_json(ROOT / "data" / "monitoring.json", {})
    monitor.update({
        "timezone": "America/Santiago",
        "schedule": ["08:00", "12:00", "16:30"],
        "last_attempt_at": now_utc.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "sources": source_results,
    })
    if successful:
        monitor["last_success_at"] = now_utc.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        monitor["last_success_local"] = now_local.strftime("%Y-%m-%d %H:%M %Z")
    return all_pending, monitor


def main() -> int:
    now = datetime.now(timezone.utc)
    if os.getenv("GITHUB_EVENT_NAME") == "schedule" and not in_santiago_cut_window(now):
        print("Ejecución horaria fuera de los cortes de America/Santiago; se omite la consulta.")
        return 0
    pending, monitor = collect(now)
    write_json(ROOT / "data" / "pending.json", pending)
    write_json(ROOT / "data" / "monitoring.json", monitor)
    print("Fuentes consultadas: " + str(len(monitor.get("sources", []))))
    print("Capturas pendientes: " + str(len(pending)))
    success_count = sum(1 for item in monitor.get("sources", []) if item.get("status") == "ok")
    output_path = os.getenv("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write("successful_sources=" + str(success_count) + "\n")
            output.write("pending_count=" + str(len(pending)) + "\n")
    return 0 if success_count else 1


if __name__ == "__main__":
    raise SystemExit(main())
