#! /usr/bin/bash
set -e

# INPUTS
NODES=$1
TANKS=$2
OUTPUT=$3

if [ "$#" -ne 3 ]; then
    echo "Usage: [input: nodes.geojson] [input: tanks.geojson] [output: wds_topology.geojson]"
    exit 1
fi

if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    echo "You must export GOOGLE_MAPS_API_KEY before running this script!"
    exit 1
fi

# GIS LAYERS & INTERMEDIATE RESULTS
TMP_FOLDER=gis_layers
echo "Creating $TMP_FOLDER to store intermediate GIS layer results..."
mkdir -p $TMP_FOLDER

SNAPS=$TMP_FOLDER/snaps.geojson
INTERSECTIONS=$TMP_FOLDER/intersections.geojson
LINKS=$TMP_FOLDER/links.geojson
LOGIC_PROGRAM=$TMP_FOLDER/instance.lp

echo "Extracting road network..."
python3 extract_road_network.py $NODES $TANKS $SNAPS $INTERSECTIONS $LINKS -b 0.00425

echo "Computing elevations..."
python3 compute_elevation.py $INTERSECTIONS

echo "Reifying network..."
python3 reify_network.py $SNAPS $LINKS $INTERSECTIONS $TANKS $LOGIC_PROGRAM

echo "Reconstructing WDS topology..."
python3 solve_wds.py $LOGIC_PROGRAM $LINKS $OUTPUT
