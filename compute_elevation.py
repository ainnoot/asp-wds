from argparse import ArgumentParser
import geopandas as gpd
from maps_api_wrapper.geocoder import MapsAPI
from maps_api_wrapper.model import GeocodeResponse, ElevationResponse, Location
import sys

def parse_args():
	p = ArgumentParser()
	p.add_argument('intersections', type=str, help="Input GeoJSON file storing road network intersection data.")

	return p.parse_args()

if __name__ == '__main__':
	args = parse_args()
	intersections_path = args.intersections
	intersections = gpd.read_file(
		intersections_path
	)

	maps = MapsAPI()

	points = intersections['geometry']
	locations = [Location(p.y, p.x) for p in tuple(points)]

	points_elevation = maps.elevation(locations)

	intersections['elevation'] = [x.elevation for x in points_elevation]
	intersections.to_file(intersections_path)
