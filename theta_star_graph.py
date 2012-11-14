import aa
from bristol_stock_exchange import BSE

from matplotlib import pyplot as plt


if __name__ == "__main__":
    scale_factor = 100.0
    aab = aa.AABuyer()
    aab.update_limit_price(4)

    upper = aa.ALPHA_MAX * scale_factor
    lower = aa.ALPHA_MIN * scale_factor
    print upper
    print lower
    upper = int(upper)
    lower = int(lower)

    xs = [x/scale_factor for x in xrange(lower,upper)]
    ys = [aab.theta_star(x) for x in xs]

    plt.plot(xs, ys)
    plt.show()


