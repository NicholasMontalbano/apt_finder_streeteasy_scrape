import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
import re

# https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/#about
# https://apidocs.geoapify.com/playground/routing

class Routing():

    apt_csv = pd.read_csv('data/streeteasy.csv')
    apt_geos = apt_csv['geo']
    directions = []
    time = []
    lines = []

    def time_directions(self, apiKey, dest_geo, mode):

        for apt_geo in self.apt_geos:
            url = f'https://api.geoapify.com/v1/routing?waypoints={apt_geo}|{dest_geo}&mode={mode}&apiKey={apiKey}'

            headers = CaseInsensitiveDict()
            headers["Accept"] = "application/json"
            resp = requests.get(url, headers=headers)
            print(resp.status_code)

            self.time.append(round(int(resp.json()['features'][0]['properties']['time'])/60, 0))
        
            direction = ""
            line = ""
            for i in range(len(resp.json()['features'][0]['properties']['legs'][0]['steps'])):
                direction = direction + str(i+1) + ': ' + resp.json()['features'][0]['properties']['legs'][0]['steps'][i]['instruction']['text'] + ' '

            self.directions.append(direction)
            line = len(re.findall('stops', direction)) if re.findall('stops', direction) else 0
            self.lines.append(line)

    def run(self):
        apiKey = '[API KEY HERE]'
        mode = 'transit'

        dest_geos = {
            "work" : '40.712882,-74.00666',
            "friend" : '40.774929,-73.908508',
            }

        for key, value in dest_geos.items():
            self.directions = []
            self.time = []
            self.lines = []
            dest_geo = value
            self.time_directions(apiKey, dest_geo, mode)
            #print(self.time, self.directions)
            self.apt_csv[f'{key}_time'] = self.time
            self.apt_csv[f'{key}_directions'] = self.directions
            self.apt_csv[f'{key}_lines'] = self.lines

        self.apt_csv.to_csv('data/apt_csv.csv', index=False)


if __name__ == '__main__':
    scraper = Routing()
    scraper.run()