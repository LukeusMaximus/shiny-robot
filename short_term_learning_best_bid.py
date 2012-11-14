import aa
from bristol_stock_exchange import BSE

from matplotlib import pyplot as plt


if __name__ == "__main__":
    scale_factor = 100.0
    aab = aa.AABuyer()
    aab.update_limit_price(4)
    doas = []
    for i in xrange(0,100):
        aab.short_term_learning(185, None)
        doas.append()

    plt.plot(xrange(0,100), doas)
    plt.show()



