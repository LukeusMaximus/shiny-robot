from bristol_stock_exchange import BSE
import copy

class RoundRobinBuffer:
    def __init__(self, window_size):
        self.buffer = []
        self.window_size = window_size

    def append(self, hash):
        c = copy.copy(hash)
        if not c.has_key("age"):
            c["age"] = 0
        self.buffer.append(c)

    def age_buffer(self):
        removal = []
        for hash in self.buffer:
            hash["age"] += 1
            if hash["age"] > self.window_size:
                removal.append(hash)

        for hash in removal:
            self.buffer.remove(hash)

    def __getitem__(self, index):
        return self.buffer[index]

    def __len__(self):
        return len(self.buffer)


class MGD(BSE.Trader):
    WINDOW_SIZE = 10

    def __init__(self,ttype,tid,balance):
        BSE.Trader.__init__(self,ttype, tid, balance)
        self.accepted_asks_history = RoundRobinBuffer(self.WINDOW_SIZE)
        self.bids_history = RoundRobinBuffer(self.WINDOW_SIZE)
        self.asks_history = RoundRobinBuffer(self.WINDOW_SIZE)
        self.previous_lob = {"bids":{"lob":[]}, "asks":{"lob":[]}}


    def update_bids(self, lob):
        old_bids = self.previous_lob["bids"]["lob"]
        new_bids = lob["bids"]["lob"]
        diff = [x for x in new_bids if x not in old_bids]
        self.age_bids()
        for bid in diff:
            self.bids_history.append({"price":bid[0],
                                      "quantity":bid[1],
                                     })

    def update_asks(self,lob,trade):
        old_asks = self.previous_lob["asks"]["lob"]
        new_asks = lob["asks"]["lob"]
        diff = [x for x in new_asks if x not in old_asks]
        if trade != None:
            diff.remove([trade["price"], trade["quantity"]])

        self.age_asks()
        for ask in diff:
            self.asks_history.append({"price":ask[0], "quantity":ask[1]})

        self.accepted_ask_history.append({"price":trade[0], "quantity":trade[1]})

    def progress_lob(self, lob):
        self.previous_lob = lob

    def respond(self, time, lob, trade, verbose):
        self.update_bids(lob)
        self.update_asks(lob, trade)
        self.progress_lob(lob)

    def age_bids(self):
        self.bids_history.age_buffer()

    def age_asks(self):
        self.asks_history.age_buffer()
        self.accepted_asks_history.age_buffer()
