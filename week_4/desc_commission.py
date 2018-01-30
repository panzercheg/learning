class Value:
    def __init__(self):
        self.value = None

    def __set__(self, commission, value):
        self.value = value - value * 0.5

    def __get__(self, commission, value):
        return self.value

    def __delete__(self, commission):
        print("delete value obj")


class Account:
    amount = Value()

    def __init__(self, commission):
        self.commission = commission


new_account = Account(0.1)
new_account.amount = 100

print(new_account.amount)