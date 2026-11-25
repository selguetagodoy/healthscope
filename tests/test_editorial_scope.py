import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from editorial_scope import public_press

class EditorialScopeTests(unittest.TestCase):
    def test_irrelevant_press(self):
        for title in ("Salud sexual entre adultos: lo que conviene saber antes de un encuentro pagado", "Matilde Burgos y Mauricio Bustamante debutan como dupla televisiva", "Psicología de la regulación del estrés en entretenimiento digital"):
            self.assertFalse(public_press({"source_type":"Prensa","title":title}))
    def test_policy_press(self):
        for title in ("Diputada presenta proyecto de ley de endometriosis", "Aumenta presupuesto de Salud", "Telemedicina se incorpora como prestación", "Cambios en Ley Ricarte Soto"):
            self.assertTrue(public_press({"source_type":"Prensa","title":title}))
    def test_original_official_and_reviewed(self):
        self.assertTrue(public_press({"source_type":"Comunicado institucional","title":"Nuevo anuncio"}))
        self.assertTrue(public_press({"source_type":"Prensa","status":"Verificado","title":"Nota revisada"}))
