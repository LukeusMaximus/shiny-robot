import math

class AggressivenessModel:
    def __init__(self, agent, limit_price, side, pmax):
        self.agent = agent
        self.limit_price = limit_price
        self.side = side
        self.pmax = pmax
        self.tau = None
        if side == 'Bid':
            self.inner_compute_tau = inner_compute_tau_buyer
        else:
            self.inner_compute_tau = inner_compute_tau_seller

        self.newton_solver = NewtonSolver()


    def update_limit_price(self, p):
        self.limit_price = p

    def compute_tau(self, theta, r, estimated_price):
        self.tau = self.inner_compute_tau(theta, r, estimated_price)
        return self.tau

    def compute_r_shout(self, theta, estimated_price, pi):
        is_intra_marginal = self.is_intra_marginal(estimated_price)
        rshout = None

        if self.side == 'Bid':
            if pi > self.limit_price:
                rshout = 0.0
            elif is_intra_marginal:
                rshout = self.inner_compute_r_shout_intra_marginal_buyer(pi, theta, estimated_price)
            else:
                rshout = self.inner_compute_r_shout_extra_marginal_buyer(pi, theta)
        else:
            if pi < self.limit_price:
                rshout = 0.0
            elif is_intra_marginal:
                rshout = self.inner_compute_r_shout_intra_marginal_seller(pi, theta, estimated_price)
            else:
                rshout = self.inner_compute_r_shout_extra_marginal_seller(pi, theta)
        return rshout

    def is_intra_marginal(self, estimated_price):
        return self.side == 'Bid' and (self.limit_price > estimated_price)\
               or self.side == 'Ask' and (self.limit_price < estimated_price)


    def inner_compute_r_shout_intra_marginal_buyer(self, pi, theta,estimated_price):
        rshout = None

        if (0.0 <= pi and pi < estimated_price):
            theta_bar = self.compute_theta_bar_buyer(estimated_price, theta)
            if theta_bar != 0:
                rshout = -(1.0/theta_bar) * math.log(((pi-estimated_price)/(self.limit_price - estimated_price)) * (math.exp(theta)-1.0) + 1.0)
            else:
                rshout = (pi - estimated_price) / (self.limit_price - estimated_price)
        elif (estimated_price <= pi and pi <= self.limit_price):
            if theta != 0:
                rshout = (1.0 / theta) * math.log(((pi - estimated_price) / (self.limit_price - self.estimated_price)) * (math.exp(theta) - 1.0) + 1.0)
            else:
                rshout = (pi - estimated_price) / (self.limit_price - estimated_price)

        return rshout


    def inner_compute_r_shout_extra_marginal_buyer(self, pi, theta):
        rshout = None

        if (0 <= pi and pi < self.limit_price):
            if (theta != 0):
                rshout = -(1.0 / theta) * math.log(((pi - self.limit_price) / self.limit_price) * (1.0 - math.exp(theta)) + 1.0);
            else:
                rshout = (pi - self.limit_price)/self.limit_price

        return rshout


    def inner_compute_r_shout_intra_marginal_seller(self, pi, theta, estimated_price):
        rshout = None

        if (estimated_price < pi and pi <= self.PMAX):
            theta_bar = self.compute_theta_bar_seller(estimated_price, theta)
            pass

