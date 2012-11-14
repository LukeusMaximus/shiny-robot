import aa
from bristol_stock_exchange import BSE

from matplotlib import pyplot as plt
import random


if __name__ == "__main__":
    scale_factor = 100.0
    doas =[]
    aab = aa.AABuyer()
    aab.tau = 190
    for i in range(0,100):
        aab.short_term_learning(None, {"price":185})
        doas.append(aab.doa)


    plt.plot(xrange(0,100), doas)
    plt.show()


