from Domain.Discounts.Discount import Discount


class ImmediateDiscount(Discount):

    def __init__(self, percent, time, double, description):
        super(ImmediateDiscount, self).__init__(percent, time, double, description)

    def apply_discount(self, price):
        if self.time > 0:
            return price * (1 - self.percent)
        return price
