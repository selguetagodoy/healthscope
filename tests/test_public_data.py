import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from public_data import order_url
class PurchaseTests(unittest.TestCase):
    def test_direct(self):
        self.assertEqual(order_url("1058095-1001-SE25"),"https://www.mercadopublico.cl/PurchaseOrder/Modules/PO/DetailsPurchaseOrder.aspx?codigoOC=1058095-1001-SE25")
    def test_invalid(self):
        self.assertEqual(order_url("bad"),"")
