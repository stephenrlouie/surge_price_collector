import json
import os 
import time
import configparser
from uber_rides.client import UberRidesClient
from uber_rides.session import Session

CONFIG_NAME = 'config.ini'
LOCATION_NAME = 'locations.ini'
CITIES_LIST = ['BOSTON', 'SAN_FRAN']

def get_prices(start_lat, start_lng, end_lat, end_lng):
    response = client.get_price_estimates(start_lat, start_lng, end_lat, end_lng)
    cars = []
    surges = []
    
    # assert response looks like price estimates
    jresponse = response.json
    for prod in jresponse['prices']:
        cars.append(prod['localized_display_name'])
        surges.append(prod['surge_multiplier'])
    return cars, surges


def load_location_data(city_name):
    location_config = configparser.ConfigParser()
    location_config.read(LOCATION_NAME)
    names = location_config.get(city_name, 'names').split(",")
    start_lats = location_config.get(city_name, 'start_lats').split(",")
    start_lngs = location_config.get(city_name, 'start_lngs').split(",")
    end_lats = location_config.get(city_name, 'end_lats').split(",")
    end_lngs = location_config.get(city_name, 'end_lngs').split(",")
    time_zone = location_config.get(city_name, 'time_zone')
    return names, start_lats, start_lngs, end_lats, end_lngs, time_zone


def get_local_time(time_zone):
    os.environ['TZ'] = time_zone
    time.tzset()
    return time.strftime("%d-%m-%y %H:%M")

config = configparser.ConfigParser()
config.read(CONFIG_NAME)
SERVER_TOKEN = config.get('UBER','server_token')

session = Session(server_token=SERVER_TOKEN)
client = UberRidesClient(session)

for city in CITIES_LIST:
    names, start_lats, start_lngs, end_lats, end_lngs, time_zone = load_location_data(city)
    localt = get_local_time(time_zone) 
    print "------"
    print city
    print localt
    for index in range(len(names)):
        print "-----"
        print names[index] 
        cars, surges = get_prices(start_lats[index], start_lngs[index], end_lats[index], end_lngs[index])
        print cars
        print surges
