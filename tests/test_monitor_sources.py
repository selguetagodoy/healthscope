import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import monitor_sources


class MonitorSourceTests(unittest.TestCase):
    def test_rss_records_are_normalized_and_stay_pending(self):
        xml = b'''<?xml version="1.0"?><rss><channel><item><title>Noticia &amp; salud</title><link>https://minsal.cl/noticia/?utm=feed</link><pubDate>Mon, 23 Nov 2026 14:50:23 +0000</pubDate><description>&lt;p&gt;Texto p&amp;uacute;blico&lt;/p&gt;</description></item></channel></rss>'''
        source = {"id": "minsal-news", "name": "MINSAL", "category": "actualidad"}
        fixed_now = datetime(2026, 11, 24, 12, tzinfo=timezone.utc)
        records = monitor_sources.parse_rss(xml, source, fixed_now)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["date"], "2026-11-23")
        self.assertEqual(records[0]["url"], "https://minsal.cl/noticia")
        self.assertEqual(records[0]["status"], "Pendiente de revisión")
        self.assertEqual(records[0]["title"], "Noticia & salud")

    def test_alert_table_extracts_official_article_link(self):
        html = b'''<table><tr><td>16-11-2026</td><td>Falsificados</td><td>Farmaceutico</td><td>Alerta de producto</td><td><a href="https://ispch.cl/alerta/producto/">Publicacion ISP</a></td></tr></table>'''
        source = {"id": "isp-alertas", "name": "ISP", "category": "farmaceutico"}
        fixed_now = datetime(2026, 11, 24, 12, tzinfo=timezone.utc)
        records = monitor_sources.parse_isp_alerts(html, source, fixed_now)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["date"], "2026-11-16")
        self.assertEqual(records[0]["url"], "https://ispch.cl/alerta/producto")

    def test_canonical_url_strips_tracking_and_rejects_non_https(self):
        self.assertEqual(monitor_sources.canonical_url("https://EXAMPLE.org/a/?utm_source=x#top"), "https://example.org/a")
        self.assertEqual(monitor_sources.canonical_url("http://example.org/a"), "")

    def test_schedule_window_uses_santiago_daylight_time(self):
        summertime = datetime(2026, 11, 24, 11, 0, tzinfo=timezone.utc)
        wintertime = datetime(2026, 6, 24, 12, 0, tzinfo=timezone.utc)
        self.assertTrue(monitor_sources.in_santiago_cut_window(summertime))
        self.assertTrue(monitor_sources.in_santiago_cut_window(wintertime))
        self.assertFalse(monitor_sources.in_santiago_cut_window(datetime(2026, 11, 24, 12, 30, tzinfo=timezone.utc)))


if __name__ == "__main__":
    unittest.main()
