import requests
from dateutil.parser import parse
import pprint
import argparse


class YahooWeatherForecast:
    def __init__(self):
        self._city_cache = {}

    def get(self, city):
        if city in self._city_cache:
            return self._city_cache[city]
        url = f"https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather." \
              f"forecast%20where%20woeid%20in%20(select%20woeid%20from%20geo." \
              f"places(1)%20where%20text%3D%22{city}%22)%20and%20u%3D%22c%22&format=json&" \
              f"env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys"
        print("Sending HTTP request")
        data = requests.get(url).json()
        city_data = data["query"]["results"]["channel"]["item"]["title"]
        print(city_data)
        forecast_data = data["query"]["results"]["channel"]["item"]["forecast"]
        forecast = []
        for day_data in forecast_data:
            forecast.append({
                "date": parse(day_data["date"]),
                "high_temp": day_data["high"],
                "low_temp": day_data["low"],
                "weather_text": day_data["text"]
            })
        self._city_cache[city] = forecast
        return forecast


class CityInfo:

    def __init__(self, city, weather_forecast=None):
        self.city = city
        self._weather_forecast = weather_forecast or YahooWeatherForecast()

    def weather_forecast(self):
        return self._weather_forecast.get(self.city)


def _main():
    weather_forecast = YahooWeatherForecast()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--city', action='store', dest='weather_city', help='city for get weather', default="Moscow")
    options = parser.parse_args()
    city_weather = options.weather_city
    city_info = CityInfo(city_weather, weather_forecast=weather_forecast)
    forecast = city_info.weather_forecast()
    pprint.pprint(forecast)


if __name__ == "__main__":
    _main()
