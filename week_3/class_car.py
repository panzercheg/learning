import csv
import os


class CarBase:
    def __init__(self, brand, photo_file_name, carrying=None):
        self.brand=brand
        self.photo_file_name = photo_file_name

    def get_photo_file_ext(self):
        filename, file_ext = os.path.splitext(self.photo_file_name)
        # for files in os.walk(self.photo_file_name):
        return filename, file_ext


class Car(CarBase):
    def __init__(self, brand, photo_file_name, carrying, passenger_seats_count):
        pass


class Truck(CarBase):
    def __init__(self, brand, photo_file_name, carrying, body_whl):
        pass


class SpecMachine(CarBase):
    def __init__(self, brand, photo_file_name, carrying, extra):
        pass


def get_car_list(csv_filename):

    with open(csv_filename) as csv_fd:
        reader = csv.reader(csv_fd, delimiter=';')
        next(reader)
        for row in reader:
            print(row)
        # car_list = []
        # return car_list


def main():
    getter = CarBase("Lamborgini", "N:\Фотографии\00041.MTS")
    print(getter.get_photo_file_ext())
    print(get_car_list("F:\python3\coursera_week3_cars.csv"))



if __name__ == "__main__":
    main()