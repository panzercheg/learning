import csv
import os
from collections import OrderedDict


class CarBase:
    def __init__(self, brand, photo_file_name, carrying=None):
        self.brand=brand
        self.photo_file_name = photo_file_name

    def get_photo_file_ext(self):
        filename, file_ext = os.path.splitext(self.photo_file_name)
        return file_ext


class Car(CarBase):
    def __init__(self, brand, photo_file_name, carrying=None, passenger_seats_count=None):
        pass


class Truck(CarBase):
    def __init__(self, brand, photo_file_name, carrying, body_whl):
        super().photo_file_name
        self.body_whl = body_whl.split("x")
        pass


class SpecMachine(CarBase):
    def __init__(self, brand, photo_file_name=None, carrying=None, extra=None):
        super().photo_file_name
        pass


def get_car_list(csv_filename):
    mapping = {'car': Car,
               'truck': Truck,
               'specmachine': SpecMachine}

    reader = csv.DictReader(open(csv_filename), delimiter=';')
    row_struct = [_ for _ in reader]
    ordered = OrderedDict()
    for row in row_struct:
        print(row)
        # row = mapping.get(_.get('car_type'))(_)



    # with open(csv_filename) as csv_fd:
    #     reader = csv.reader(csv_fd, delimiter=';')
    #     next(reader)
    #     for row in reader:
    #         print(row)
        # car_list = []
        # return car_list


def main():
    getter = CarBase("Lamborgini", "00041.MTS")
    print(getter.get_photo_file_ext())
    print(get_car_list("F:\python3\coursera_week3_cars.csv"))



if __name__ == "__main__":
    main()