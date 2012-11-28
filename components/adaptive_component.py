import math

class AdaptiveComponent:
    def __init__(self, agent, side, limit_price, aggressiveness_model):
        self.GAMMA = 2.0
        self.THETA_MIN = -8.0
        self.THETA_MAX = 2.0
        self.BETA1 = 0.5
        self.BETA2 = 0.5
        self.LAMBDA_R = 0.05
        self.LAMBDA_A = 0.01
        self.WS = 30
        
        self.side = side
        self.agent = agent
        self.aggressiveness_model = aggressiveness_model
        self.limit_price = limit_price
        self.theta = 0.5
        self.aggressiveness = 0
        self.transaction_prices = []
        self.alpha_min = 1000000000000000000
        self.alpha_max = -1000000000000000000
        
    def update_limit_price(self, limit_price):
        self.limit_price = limit_price

    def initialise_aggressiveness(self, aggressiveness):
        self.aggressiveness = aggressiveness
        
    def update_long_term(self, t_price, e_price):
        self.transaction_prices.append(t_price)
        if len(self.transaction_prices) >= self.WS:
            self.transaction_prices == self.transaction_prices[:self.WS]
        alpha = (sum([(x - e_price)**2 for x in self.transaction_prices]) / len(self.transaction_prices)) ** 0.5 / e_price)
        self.alpha_max = max(self.alpha_max, alpha)
        self.alpha_min = min(self.alpha_min, alpha)
        a = 0.5
        if self.alpha_max != self.alpha_min:
            a = (alpha - self.alpha_min) / (self.alpha_max - self.alpha_min)
        self.theta = self.theta + self.BETA2 * (((self.THETAMAX - self.THETAMIN) * (1.0 - a) * math.exp(self.GAMMA * (a - 1.0)) + self.THETAMIN) - self.theta)
    
    def update_short_term_from_inactivity(self, e_price):
        snapshot = self.agent.agent_status.last_snapshot     
        if snapshot == None:
            return False

        side = None
        if self.side == "Ask":
            side = "Bid"
        else:
            side = "Ask"
        if side.Depth == 0:
            return False
        best_price = side[0].Price

        if best_price == 0:
            return False
        
        desired_price = best_price
        current_target_price = self.aggressiveness_model.compute_tau(self.theta, self.aggressiveness, e_price)
        increase_profit_margin = False
        
        if self.side == "Bid":
            if desired_price > self.limit_price:
                desired_price = self.limit_price
            increase_profit_margin = desired_price < current_target_price
        else:
            if desired_price < self.limit_price:
                desired_price = self.limit_price
            increase_profit_margin = desired_price > current_target_price

        if increaseProfitMargin or self.agent.is_active:
            s = "REDUCING"
            if increase_profit_margin:
                s = "INCREASING"
            self.update_aggressiveness(increase_profit_margin, e_price, desired_price)
            return True
        
        return False

    
    def update_short_term(self, shout_stimulus, e_price):
        desired_target_price = -1
        current_target_price = self.aggressiveness_model.compute_tau(self.theta, self.aggressiveness, e_price)
        change_aggressiveness = False
        increase_aggressiveness = False          
        if (shout_stimulus.shout.accepted):
            change_aggressiveness = True
            p_t = shout_stimulus.last_trade.price;
            if (side == "Bid"):
                if (current_target_price < p_t)
                    increase_aggressiveness = True
            elif (side == "Ask"):
                if (current_target_price > pT):
                    increase_aggressiveness = True
            desired_target_price = p_t
        elif (side == "Bid" and shout_stimulus.shout.side == "Bid"):
            bid = shoutStimulus.Shout.Price
            if (current_target_price <= bid):
                change_aggressiveness = True
                increase_aggressiveness = True
                desired_target_price = bid
        elif (side == "Ask" && shout_stimulus.shout.side == "Ask"):
            ask = shout_timulus.shout.price
            if (current_target_price >= ask):
                change_aggressiveness = True
                increase_aggressiveness = True
                desired_target_price = ask
        if change_aggressiveness:
            update_aggressiveness(increase_aggressiveness, e_price, desired_target_price)

    def update_aggressiveness(self, inc_aggressiveness, e_price, desired_target_price):
        delta = 0
        r_shout = self.aggressiveness_model.compute_r_shout(self.theta, self.e_price, desired_target_price);

        if inc_aggressiveness:
            delta = (1.0 + self.LAMBDA_R) * r_shout + self.LAMBDA_A
        else:
            delta = (1.0 - self.LAMBDA_R) * r_shout - self.LAMBDA_A

        self.aggressiveness = self.aggressiveness + self.BETA1 * (delta - self.aggressiveness)
        
        
    
