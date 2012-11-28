from components.adaptive_component import *
from components.bidding_component import *
from components.aggressiveness_model import *
from components.equilibrium_estimator import *
import BSE

class CurrentInstrument():
    def __init__(self):
        self.maxprice = 1000
        self.minprice = 1
        self.pricetick = 0.01

class AgentStatus():
    def __init__(self):
        self.current_instrument = CurrentInstrument()
        self.best_bid = None
        self.best_ask = None

    def best_bid_price(self):
        return 1 if self.best_bid == None else self.best_bid

    def best_ask_price(self):
        return 1000 if self.best_ask == None else self.best_ask

class AAAgent(BSE.Trader):
    def __init__(self, ttype, tid, balance):
        BSE.Trader.__init__(self,ttype, tid, balance)
        self.window_size = 30
        self.rho = 0.9

        self.agent_status = AgentStatus()
        self.equilibrium_estimator = EquilibriumEstimator(self)
        self.first_order = True
        self.side = None
        self.previous_limit = None
        self.first_respond = True
        self.last_trade_price = None

    def add_order(self, order):
        self.orders = [order]
        assert self.side == order.otype or self.side == None
        if self.first_order:
            print "setting it up"
            self.first_order = False
            self.side = order.otype
            maxprice = self.agent_status.current_instrument.maxprice
            self.aggressiveness_model = AggressivenessModel(self, order.price, self.side, maxprice)
            self.adaptive_component   = AdaptiveComponent(self, self.side, order.price, self.aggressiveness_model)
            self.bidding_component = BiddingComponent(self.side, order.price, self.agent_status.current_instrument)
            self.previous_limit = order.price
        elif (self.previous_limit != order.price):
            self.previous_limit = order.price
            aggressiveness_model.update_limit_price(limit_price);
            adaptive_component.update_limit_price(limit_price);
            bidding_component.update_limit_price(limit_price);

        self.adjust_from_inactivity()

    def respond(self, time, lob, trade, verbose):

        something = trade is not None
        if len(self.orders) > 0:
            if lob["bids"]["best"] != self.agent_status.best_bid_price():
                self.respond_to_new_best_price(trade, lob["bids"]["best"], "Bid")
                something = True
            else:
                assert trade is None

            if lob["asks"]["best"] != self.agent_status.best_ask_price():
                self.respond_to_new_best_price(trade, lob["asks"]["best"], "Ask")
                something = True
            else:
                assert trade is None

        self.agent_status.best_bid = lob["bids"]["best"]
        self.agent_status.best_ask = lob["asks"]["best"]

        if trade is not None:
            self.last_trade_price = trade["price"]

        if not something and len(self.orders) > 0:
            self.adjust_from_inactivity()

    def respond_to_new_best_price(self, trade, best_price, best_side):
        accepted = trade is not None
        estimated_price = self.equilibrium_estimator.estimated_price
        transaction_price = None

        if accepted:
            transaction_price = trade
            self.equilibrium_estimator.add_new_transaction(transaction_price)
            estimated_price = self.equilibrium_estimator.estimated_price
            self.adaptive_component.update_long_term(transaction_price, estimated_price)

        self.bidding_component.update_best_prices(self.agent_status.best_bid, self.agent_status.best_ask)
        theta = self.adaptive_component.theta
        aggressiveness = self.adaptive_component.aggressiveness

        if (self.first_respond and accepted):
            pi,b = self.bidding_component.price(self.aggressiveness_model.tau)
            aggressiveness = self.aggressiveness_model.compute_r_shout(theta, estimated_price, pi)
            self.adaptive_component.initalise_aggressiveness(aggressiveness)
            self.first_Respond = False

        assert self.last_trade_price is not None
        self.adaptive_component.update_short_term(best_price, best_side, self.last_trade_price, estimated_price)


        return None

    def getorder(self, time, countdown, lob):
        if len(self.orders) > 0:
            tau = self.aggressiveness_model.compute_tau(adaptive_component.theta, adaptive_component.aggressiveness, equilibrium_estimator.estimated_price)
            success = False

            price,success = bidding_component.price(tau, success)
            assert price != 0
            bidding_component.first_trading_round = False
            if success:
                return BSE.Order(self.tid, self.side, price, self.orders[0].qty, time)


    def adjust_from_inactivity(self):
        estimated_price = self.equilibrium_estimator.estimated_price

        self.bidding_component.update_best_prices(self.agent_status.best_bid_price(), self.agent_status.best_ask_price())

        theta = self.adaptive_component.theta
        self.aggressiveness = self.adaptive_component.aggressiveness

        update = self.adaptive_component.update_short_term_from_inactivity(estimated_price)
        if (update):
            return True

        return False
