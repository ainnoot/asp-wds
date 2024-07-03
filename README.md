# Installing
This project uses `poetry` as a dependency management system. Run `poetry install` to install dependencies, and `poetry shell` to activate a separate Python environmnet.

# Inputs
Running the scripts requires a set of geographical coordinates in GeoJSON format, storing `Point` geometry. This is an example of the required data schema for the WDS nodes.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
	# Unique identifier for the node
        "id": 1,

	# Physical address of the node
        "address": "Via Pietro Bucci, 87036, Arcavacata CS, Italy"
      },

      "geometry": {
        "type": "Point",

	# (lon,lat) coordinates
        "coordinates": [
          16.22580,
          39.36322
        ]
      }
    }
  ]
}
```

Tanks must be provided in a separate GeoJSON file matching the same schema but with an extra `elevation` property (the average meters above local sea level, as an integer).

# Scripts
Check out `wds_reconstruction.sh` for the execution order of the different scripts. `compute_elevation.py` requires the environment variable `GOOGLE_MAPS_API_KEY` to be exported. The encoding is available in the `wds_reconstruction.lp` file.

## `extract_road_network.py`
```
usage: extract_road_network.py [-h] [-b BOUND] [-c CRS] [--unprojected-crs UNPROJECTED_CRS] [-t TOLERANCE]
                               users tanks snaps intersections links

positional arguments:
  users                 Input GeoJSON file storing nodes coordinates.
  tanks                 Input GeoJSON file storing tanks coordinates and elevation.
  snaps                 Output GeoJSON file storing the result of the spatial join between nodes, tanks and road network
                        intersections.
  intersections         Output GeoJSON file storing road network intersections (future WDS possible junctions).
  links                 Output GeoJSON file storing road network links.

options:
  -h, --help            show this help message and exit
  -b BOUND, --bound BOUND
                        Buffer around the smallest enclosing circle encompassing nodes and tanks.
  -c CRS, --crs CRS     CRS to be used within shapely computations.
  --unprojected-crs UNPROJECTED_CRS
                        Unprojected CRS to be used within shapely computations.
  -t TOLERANCE, --tolerance TOLERANCE
                        Tolerance constant used in osmnx road network simplification.

```

## `compute_elevation.py`
```
usage: compute_elevation.py [-h] intersections

positional arguments:
  intersections  Input GeoJSON file storing road network intersection data.

options:
  -h, --help     show this help message and exit

```

This scripts modifies the `intersections` file, adding an `elevation` property to points.

## `reify_network.py`
```
usage: reify_network.py [-h] [--crs CRS] snaps links intersections tanks logic_program

positional arguments:
  snaps          Input GeoJSON file storing information about spatial join between nodes, tanks and road network intersections.
  links          Input GeoJSON file storing information about road network links.
  intersections  Input GeoJSON file storing information about road network intersections.
  tanks          Input GeoJSON file storing tanks' coordinates and elevation data.
  logic_program  Output file storing the set of facts for this WDS reconstruction problem instance.

options:
  -h, --help     show this help message and exit
  --crs CRS      Coordinate reference system used to read the GeoJSON files.
```

## `solve_wds.py`
```
usage: solve_wds.py [-h] instance links output_geojson

positional arguments:
  instance        Input set of facts for the WDS reconstruction problem instance.
  links           Input GeoJSON file storing available road network links.
  output_geojson  Output GeoJSON file storing the reconstructed topology.

options:
  -h, --help      show this help message and exit
```
