"""
Extracts road graph from the convex hull of some coordinates.
"""

import shapely
import osmnx
import networkx as nx
import geopandas as gpd
import pandas as pd
from argparse import ArgumentParser

def simplify_graph(G: nx.MultiDiGraph, tol):
    # osmnx simplify
    G_unprojected = osmnx.project_graph(G)
    G = osmnx.consolidate_intersections(G_unprojected, dead_ends=True, tolerance=tol, rebuild_graph=True)
    G = osmnx.project_graph(G, to_crs="EPSG:4326")

    # self loops
    G.remove_edges_from(nx.selfloop_edges(G))
    return G

def parse_args():
    p = ArgumentParser()
    p.add_argument('users', type=str, help="Input GeoJSON file storing nodes coordinates.")
    p.add_argument('tanks', type=str, help="Input GeoJSON file storing tanks coordinates and elevation.")
    p.add_argument('snaps', type=str, help="Output GeoJSON file storing the result of the spatial join between nodes, tanks and road network intersections.")
    p.add_argument('intersections', type=str, help="Output GeoJSON file storing road network intersections (future WDS possible junctions).")
    p.add_argument('links', type=str, help="Output GeoJSON file storing road network links.")
    p.add_argument('-b', '--bound', type=float, default=0.00300, help="Buffer around the smallest enclosing circle encompassing nodes and tanks.")
    p.add_argument('-c', '--crs', type=str, default='EPSG:4326', help="CRS to be used within shapely computations.")
    p.add_argument('--unprojected-crs', type=str, default="EPSG:3857", help="Unprojected CRS to be used within shapely computations.")
    p.add_argument('-t', '--tolerance', type=float, default=30.0, help="Tolerance constant used in osmnx road network simplification.")

    return p.parse_args()


if __name__ == '__main__':
    args = parse_args()
    users_path = args.users
    tanks_path = args.tanks  
    snaps_path = args.snaps
    links_path = args.links
    intersections_path = args.intersections

    users_gdf = gpd.read_file(users_path, crs=args.crs)
    tanks_gdf = gpd.read_file(tanks_path, crs=args.crs)
    polygon = shapely.minimum_bounding_circle(users_gdf.unary_union).buffer(args.bound)

    G = osmnx.graph_from_polygon(
        polygon,
        simplify=True,
        network_type='drive',
        retain_all=False,
    )
    G = simplify_graph(G, args.tolerance)
    # osmnx.plot_graph(G)

    osm_nodes, osm_edges = osmnx.graph_to_gdfs(G, nodes=True, edges=True)

    osm_nodes.reset_index(drop=False, inplace=True)
    intersections = osm_nodes[['osmid', 'geometry']]

    gpd_intersections = gpd.GeoDataFrame(intersections, geometry='geometry', crs=args.crs)

	### Adding tanks to users ###
    gdf = pd.concat([users_gdf[['geometry','id']], tanks_gdf[['geometry','id']]])
    nearest = gdf.to_crs(args.unprojected_crs).sjoin_nearest(gpd_intersections.to_crs(args.unprojected_crs))

    osm_edges.reset_index(inplace=True)
    links = osm_edges[['u', 'v', 'key', 'length', 'geometry', 'highway']]

    def make_highway_tuple(row):
        if isinstance(row['highway'], list):
            row['highway'] = ";".join(row['highway'])
        return row
    links = links.apply(make_highway_tuple, axis=1)

    intersections = gpd.GeoDataFrame(intersections,
                                     geometry='geometry',
                                     crs=args.crs)

    links = gpd.GeoDataFrame(links,
                                     geometry='geometry',
                                     crs=args.crs)

    intersections.to_file(intersections_path, driver='GeoJSON')
    links.to_file(links_path, driver='GeoJSON')
    links.set_index(['u', 'v', 'key'], drop=False, inplace=True)

    nearest = nearest.to_crs(args.crs)
    nearest.to_file(snaps_path, driver='GeoJSON')

