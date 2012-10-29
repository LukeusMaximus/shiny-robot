import aa
from bristol_stock_exchange import BSE
from matplotlib import pyplot as plt


if __name__ == "__main__":

    aab = aa.AABuyer()
    aab.update_limit_price(4)

    aas = aa.AASeller()
    aas.update_limit_price(2)

    xs = [x/100.0 for x in xrange(-100,100)]
    ys = [aas.aggressiveness_model(4, x, 3) for x in xs]

    plt.plot(xs, ys)
    plt.show()


