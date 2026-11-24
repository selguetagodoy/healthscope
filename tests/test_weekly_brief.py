import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from weekly_brief import relevant, classify, score
class WeeklyBriefTests(unittest.TestCase):
    def test_scope(self):
        self.assertTrue(relevant("Ley Ricarte Soto"))
        self.assertTrue(relevant("Informe GES"))
        self.assertFalse(relevant("Congreso de pesca"))
        self.assertFalse(relevant("Impuesto a juegos"))
    def test_classification(self):
        self.assertEqual(classify({"category":"legislacion","title":"Ley Ricarte Soto"}),"Regulación y Congreso")
        self.assertEqual(classify({"category":"datos","title":"Presupuesto de Salud"}),"Presupuesto y financiamiento")
        self.assertGreater(score({"title":"Trikafta y fibrosis quística"}),score({"title":"Medicamentos"}))
