import json
import requests
import urllib.parse

import os
from dotenv import load_dotenv

import pandas as pd

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
ENDPOINT = 'https://maps.googleapis.com/maps/api/geocode/json'


class GeocodingClient():
    def __init__(self, api_key=GOOGLE_API_KEY):
        self.key = api_key
        self.endpoint = ENDPOINT
        self.lat_list = []
        self.lng_list = []

    def get_geocode(self, url):
        r = requests.get(url)
        if r.status_code not in range(200, 300):
            print(r.status_code)
            pass
        else:
            response = r.json()
            return response

    def parse_url(self, address):
        params = {
            'address': address,
            'key': self.key,
        }
        enc_params = urllib.parse.urlencode(params)
        url = self.endpoint + '?' + enc_params
        return url

    def read_response(self, response):
        lat = response['results'][0]['geometry']['location']['lat']
        lng = response['results'][0]['geometry']['location']['lng']
        return lat, lng

    def add_coordinates(self, lat, lng):
        self.lat_list.append(lat)
        self.lng_list.append(lng)
        pass


geocoder = GeocodingClient()
schools_df = pd.read_csv('../data_raw/schools.csv')


for idx, address in enumerate(schools_df.Address):
    print(idx, end=' ')
    url = geocoder.parse_url(address)
    response = geocoder.get_geocode(url)
    lat, lng = geocoder.read_response(response)
    geocoder.add_coordinates(lat, lng)

schools_df['latitude'] = geocoder.lat_list
schools_df['longitude'] = geocoder.lng_list

schools_df.to_csv('../data_raw/coordinates.csv')
