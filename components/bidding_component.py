class BiddingComponent:
    def __init__(self, side, limit_price, Instrument instrument):

        self.limit_price = self.limit_price          
        self.first_trading_round = True
        self.current_instrument = instrument

        self.eta = 3
        self.max_spread = 1
        self.LAMBDA_R = 0.05
        self.LAMBDA_A = 0.01
        
        self.best_bid = 0
        self.best_ask = 0

        if (side == "bid")
        {
            InnerPrice = InnerPriceBuyer;
        }
        else
        {
            InnerPrice = InnerPriceSeller;
        }


    #public bool IsFirstTradingRound { get { return _isFirstTradingRound; } set { _isFirstTradingRound = value; } }

    def update_best_prices(best_bid, best_ask):
        if (best_bid == 0.0):
            best_bid = self.current_instrument.MinPrice
        if (best_ask == 0.0):
            best_ask = self.current_instrument.MaxPrice

        self.best_bid = best_bid
        self.best_ask = best_ask

    public double Price(double tau, out bool success)
    {
        if (!_isFirstTradingRound && double.IsNaN(tau))
        {
            success = false;
            return double.NaN;                
        }

        double price = InnerPrice(tau, out success);
        int ticksInPrice = (int)(price / _currentInstrument.PriceTick);
        return (double)ticksInPrice * _currentInstrument.PriceTick;            
    }
    
    private double InnerPriceBuyer(double tau, out bool success)
    {
        double price = 0.0;
        success = false;
        
        if (_limitPrice <= _bestBid)
        {
            success = true;
            price = _limitPrice;
        }
        else if (_limitPrice >= _bestAsk && ((_bestAsk - _bestBid) <= MaxSpread))
        {
            success = true;
            price = _bestAsk;
        }
        else if (_limitPrice > _bestBid)
        {
            success = true;
            if (_isFirstTradingRound)
            {
                double bestAskPlus = (1.0 + LambdaRelative) * _bestAsk + LambdaAbsolute;
                price = _bestBid + (Math.Min(_limitPrice, bestAskPlus) - _bestBid) / Eta;
            }
            else
            {
                if (_bestAsk <= tau)
                {
                    price = _bestAsk;
                }
                else
                {
                    price = _bestBid + (tau - _bestBid) / Eta;
                }
            }
        }           

        return price;
    }

    private double InnerPriceSeller(double tau, out bool success)
    {
        double price = 0.0;
        success = false;

        if (_limitPrice >= _bestAsk)
        {
            success = true;
            price = _limitPrice;
        }
        else if (_limitPrice <= _bestBid && ((_bestAsk - _bestBid) <= MaxSpread))
        {
            success = true;
            price = _bestBid;
        }
        else if (_limitPrice < _bestAsk)
        {
            success = true;
            if (_isFirstTradingRound)
            {
                double bestBidMinus = (1.0 - LambdaRelative) * _bestBid - LambdaAbsolute;
                price = _bestAsk - (_bestAsk - Math.Max(_limitPrice, bestBidMinus)) / Eta;
                _isFirstTradingRound = false;
            }
            else
            {
                if (_bestBid >= tau)
                {
                    price = _bestBid;
                }
                else
                {
                    price = _bestAsk - (_bestAsk - tau) / Eta;
                }
            }
        }           

        return price;
    }
