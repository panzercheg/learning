import requests
import datetime
import dateutil
import pprint

class CityInfo:

    def __init__(self, city):
        self.city = city

    def weather_forecast(self):
        pass



def _main():
    city_info = CityInfo("Moscow")
    forecast = city_info.weather_forecast()
    pprint.pprint(forecast)

if __name__ == "__main__":
    _main()
