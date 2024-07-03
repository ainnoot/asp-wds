"""
Maps available network into facts.
"""

from argparse import ArgumentParser
import geopandas as gpd
from math import ceil

def parse_args():
    p = ArgumentParser()
    p.add_argument('snaps', type=str, help="Input GeoJSON file storing information about spatial join between nodes, tanks and road network intersections.")
    p.add_argument('links', type=str, help="Input GeoJSON file storing information about road network links.")
    p.add_argument('intersections', type=str, help="Input GeoJSON file storing information about road network intersections.")
    p.add_argument('tanks', type=str, help="Input GeoJSON file storing tanks' coordinates and elevation data.")
    p.add_argument('logic_program', type=str, help="Output file storing the set of facts for this WDS reconstruction problem instance.")
    p.add_argument('--crs', type=str, default="EPSG:4326", help="Coordinate reference system used to read the GeoJSON files.")
    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    snaps_path = args.snaps
    links_path = args.links
    tanks_path = args.tanks
    intersections_path = args.intersections
    lpout = args.logic_program

    links = gpd.read_file(links_path, geometry='geometry', crs=args.crs)
    snaps = gpd.read_file(snaps_path, geometry='geometry', crs=args.crs)
    tanks = gpd.read_file(tanks_path, geometry='geometry', crs=args.crs)
    intersections = gpd.read_file(intersections_path, geometry='geometry', crs=args.crs)

    with open(lpout, 'w') as instance:
        for _, row in links.iterrows():
            # print("edge({},{},{},{}).".format(row['u'], row['v'], row['key'], ceil(row['length'])), file=instance)
            print("edge({},{},{}).".format(row['u'], row['v'], row['key']), file=instance)
            if ';' in row['highway']:
                row['highway'] = '(' + row['highway'] + ')'
            print("highway({},{},{},{}).".format(row['u'], row['v'], row['key'], row['highway']), file=instance)

        for _, row in snaps.iterrows():
            print("snaps_to(\"{}\",{}).".format(row['id'], row['osmid']), file=instance)

        for _, row in tanks.iterrows():
            print("is_tank(\"{}\").".format(row['id']), file=instance)
            print("height(\"{}\",{}).".format(row['id'], ceil(row['elevation'])), file=instance)

        for _, row in intersections.iterrows():
            print("height({},{}).".format(row['osmid'], ceil(row['elevation'])), file=instance)
