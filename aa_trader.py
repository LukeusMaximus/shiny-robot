import BSE
import aa_core as aa

class AATrader(BSE.Trader):
    def __init__(self, ttype, tid, balance):
        BSE.Trader.__init__(self,ttype, tid, balance)

        self.buyer_agent = aa.AABuyer()
        self.seller_agent = aa.AASeller()

    def add_order(self, order):
        # in this version, trader has at most one order,
        # if allow more than one, this needs to be self.orders.append(order)
        self.orders=[order]
        print "aa getting an order", order
        if order.otype == "Bid":
            self.buyer_agent.orders = [order]
        elif order.otype == "Ask":
            self.seller_agent.orders = [order]
        else:
            assert False

    def best_ask_price(self, lob):
        bap = lob["asks"]["best"]
        if bap is None:
            bap = BSE.bse_sys_minprice

        return bap
    def best_bid_price(self, lob):
        bbp = lob["bids"]["best"]
        if bbp is None:
            bbp = BSE.bse_sys_maxprice

        return bbp

    def respond(self, time, lob, trade, verbose):
        #print "responding"
        #print "aa BALANCE", self.balance
        if trade is not None:
            self.receive_trade(trade)
            self.buyer_respond(trade, lob)
            self.seller_respond(trade, lob)

    def getorder(self, time, countdown, lob):
        if len(self.orders) > 0:
            print "giving an order"
            print self.orders[0]
            if self.orders[0].otype == "Bid":
                r = self.buyer_order(self.best_bid_price(lob),
                                     self.best_ask_price(lob), time)
                if r is not None:
                    print [r]
                    self.buyer_agent.orders = []
                return r
            else:
                assert self.orders[0].otype == "Ask"
                print "asking!"
                r = self.seller_order(self.best_bid_price(lob),
                                     self.best_ask_price(lob), time)
                if r is not None:
                    print [r]
                    self.buyer_agent.orders = []
                return r


    def buyer_respond(self, trade, lob):
        equilibrium = self.buyer_agent.equilibrium_estimator()
        self.buyer_agent.adaptive_component(equilibrium, trade, self.best_bid_price(lob))
        if len(self.buyer_agent.orders) > 0:
            if not self.buyer_agent.extramarginal(equilibrium):
                self.buyer_agent.aggressiveness_model(self.buyer_agent.theta, self.buyer_agent.doa, equilibrium)
            else:
                self.buyer_agent.aggressiveness_model_extra(self.buyer_agent.theta, self.buyer_agent.doa)
        print "aab eq", equilibrium, "doa", self.buyer_agent.doa, "theta", self.buyer_agent.theta, "tau", self.buyer_agent.tau

    def seller_respond(self, trade, lob):
        equilibrium = self.seller_agent.equilibrium_estimator()
        self.seller_agent.adaptive_component(equilibrium, trade, self.best_ask_price(lob))
        if len(self.seller_agent.orders) > 0:
            if not self.seller_agent.extramarginal(equilibrium):
                self.seller_agent.aggressiveness_model(self.seller_agent.theta, self.seller_agent.doa, equilibrium)
            else:
                self.seller_agent.aggressiveness_model_extra(self.seller_agent.theta, self.seller_agent.doa)
        print "aas eq", equilibrium, "doa", self.buyer_agent.doa, "theta", self.buyer_agent.theta, "tau", self.buyer_agent.tau

    def buyer_order(self, best_bid_price, best_ask_price, time):
        o = self.buyer_agent.bidding_component(best_ask_price, best_bid_price, time)
        if o is not None:
            print "aa making a trade"
            if o.price < BSE.bse_sys_minprice:
                print "aa price", o.price
                print "aa clamping"
                o.price = BSE.bse_sys_minprice
            print "aab b o", o
            print "aab b lp", self.buyer_agent.limit_price()
            print "aab b da", self.buyer_agent.doa
            assert o.price >= BSE.bse_sys_minprice and o.price <= self.buyer_agent.limit_price()
            assert o.otype == "Bid"
            assert o.qty > 0
        return o

    def seller_order(self, best_bid_price, best_ask_price, time):
        o = self.seller_agent.bidding_component(best_ask_price, best_bid_price, time)
        if o is not None:
            print "aa making a trade"
            if o.price > BSE.bse_sys_maxprice:
                o.price = BSE.bse_sys_maxprice
            print "aa s o", o
            print "aa s lp", self.seller_agent.limit_price()
            print "aa s da", self.seller_agent.doa
            assert o.price >= self.seller_agent.limit_price() and o.price <= BSE.bse_sys_maxprice
            assert o.otype == "Ask"
            assert o.qty > 0
        return o

    def receive_trade(self, trade):
        if trade is not None:
            self.buyer_agent.receive_trade(trade)
            self.seller_agent.receive_trade(trade)
