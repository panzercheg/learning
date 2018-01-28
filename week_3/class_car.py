import csv
import os


class CarBase:
    def __init__(self, brand, photo_file_name, carrying=None):
        self.brand=brand
        self.photo_file_name = photo_file_name

    def get_photo_file_ext(self):
        filename, file_ext = os.path.splitext(self.photo_file_name)
        return file_ext


class Car(CarBase):
    def __init__(self, brand, photo_file_name, carrying, passenger_seats_count):
        self.brand = brand
        self.photo_file_name = photo_file_name
        self.carrying = carrying
        self.passenger_seats_count = passenger_seats_count
        pass


class Truck(CarBase):
    def __init__(self, brand=None, photo_file_name=None, carrying=None, body_whl=None):
        self.photo_file_name = photo_file_name
        # self.body_whl = body_whl.split("x")
        pass


class SpecMachine(CarBase):
    def __init__(self, brand, photo_file_name=None, carrying=None, extra=None):
        super().photo_file_name
        pass


def get_car_list(csv_filename):
    mapping = {
               'truck': Truck,
               'specmachine': SpecMachine}

    inp = csv.DictReader(open(csv_filename), delimiter=';')
    res = [_ for _ in inp]

    for _ in res:
        tt = mapping.get(_.get('car_type'), Truck)(_)
        print(tt)
    # reader = csv.DictReader(open(csv_filename), delimiter=';')
    # row_struct = [_ for _ in reader]
    # for row in row_struct:
    #     print(row)


def main():
    getter = CarBase("Lamborgini", "00041.MTS")
    print(getter.get_photo_file_ext())
    print(get_car_list("F:\python3\coursera_week3_cars.csv"))


if __name__ == "__main__":
    main()