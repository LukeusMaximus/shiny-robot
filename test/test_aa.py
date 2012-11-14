import sys
sys.path.insert(0, "../")

import aa_core
from bristol_stock_exchange import BSE

import unittest
from random import random

class TestAA(unittest.TestCase):

    def setUp(self):
        self.aas = aa_core.AASeller()
        self.aas.orders = [BSE.Order(1, "Ask", 2, 1, 0)]

        self.aab = aa_core.AABuyer()
        self.aab.orders = [BSE.Order(1, "Bid", 4, 1, 0)]

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

    def test_buyer_aggressiveness_model_returns_equilibrium_price_at_0(self):
        price = self.aab.aggressiveness_model(0, 0, 3)
        self.assertEqual(price, 3)

    def test_buyer_aggressiveness_model_goes_down_after_zero(self):
        price = self.aas.aggressiveness_model(0, 0.1, 3)
        self.assertTrue(price > 3)

    def test_buyer_aggressiveness_model_goes_up_after_zero(self):
        price = self.aas.aggressiveness_model(0, -0.1, 3)
        self.assertTrue(price < 3)

    def test_buyer_aggressiveness_model_hits_limit_price_at_minus_one(self):
        price = self.aas.aggressiveness_model(0, -1, 3)
        self.assertTrue(price, 4)

    def test_ee(self):
        self.aas.receive_trade({"price":18})
        self.assertEqual(self.aas.equilibrium_estimator(), 18)

        self.aas.receive_trade({"price": 18})
        self.assertTrue(abs(self.aas.equilibrium_estimator()-18) < 0.00001)


        aas = aa_core.AASeller()
        aas.receive_trade({"price": 19})
        aas.receive_trade({"price": 0})
        self.assertTrue(abs(aas.equilibrium_estimator()-9) < 0.00001)

if __name__ == "__main__":
    unittest.main()
