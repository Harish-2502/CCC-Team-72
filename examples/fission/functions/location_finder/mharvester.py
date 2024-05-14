import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, Point


def main():
    
    i = 0
    for coord in dev_act_monitor[['Location']].iterrows():
        coord = coord[1][0].split(",")
        lat = coord[0]
        long = coord[1]
        point = Point(long, lat)
        inside_east = False
        inside_west = False
        inside_north = False

        for poly in sf_east['geometry']:
            if poly.contains(point):
                inside_east = True
        
        for poly in sf_west['geometry']:
            if poly.contains(point):
                inside_west = True

        for poly in sf_north['geometry']:
            if poly.contains(point):
                inside_north = True

        if (inside_east == True) or (inside_north == True) or (inside_west == True):
            print(f"{i}'th point:")
            print(f"east: {inside_east}")
            print(f"north: {inside_north}")
            print(f"west: {inside_west}")
        else:
            print(f"{i}'th point was out of bounds")
        i += 1
    return json.dumps(m.timeline(timeline='public', since_id=lastid, remote=True), default=str)
