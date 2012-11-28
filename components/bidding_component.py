class BiddingComponent:
    def __init__(self, side, limit_price, instrument):

        self.limit_price = self.limit_price          
        self.first_trading_round = True
        self.current_instrument = instrument

        self.eta = 3
        self.max_spread = 1
        self.LAMBDA_R = 0.05
        self.LAMBDA_A = 0.01
        
        self.best_bid = 0
        self.best_ask = 0

        self.inner_price = self.inner_price_seller
        if (side == "bid"):
            self.inner_price = self.inner_price_buyer


    #public bool IsFirstTradingRound { get { return _isFirstTradingRound; } set { _isFirstTradingRound = value; } }

    def update_best_prices(self, best_bid, best_ask):
        if (best_bid == 0.0):
            best_bid = self.current_instrument.MinPrice
        if (best_ask == 0.0):
            best_ask = self.current_instrument.MaxPrice

        self.best_bid = best_bid
        self.best_ask = best_ask

    def price(self, tau)
        if not self.first_trading_round and tau < 0:
            return tau, False      
        price, success = self.inner_price(tau);
        ticksInPrice = int(price / self.current_instrument.PriceTick);
        return float(ticksInPrice * self.current_instrument.PriceTick), success          
    
    def inner_price_buyer(self, tau)
        price = 0.0
        success = False
        
        if self.limit_price <= self.best_bid):
            success = True
            price = self.limit_price
        elif self.limit_price >= self.best_ask and self.best_ask - self.best_bid <= self.max_spread:
            success = True
            price = self.best_ask
        elif self.limit_price > self.best_bid:
            success = True
            if self.first_trading_round:
                best_ask_plus = (1.0 + self.LAMBDA_R) * self.bestAsk + self.LAMBDA_A;
                price = self.best_bid + (min(self.limit_price, best_ask_plus) - self.best_bid) / self.eta;
            else:
                if self.best_ask <= tau:
                    price = self.best_ask
                else:
                    price = self.best_bid + (tau - self.best_bid) / self.eta;
        return price, success

    def inner_price_seller(self, tau):
        price = 0.0
        success = False

        if self.limit_price >= self.best_ask:
            success = True
            price = self.limit_price
        elif self.limit_price <= self.best_bid and self.best_ask - self.best_bid <= self.max_spread:
            success = True
            price = self.best_bid
        elif self.limit_price < self.best_ask:
            success = True
            if self.first_trading_round:
                best_bid_minus = (1.0 - self.LAMBDA_R) * self.best_bid - self.LAMBDA_A
                price = self.best_ask - (self.best_ask - max(self.limit_price, best_bid_minus)) / self.eta
                self.first_trading_round = False
            else:
                if self.best_bid >= tau:
                    price = self.best_bid
                else:
                    price = self.best_bsk - (self.best_ask - tau) / self.eta
        return price, success

