from argparse import ArgumentParser
from pathlib import Path

import clingo
import pandas as pd
import geopandas as gpd
CLINGO_OPTS = ["--opt-strategy=usc,oll", "--opt-mode=optN", "--models=0"]

class WDSTopology:
    def __init__(self, links):
        self.links = links
        self.edges = []

    def save(self, path):
        spanning_tree = self.links[self.links.index.isin(st.edges)]
        spanning_tree.to_file(path, driver='GeoJSON')

    def __call__(self, model: clingo.Model):
        if model.optimality_proven:
            for f in model.symbols(shown=True):
                u, v = f.arguments[0].number, f.arguments[1].number
                k = f.arguments[2].number
                i = f.arguments[3].name == 'inversion'
                self.edges.append((u, v, k) if not i else (v, u, k))
            return False


def parse_args():
    p = ArgumentParser()
    p.add_argument('instance', help="Input set of facts for the WDS reconstruction problem instance.")
    p.add_argument('links', help="Input GeoJSON file storing available road network links.")
    p.add_argument('output_geojson', help="Output GeoJSON file storing the reconstructed topology.")

    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()

    instance_path = args.instance
    links_path = args.links
    output_geojson_path = args.output_geojson

    links = gpd.read_file(links_path, geometry='geometry')
    links.set_index(['u', 'v', 'key'], drop=True, inplace=True)

    ctl = clingo.Control(CLINGO_OPTS)
    ctl.load((Path(__file__).parent / 'wds_reconstruction.lp').as_posix())
    ctl.load(instance_path)
    ctl.ground([("base", [])])

    st = WDSTopology(links)
    ans = ctl.solve(on_model=st)

    st.save(output_geojson_path)
