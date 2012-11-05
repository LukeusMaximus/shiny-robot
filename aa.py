from __future__ import division
from bristol_stock_exchange import BSE
import copy

import math
import random


#guesswork comment!
ALPHA_MIN = 0.02;
ALPHA_MAX = 0.16;
THETA_MIN = -8;
THETA_MAX = 2;

class RoundRobinBuffer:
    def __init__(self, window_size):
        self.buffer = []
        self.window_size = window_size

    def append(self, hash):
        c = copy.copy(hash)
        if not c.has_key("age"):
            c["age"] = 0
        print "buffer append"
        self.buffer.append(c)

    def age_buffer(self):
        removal = []
        for hash in self.buffer:
            hash["age"] += 1
            if hash["age"] > self.window_size:
                removal.append(hash)

        for hash in removal:
            self.buffer.remove(hash)

    def __getitem__(self, index):
        return self.buffer[index]

    def __len__(self):
        return len(self.buffer)

    def __iter__(self):
        return self.buffer.__iter__()

class AACommon:
    def __init__(self):
        #-1 is most aggressive
        # 1 is least aggressive
        self.doa = 0
        self.learning_rate_beta1 = 0.5
        self.learning_rate_beta2 = 0.5
        self.theta = 0
        self.last_transaction_price = None
        self.previous_trades = RoundRobinBuffer(self.N)
        self.tau = 1

        #this is a magical ass pull by sam
        self.N = 10
        #these are magical ass pulls by vytelingum
        self.weight_decay = 0.9
        self.nyan = 3

    def interesting_trades(self):
        return self.previous_trades

    def update_limit_price(self, limit_price):
        self.limit_price = limit_price

    def theta_star(self,alpha):
        alphabar = (alpha - ALPHA_MIN) / (ALPHA_MAX - ALPHA_MIN);
        return (THETA_MAX-THETA_MIN)*(1-alphabar*math.exp(2*(alphabar-1)))+THETA_MIN

    def long_term_learning(self,equilibrium_price):
        interesting_trades = self.interesting_trades()
        alpha = (sum([(x-equilibrium_price)**2 for x in interesting_trades])/self.N)**0.5/equilibrium_price
        ts = self.theta_star(alpha)
        self.theta = self.theta + self.learning_rate_beta2*(ts-self.theta)

    def adaptive_component(self, equilibrium_price, trade, best_bid_price):
        self.short_term_learning(best_bid_price, trade)
        self.long_term_learning(equilibrium_price)

    def short_term_learning(self, best_price, trade):
        lambda_value = self.lambda_value(best_price, trade)
        #we guessed self.previous_doa in this term but fuck it we're probably right
        #because luke and I are genii
        delta_t = ((1 + lambda_value) * self.doa) + lambda_value/2
        new_doa = self.doa + (self.learning_rate_beta1 * (delta_t - self.doa))
        self.doa = new_doa

    def decay_old_trades(self):
        for trade in self.previous_trades:
            trade["weight"] *= self.weight_decay

    def receive_trade(self, trade):
        self.decay_old_trades()

        trade = trade.copy()
        trade["weight"] = 1

        self.previous_trades.append(trade)
        self.previous_trades.age_buffer()

    def equilibrium_estimator(self):
        interesting_trades = self.previous_trades
        n = sum(x["weight"] for x in interesting_trades)
        sx = sum(x["price"]*x["weight"] for x in interesting_trades)
        mean = sx/n
        return mean

class AABuyer(AACommon):

    def __init__(self):
        AACommon.__init__(self)

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

    def lambda_value(self, best_bid_price, trade):
        if trade is not None:
            #guesswork, flip these if it doesn't beat zip
            if self.tau >= trade["price"]:
                #become more passive
                lambda_value = 0.05
            else:
                #become more aggressive
                lambda_value = -0.05
        elif best_bid_price is not None:
            if self.tau <= best_bid_price:
                print "going down"
                #become more aggressive
                lambda_value = -0.05

        return lambda_value

    def bidding_component(self, market_best_ask, market_best_bid, time):
        if len(self.orders) > 0:
            order = self.orders[0]
            assert order.otype == "Bid"
            if order.price <= market_best_bid:
                return None
            elif len(self.previous_trades) == 0:
                bid = market_best_bid + (min(order.price, market_best_ask) - market_best_bid)/self.nyan
            elif market_best_ask <= self.tau:
                bid = market_best_ask
            else:
                bid = market_best_bid + (self.tau-market_best_bid)/self.nyan

            return BSE.Order(order.tid, "Bid", bid, order.qty)
        return None

class AASeller(AACommon):
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

    def lambda_value(self, best_ask_price, trade):
        if trade is not None:
            #guesswork, flip these if it doesn't beat zip
            if self.tau <= trade["price"]:
                #become more passive
                lambda_value = 0.05
            else:
                #become more aggressive
                lambda_value = -0.05
        elif best_ask_price is not None:
            if self.tau >= best_ask_price:
                print "going down"
                #become more aggressive
                lambda_value = -0.05

        return lambda_value

    def bidding_component(self, market_best_ask, market_best_bid, time):
        if len(self.orders) > 0:
            order = self.orders[0]
            assert order.otype == "Ask"
            if order.price >= market_best_ask:
                return None
            elif len(self.previous_trades) == 0:
                ask = market_best_ask - (market_best_ask - max(order.price, market_best_bid))/self.nyan
            elif market_best_bid >= self.tau:
                ask = market_best_bid
            else:
                ask = market_best_ask - (market_best_ask - self.tau)/self.nyan

            return BSE.Order(order.tid, "Ask", ask, order.qty)
        return None
