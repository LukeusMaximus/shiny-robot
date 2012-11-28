import math

class AdaptiveComponent:
    def __init__(self):
        self.GAMMA = 2.0
        self.THETA_MIN = -8.0
        self.THETA_MAX = 2.0
        self.BETA1 = 0.5
        self.BETA2 = 0.5
        self.LAMBDA_R = 0.05
        self.LAMBDA_A = 0.01
        self.WS = 30

        self.theta = 0.5
        self.limit_price = 500
        self.aggressiveness = 0
        self.transaction_prices = []
        self.alpha_min = 1000000000000000000
        self.alpha_max = -1000000000000000000

    def update_long_term(self, t_price, e_price):
        self.transaction_prices.append(t_price)
        if len(self.transaction_prices) >= self.WS:
            self.transaction_prices == self.transaction_prices[:self.WS]
        alpha = (sum([(x - e_price)**2 for x in self.transaction_prices]) / len(self.transaction_prices)) ** 0.5 / e_price
        self.alpha_max = max(self.alpha_max, alpha)
        self.alpha_min = min(self.alpha_min, alpha)
        a = 0.5
        if self.alpha_max != self.alpha_min:
            a = (alpha - self.alpha_min) / (self.alpha_max - self.alpha_min)
        self.theta = self.theta + self.BETA2 * (((self.THETAMAX - self.THETAMIN) * (1.0 - a) * math.exp(self.GAMMA * (a - 1.0)) + self.THETAMIN) - self.theta)

    def update_short_term(self, shoutStimulus, e_price, tau, side):
        desired_target_price = -1
        #double currentTargetPrice = _aggressivenessModel.ComputeTau(_theta, _aggressiveness, estimatedPrice);
        change_aggressiveness = False
        increase_aggressiveness = False          
        if (shoutStimulus.Shout.Accepted):
            change_aggressiveness = True
            p_t = shoutStimulus.LastTrade.Price;
            if (side == "bid"):
                if (tau < p_t):
                    increase_aggressiveness = True
            elif (side == "ask"):
                if (tau > pT):
                    increase_aggressiveness = True
            desired_target_price = p_t
        elif (side == "bid" and shoutStimulus.Shout.Side == "bid"):
            bid = shoutStimulus.Shout.Price
            if (tau <= bid):
                change_aggressiveness = True
                increase_aggressiveness = True
                desired_target_price = bid
        elif (side == "ask" and shoutStimulus.Shout.Side == "ask"):
            ask = shoutStimulus.Shout.Price
            if (tau >= ask):
                change_aggressiveness = True
                increase_aggressiveness = True
                desired_target_price = ask
        if change_aggressiveness:
            self.update_aggressiveness(increase_aggressiveness, e_price, desired_target_price)

    def update_aggressiveness(self, inc_aggressiveness, e_price, desired_tau, r_shout):
        delta = 0

        if inc_aggressiveness:
            delta = (1.0 + self.LAMBDA_R) * r_shout + self.LAMBDA_A
        else:
            delta = (1.0 - self.LAMBDA_R) * r_shout - self.LAMBDA_A

        self.aggressiveness = self.aggressiveness + self.BETA1 * (delta - self.aggressiveness)
