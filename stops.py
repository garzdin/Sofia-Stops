from json import loads, dump
import re
import time
import requests
from pyproj import Proj, transform

stops = {}

types = [1, 2, 3]
line_ids = "https://www.sofiatraffic.bg/interactivecard/lines/{type}"
line_info = "https://www.sofiatraffic.bg/interactivecard/lines/stops/geo?line_id={line}"

coords_in_format = Proj(init='epsg:3857')
coords_out_format = Proj(init='epsg:4326')


class Stop(object):
	def __init__(self, name, coordinates):
		self.name = name
		self.coordinates = coordinates

	def json(self):
		return {
			'name': self.name,
			'coordinates': self.coordinates
		}


def get_line_stops(line):
	response = requests.get(line_info.format(line=line))
	data = response.json()

	if 'features' in data:
		for stop in data['features']:
			properties = stop['properties']
			code = properties['code']
			name = properties['name']
			geometry = stop['geometry']
			x, y = geometry['coordinates']
			x, y = float(x), float(y)
			x_new, y_new = transform(coords_in_format, coords_out_format, x, y)
			coordinates = {'y': y_new, 'x': x_new}
			stop = Stop(name, coordinates).json()
			stops[code] = stop


def get_stops():
	for t_type in types:
		response = requests.get(line_ids.format(type=t_type))
		html = response.text

		line_numbers = re.findall("[a-z0-9<\"\"\s]+value=\"([0-9]+)\">?", html)

		for line in line_numbers:
			if line != "-1":
				get_line_stops(line)

if __name__ == '__main__':
	print("Getting stops data ...")
	start_time = time.time()
	get_stops()
	with open('stops.json', 'w+') as f:
		dump(stops, f)
	print("Finished in %s seconds" % (time.time() - start_time))
