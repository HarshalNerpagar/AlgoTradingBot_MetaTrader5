
def true_range(current_high, current_low, previous_close=0):  # previous close = 0 if no prior data
    return max(abs(current_high - current_low),
               abs(current_high - previous_close),
               abs(current_low - previous_close))


class ATR:

    def __init__(self):
        self.true_range_history = []
        self.prior_ATR = -1  # -1 not possible, represents nonexistence of ATR
        self.periods = 14

    def current_ATR(self, current_true_range):
        if len(self.true_range_history) < self.periods:  # until required number of periods has been met
            self.true_range_history.append(current_true_range)  # store true ranges
            current_ATR = -1  # return -1 to show that no ATR could be calculated

        elif self.prior_ATR == -1:  # required number of periods met, no prior ATR
            current_ATR = sum(self.true_range_history) / self.periods

        else:  # required number of periods met, prior ATR
            current_ATR = ((self.prior_ATR * (self.periods - 1)) + current_true_range) / self.periods

        self.prior_ATR = current_ATR
        return current_ATR




ATR_object = ATR()

