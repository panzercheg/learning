tmp1 = {"k1": "",
        "k2": "",
        "k3": ""
        }

string_word = "8x6.7x2.5"
split_word = string_word.split("x")
truck_key = ("body_length", "body_width", "body_height")
# truck_dict = dict(zip(truck_key, split_word))
tmp1["k1"]=split_word[0]
tmp1["k2"]=split_word[1]
tmp1["k3"]=split_word[2]
print(tmp1)
# print("body_height is {}".format(truck_dict.get('body_height')))


def __init__(self, start, end):
        self.current = start
        self.end = end


def __iter__(self):
        return self


def __next__(self):
        if self.current >= self.end:
                raise StopIteration

        result = self.current ** 2
        self.current += 1
        return result