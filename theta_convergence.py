import aa
from bristol_stock_exchange import BSE

from matplotlib import pyplot as plt
import random


if __name__ == "__main__":
    scale_factor = 100.0
    thetas =[]
    aab = aa.AABuyer()
    for i in range(0,100):
        aab.long_term_learning(185+random.random()*3.4)
        thetas.append(aab.theta)


    plt.plot(xrange(0,100), thetas)
    plt.show()

