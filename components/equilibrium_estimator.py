from random import random

class EquilibriumEstimator:
    def __init__(self, agent):
        self.agent = agent
        self.window_size = agent.window_size
        self.rho = agent.rho
        self.prices = []
        self.estimated_price = None
        self.initial_price_guess_percentage_around_mid = 0.35


    def add_new_transaction(self, price):
        self.prices.append(price)
        if len(self.prices) > self.window_size:
            self.prices = self.prcies[1:]
            assert len(self.prices) <= self.window_size

        w = 1.0
        w_sum = 0
        price_sum = 0
        for p in self.prices:
            price_sum += p * w
            w_sum += w
            w *= self.rho

        self.estimated_price = price_sum/w_sum

    def reset(self):
        self.prices = []
        a = self.agent.agent_status.current_instrument.minprice
        b = self.agent.agent_status.current_instrument.maxprice
        p_min = a + 0.5 * (b - a) * (1.0 - self.initial_price_guess_percentage_around_mid)
        self.estimatedPrice = p_min + random() * (b - a) * self.initial_price_guess_percentage_around_mid

        total_ticks = int(self.estimatedPrice / self.agent.agent_status.current_instrument.price_tick)
        self.estimated_price = float(total_ticks) * self.agent.agent_status.current_instrument.price_tick

