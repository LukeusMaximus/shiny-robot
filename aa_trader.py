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
            print "aa getting an bid order"
            self.buyer_agent.orders = [order]
        elif order.otype == "Ask":
            print "aa getting an ask order", order
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
                    print "aa order bid",str(r.price) + "," + str(r.time) + "," + str(self.buyer_agent.equilibrium_price) + "," + str(self.buyer_agent.doa) + "," + str(self.buyer_agent.tau) + "," + str(self.buyer_agent.limit_price())
                    self.buyer_agent.orders = []
                return r
            else:
                assert self.orders[0].otype == "Ask"
                print "asking!"
                r = self.seller_order(self.best_bid_price(lob),
                                     self.best_ask_price(lob), time)
                if r is not None:
                    print [r]
                    print "aa order ask",str(r.price) + "," + str(r.time) + "," + str(self.seller_agent.equilibrium_price) + "," + str(self.seller_agent.doa) + "," + str(self.seller_agent.tau) + "," + str(self.seller_agent.limit_price())
                    self.seller_agent.orders = []
                return r

    def buyer_respond(self, trade, lob):
        self.buyer_agent.equilibrium_estimator()
        self.buyer_agent.adaptive_component(trade, self.best_bid_price(lob))
        self.buyer_agent.aggressiveness_model()

    def seller_respond(self, trade, lob):
        self.seller_agent.equilibrium_estimator()
        self.seller_agent.adaptive_component(trade, self.best_ask_price(lob))
        self.seller_agent.aggressiveness_model()

    def buyer_order(self, best_bid_price, best_ask_price, time):
        # TODO Aggressiveness model and adaptive component updates here
        self.buyer_agent.adaptive_component2()
        self.buyer_agent.aggressiveness_model()
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
        # TODO Aggressiveness model and adaptive component updates here
        self.seller_agent.adaptive_component2()
        self.seller_agent.aggressiveness_model()
        o = self.seller_agent.bidding_component(best_ask_price, best_bid_price, time)
        if o is not None:
            print "aa making a trade"
            if o.price > BSE.bse_sys_maxprice:
                o.price = BSE.bse_sys_maxprice
            print "aas o", o
            print "aas lp", self.seller_agent.limit_price()
            print "aas da", self.seller_agent.doa
            assert o.price >= self.seller_agent.limit_price() and o.price <= BSE.bse_sys_maxprice
            assert o.otype == "Ask"
            assert o.qty > 0
        return o

    def receive_trade(self, trade):
        if trade is not None:
            self.buyer_agent.receive_trade(trade)
            self.seller_agent.receive_trade(trade)
