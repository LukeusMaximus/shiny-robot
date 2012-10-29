from __future__ import division
from bristol_stock_exchange import BSE
import copy

import math

class AABuyer:
    def update_limit_price(self, limit_price):
        self.limit_price = limit_price

    def aggressiveness_model(self, theta, doa, equilibrium_price):
        assert doa >= -1 and doa <= 1

        diff_from_equilibrium = self.limit_price - equilibrium_price

        if doa >= 0 and doa <= 1:
            return equilibrium_price * (1-doa*math.exp(theta*(doa-1)))
        else:
            theta_bar = equilibrium_price * math.exp(-theta)
            theta_bar /= diff_from_equilibrium
            theta_bar -= 1

            t = diff_from_equilibrium*(1-(doa+1)*math.exp(doa*theta_bar))
            t += equilibrium_price
            return t

class AASeller:
    PMAX = 6

    def update_limit_price(self, limit_price):
        self.limit_price = limit_price

    def aggressiveness_model(self, theta, r, equilibrium_price):
        assert r >= -1 and r <= 1

        theta_bar = self.PMAX-equilibrium_price
        theta_bar /= equilibrium_price - self.limit_price
        theta_bar = math.log(theta_bar)
        theta_bar -= theta

        if r >= 0 and r <= 1:
            return equilibrium_price + ((self.PMAX - equilibrium_price)*r*math.exp((r-1)*theta))
        else:
            print "this maths, not the other maths"

            return equilibrium_price + (equilibrium_price-self.limit_price)*r*math.exp((r+1)*theta_bar)

class AA(BSE.Trader):
    def __init__(self, ttype, tid, balance):
        BSE.Trader.__init__(self,ttype, tid, balance)
        self.role = None


    #doa -> between -1 and 1
    #1 passive
    #-1 is aggressive
    def aggressiveness_model(self, limit_price, theta, doa, equilibrium_price):


        return target_price

    def respond(self, time, lob, trade, verbose):
        pass

    def getorder(self, time, countdown, lob):
        if len(self.orders) < 1:
            return None


        limit_price = self.orders[0].price
