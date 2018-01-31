class Value:
    def __init__(self):
        self.value = None

    def __set__(self, instance, value):
        self.value = value - value * instance.commission

    def __get__(self, instance, value):
        return self.value

    def __delete__(self, instance):
        print("delete value obj")


class Account:
    amount = Value()

    def __init__(self, commission):
        self.commission = commission



new_account = Account(0.5)
new_account.amount = 100

print(new_account.amount)