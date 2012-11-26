class NewtonSolver:
    def __init__(self, precision, steps):
        self.precision = precision
        self.steps = steps
    def solve(self, f, f1, start):
        x = startPoint
        delta = self.precision
        i = 0
        while i < self.steps and abs(delta) >= self.precision:
            delta = f(x) / f1(x)
            x -= delta
        return x
