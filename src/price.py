import json
import os 
import time
import configparser
import pymongo
from uber_rides.client import UberRidesClient
from uber_rides.session import Session

CONFIG_NAME = 'config.ini'
LOCATION_NAME = 'locations.ini'
CITIES_LIST = ['BOSTON', 'SAN_FRAN', 'NEW_YORK']

def get_prices(start_lat, start_lng, end_lat, end_lng):
    cars = []
    surges = []
    #try:
    response = client.get_price_estimates(start_lat, start_lng, end_lat, end_lng)
    # assert response looks like price estimates
    jresponse = response.json
    for prod in jresponse['prices']:
        cars.append(prod['localized_display_name'])
        surges.append(prod['surge_multiplier'])
    return cars, surges
    #except:
    #    return cars,surges

def listify_config(string):
    return string.replace(' ','').split(",")


def load_location_data(city_name):
    location_config = configparser.ConfigParser()
    location_config.read(LOCATION_NAME)
    names = location_config.get(city_name, 'names').split(",")
    start_lats = listify_config(location_config.get(city_name, 'start_lats'))
    start_lngs = listify_config(location_config.get(city_name, 'start_lngs'))
    end_lats = listify_config(location_config.get(city_name, 'end_lats'))
    end_lngs = listify_config(location_config.get(city_name, 'end_lngs'))
    time_zone = location_config.get(city_name, 'time_zone')
    return names, start_lats, start_lngs, end_lats, end_lngs, time_zone


def get_local_time(time_zone):
    os.environ['TZ'] = time_zone
    time.tzset()
    dayIndex = time.strftime("%w")
    date = time.strftime("%d")
    month = time.strftime("%m")
    year = time.strftime("%Y")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    return dayIndex, date, month, year, hour, minute

def connect_to_mongo():
    try:
        return pymongo.MongoClient()
    except:
        print("Could not connect to mongo")

def connect_to_db(mongo_client, name):
    try:
        return mongo_client[name]
    except: print("Could not connect to db name")

def disconnect_from_mongo(mongo_client):
    mongo_client.close()


mongo_client = connect_to_mongo()
mongo = connect_to_db(mongo_client, "uber")

config = configparser.ConfigParser()
config.read(CONFIG_NAME)
SERVER_TOKEN = config.get('UBER','server_token')

session = Session(server_token=SERVER_TOKEN)
client = UberRidesClient(session)

for city in CITIES_LIST:
    names, start_lats, start_lngs, end_lats, end_lngs, time_zone = load_location_data(city)
    dayIndex, date, month, year, hour, minute = get_local_time(time_zone) 
    for index in range(len(names)):
        cars, surges = get_prices(start_lats[index], start_lngs[index], end_lats[index], end_lngs[index])
        entry = {'city': city, 'name': names[index],'cars': cars, 'surge': surges, 'dayIndex': dayIndex, 'date': date, 'month': month, 'year': year, 'hour': hour, 'minute': minute} 
        mongo.surge.insert_one(entry)

disconnect_from_mongo(mongo_client)
