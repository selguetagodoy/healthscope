import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from import_epof import parse_csv

class CatalogTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(parse_csv("Código ORPHA,Nombre\n5,Ejemplo A\n7,Ejemplo B\n".encode()),[{"code":5,"name":"Ejemplo A"},{"code":7,"name":"Ejemplo B"}])
    def test_duplicate(self):
        with self.assertRaises(ValueError):
            parse_csv(b"codigo,nombre\n5,A\n5,B\n")
    def test_missing_name(self):
        with self.assertRaises(ValueError):
            parse_csv(b"codigo,nombre\n5,\n")
