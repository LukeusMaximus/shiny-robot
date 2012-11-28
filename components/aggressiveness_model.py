import math


class AggressivenessModel:
    def __init__(self, agent, limit_price, side, pmax):
        self.agent = agent
        self.limit_price = limit_price
        self.side = side
        self.pmax = pmax
        self.tau = None
        if side == 'Bid':
            self.inner_compute_tau = self.inner_compute_tau_buyer
        else:
            self.inner_compute_tau = self.inner_compute_tau_seller

        self.newton_solver = NewtonSolver()
        self.last_a = None
        self.last_soultion = None


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
            if theta_bar != 0:
                rshout = -(1.0 / theta_bar) * math.log(((pi - estimated_price) / (self.PMAX - estimated_price)) * (math.exp(theta_bar) - 1.0) + 1.0)
            else:
                rshout = (pi - estimated_price) / (estimated_price - self.PMAX)
        elif (self.limit_price <= pi and pi <= estimated_price):
            if (theta != 0):
                rshout = (1.0 / theta) * math.log(((pi - estimated_price) / (estimated_price - self.limit_price)) * (1.0 - math.exp(theta)) + 1.0)

            else:
                rshout = (estimated_price - pi) / (estimated_price - self.limit_price)

        return rshout

    def inner_compute_r_shout_extra_marginal_seller(self, pi, theta):
        if (self.limit_price <= pi and pi <= self.PMAX):
            if theta != 0:
                rshout = -(1.0 / theta) * math.log(((pi - self.limit_price) / (self.PMAX - self.limit_price)) * (math.exp(theta) - 1.0) + 1.0)
            else:
                rshout = (self.limit_price - pi) / (self.PMAX - self.limit_price);

        return rshout

    def inner_compute_tau_buyer(self, theta, r, estimated_price):
        tau = 0.0
        intra_marginal = self.limit_price > estimated_price

        if abs(r) > 1:
            r1 = -1 if r < 0 else 1
            r = r1

        if r >= -1.0 and r < 0.0:
            if intra_marginal:
                theta_buyer = self.compute_theta_buyer(estimated_price, theta)
                tau = estimated_price * (1.0 - ((math.exp(-r * theta_buyer) - 1.0) / (math.exp(theta_buyer) - 1.0)))
            else:
                tau = self.limit_price * (1.0 - ((math.exp(-r * theta) - 1.0) / (math.exp(theta) - 1.0)))
        elif (r > 0.0 and r < 1.0):
            if intra_marginal:
                tau = estimated_price + (self.limit_price - estimated_price) * ((math.exp(r * theta) - 1.0) / (math.exp(theta) - 1.0))
            else:
                tau = self.limit_price

        return tau


    def inner_compute_tau_seller(self, theta, r, estimated_price):
        tau = 0.0
        intra_marginal = self.limit_price < estimated_price

        if (abs(r) > 1):
            r1 = -1 if r < 0 else 1
            r = r1

        if r >= -1.0 and r < 0.0:
            if intra_marginal:
                theta_seller = self.compute_theta_seller(estimated_price, theta)
                tau = estimated_price + (self.PMAX - estimated_price) * ((math.exp(-r * theta_seller) - 1.0) / (math.exp(theta_seller) - 1.0))
            else:
                tau = self.limit_price + (self.PMAX - self.limit_price) * ((math.exp(-r * theta) - 1.0) / (math.exp(theta) - 1.0))
        elif (r > 0.0 and r < 1.0):
            if (intra_marginal):
                tau = self.limit_price + (estimated_price - self.limit_price) * (1.0 - ((math.exp(r * theta) - 1.0) / (math.exp(theta) - 1.0)))
            else:
                tau = self.limit_price

        return tau

    def compute_theta_bar_seller(self, estimated_price, theta):
        if (theta != 0):
            self.current_a = ((estimated_price - self.PMAX) / (self.estimated_Price - self.limit_price)) * (1.0 - math.exp(theta)) / theta
        else:
            self.current_a = (estimated_price - self.PMAX) / estimated_price

        return self.compute_theta_bar()

    def compute_thete_bar_buyer(self, estimated_price, theta):
        if theta != 0:
            self.current_a = (estimated_price / (self.limit_price - estimated_price)) * (math.exp(theta) - 1.0) / theta
        else:
            self.current_a = estimated_price / (self.limit_price - estimated_price)

        return self.compute_theta_bar()


    def f(theta):
        return math.exp(theta)-self.current_a * theta - 1.0

    def compute_theta_bar(self):
        solution = None
        epsilon = 1.0

        if self.last_a is not None and self.last_solution is not None:
            solution = self.last_solution
        else:
            if self.current_a < 0.0 or self.current_a == 1.0:
                solution = 0.0
            else:
                starting_point = math.log(self.current_a)
                if (0.0 < self.current_a and self.current_a <= 1):
                    starting_point -= epsilon
                else:
                    starting_point += epsilon

                solution = self.newton_solver.solve(self.f, self.f1, starting_point)

        self.last_a = self.current_a
        self.last_solution = solution
        return solution



