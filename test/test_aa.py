import sys
sys.path.insert(0, "../")

import aa
from bristol_stock_exchange import BSE

import unittest
from random import random

class TestAA(unittest.TestCase):

    def setUp(self):
        self.aas = aa.AASeller()
        self.aas.update_limit_price(2)

        self.aab = aa.AABuyer()
        self.aab.update_limit_price(4)

    def test_seller_aggressiveness_model_returns_equilibrium_price_at_0(self):
        price = self.aas.aggressiveness_model(0, 0, 3)
        self.assertEqual(price, 3)

    def test_seller_aggressiveness_model_goes_down_after_zero(self):
        price = self.aas.aggressiveness_model(0, -0.1, 3)
        self.assertTrue(price < 3)

    def test_seller_aggressiveness_model_goes_up_after_zero(self):
        price = self.aas.aggressiveness_model(0, 0.1, 3)
        self.assertTrue(price > 3)

    def test_seller_aggressiveness_model_hits_limit_price_at_minus_one(self):
        price = self.aas.aggressiveness_model(0, -1, 3)
        self.assertTrue(price, 2)


if __name__ == "__main__":
    unittest.main()
