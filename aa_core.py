from __future__ import division
import BSE
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
        self.doa = -1
        self.learning_rate_beta1 = 0.5
        self.learning_rate_beta2 = 0.5
        self.orders = []
        self.theta = 0
        self.last_transaction_price = None
        self.tau = 1
        self.equilibrium_price = 1
        self.lambda_val = 0.05

        #this is a magical ass pull by sam
        self.N = 10
        #these are magical ass pulls by vytelingum
        self.weight_decay = 0.9
        self.nyan = 3

        self.previous_trades = RoundRobinBuffer(self.N)

        # DEBUG
        self.strval = ""

    def interesting_trades(self):
        return self.previous_trades

    def limit_price(self):
        return self.orders[0].price

    def theta_star(self, alpha):
        alphabar = (alpha - ALPHA_MIN) / (ALPHA_MAX - ALPHA_MIN);
        print "aa ltl alpha", alpha, "alphabar", alphabar
        return (THETA_MAX-THETA_MIN)*(1-alphabar*math.exp(2*(alphabar-1)))+THETA_MIN

    def long_term_learning(self):
        interesting_trades = [x["price"] for x in self.interesting_trades()]
        #if len(interesting_trades) >= self.N:
        print "aa ltl eqp", self.equilibrium_price
        print "aa ltl interesting_trades", interesting_trades
        alpha = (sum([(x-self.equilibrium_price)**2 for x in interesting_trades])/self.N)**0.5/self.equilibrium_price
        ts = self.theta_star(alpha)
        print "aa ltl old theta", self.theta
        self.theta = self.theta + self.learning_rate_beta2*(ts-self.theta)
        print "aa ltl new theta", self.theta

    def adaptive_component(self, trade, best_price):
        self.lambda_val = self.lambda_value(best_price, trade)
        self.adaptive_component2()
        
    def adaptive_component2(self):
        self.short_term_learning(self.lambda_val)
        self.long_term_learning()

    def short_term_learning(self, lambda_value):
        #we guessed self.previous_doa in this term but fuck it we're probably right
        #because luke and I are genii
        delta_t = ((1 + lambda_value) * self.doa) + lambda_value/2
        new_doa = self.doa + (self.learning_rate_beta1 * (delta_t - self.doa))
        print "aa od", self.doa
        self.doa = new_doa
        print "aa lbd", lambda_value
        print "aa dt", delta_t
        print "aa nd", new_doa
        # Screw this, capping it.
        if self.doa > 1:
            self.doa = 1
        elif self.doa < -1:
            self.doa = -1
        assert self.doa >= -1 and self.doa <= 1

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
        print "aa eq", mean
        self.equilibrium_price = mean

class AABuyer(AACommon):

    def __init__(self):
        AACommon.__init__(self)

    def extramarginal(self):
        return self.limit_price() < self.equilibrium_price

    def aggressiveness_model(self):
        if len(self.orders) > 0:
            if self.extramarginal():
                r = self.limit_price()
                if self.doa >= 0 and self.doa <= 1:
                    r *= (1-self.doa*math.exp(self.theta*(self.doa-1)))
                self.tau = r
                assert self.tau >= 1 and self.tau <= self.limit_price()
                self.strval = "aab ame tau = " + str(self.tau) + " lp = " + str(self.limit_price())
                print "aab ame tau", self.tau
            else:
                #if doa > 1:
                #    doa = 1
                #elif doa < -1:
                #    doa = -1
                assert self.doa >= -1 and self.doa <= 1
                assert not self.extramarginal()

                diff_from_equilibrium = self.limit_price() - self.equilibrium_price
                print "aab am dfe", diff_from_equilibrium

                if self.doa >= 0 and self.doa <= 1:
                    self.tau = self.equilibrium_price * (1-self.doa*math.exp(self.theta*(self.doa-1)))
                elif diff_from_equilibrium == 0:
                    self.tau = self.equilibrium_price
                else:
                    print self.equilibrium_price
                    print self.theta
                    print diff_from_equilibrium
                    theta_bar = self.equilibrium_price * math.exp(-self.theta)
                    theta_bar /= diff_from_equilibrium
                    theta_bar -= 1

                    print self.doa
                    print theta_bar
                    t = diff_from_equilibrium*(1-(self.doa+1)*math.exp(self.doa*theta_bar))
                    t += self.equilibrium_price
                    self.tau = t
                assert self.tau >= 1 and self.tau <= self.limit_price()
                self.strval = "aab ami tau = " + str(self.tau) + " lp = " + str(self.limit_price())
                print "aab ami tau", self.tau

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
                print "aab bc case a"
                return None
            elif len(self.previous_trades) == 0:
                print "aab bc case b"
                expr = min([order.price, market_best_ask,0], key=lambda x: 1000000 if x == None else x)
                bid = market_best_bid + (expr - market_best_bid)/self.nyan
            elif market_best_ask <= self.tau:
                print "aab bc case c"
                bid = market_best_ask
            else:
                print "aab bc case d"
                bid = market_best_bid + (self.tau-market_best_bid)/self.nyan
            return BSE.Order(order.tid, "Bid", bid, order.qty, time)
        return None

class AASeller(AACommon):
    PMAX = 1000

    def extramarginal(self):
        return self.limit_price() >= self.equilibrium_price

    def aggressiveness_model(self):
        if len(self.orders) > 0:
            if self.extramarginal():
                r = self.limit_price()
                if self.doa >= 0 and self.doa <= 1:
                    r += (self.PMAX-self.limit_price())*self.doa*math.exp((self.doa-1)*self.theta)
                self.tau = r
                print "aas ame doa", self.doa, "theta", self.theta, "tau", self.tau, "lp", self.limit_price()
                self.strval = "aas ame tau = " + str(self.tau) + " lp = " + str(self.limit_price())
                assert self.tau <= self.PMAX and self.tau >= self.limit_price()
            else:
                print "doa", self.doa
                assert self.doa >= -1 and self.doa <= 1
                assert self.equilibrium_price > 0
                assert not self.extramarginal()

                theta_bar = self.PMAX-self.equilibrium_price
                theta_bar /= self.equilibrium_price - self.limit_price()
                print "eq", self.equilibrium_price
                print "pm", self.PMAX
                print "lp", self.limit_price()
                theta_bar = math.log(theta_bar)
                theta_bar -= self.theta
                print "tb", theta_bar

                if self.doa >= 0 and self.doa <= 1:
                    self.tau = self.equilibrium_price + ((self.PMAX - self.equilibrium_price)*self.doa*math.exp((self.doa+1)*self.theta))
                else:
                    print "this maths, not the other maths"
                    self.tau = self.equilibrium_price + (self.equilibrium_price-self.limit_price())*self.doa*math.exp((self.doa-1)*theta_bar)
                print "aas ami doa", self.doa, "theta", self.theta, "tb", theta_bar, "lp", self.limit_price(), "eqp", self.equilibrium_price, "tau", self.tau
                self.strval = "aas ami tau = " + str(self.tau) + " lp = " + str(self.limit_price())
                assert self.tau <= self.PMAX and self.tau >= self.limit_price()

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

        return -lambda_value

    def bidding_component(self, market_best_ask, market_best_bid, time):
        print "aas -----------------------------"
        if len(self.orders) > 0:
            order = self.orders[0]
            assert order.otype == "Ask"
            print "aas op", order.price, "ba", market_best_ask, "bb", market_best_bid, "tau", self.tau, "eqp", self.equilibrium_price, "lim", self.limit_price()
            print self.strval
            if order.price >= market_best_ask:
                print "aas bc case a"
                return None
            elif len(self.previous_trades) == 0:
                print "aas bc case b"
                ask = market_best_ask
                mop = max([order.price, market_best_bid,1000], key=lambda x: -100000000 if x == None else x)
                ask -= (market_best_ask - mop)/self.nyan
            elif market_best_bid >= self.tau:
                print "aas bc case c"
                ask = market_best_ask
            else:
                print "aas bc case d"
                ask = market_best_ask - (market_best_ask - self.tau)/self.nyan
                assert ask >= self.limit_price()
            return BSE.Order(order.tid, "Ask", ask, order.qty, time)
        return None
        
        
