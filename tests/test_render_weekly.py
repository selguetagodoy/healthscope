import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from render_weekly import render
class TestWeeklyRender(unittest.TestCase):
    def test_static_content_and_escaping(self):
        template=(ROOT/"index.html").read_text(encoding="utf-8")
        item={"title":"Noticia <b> sanitaria","url":"https://example.org/official","published":"2026-11-24","authority":"ISP","summary":"Dato original","topic":"Medicamentos"}
        d={"window_start":"2026-11-18","window_end":"2026-11-24","verified":[item],"candidates":[dict(item,title="Agenda")],"sources":[]}
        result=render(template,d,True)
        self.assertIn("Noticia &lt;b&gt; sanitaria",result)
        self.assertIn("Dato original",result)
        self.assertIn('id="weeklyReport"',result)
        self.assertNotIn('id="weeklyVerified" aria-live="polite">Cargando',result)
        self.assertIn("Agenda",result)
