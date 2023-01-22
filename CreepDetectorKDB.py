import argparse
import json
import kismetdb
from pathlib import Path
from pandas import DataFrame
from haversine import haversine, Unit
from folium import FeatureGroup, Icon, LayerControl, Map, Marker, PolyLine, Popup


class CreepDetectorKDB:
  @staticmethod
  def find_creeps(kismetdb_file, distance_threshold=0.2, distance_unit=Unit.MILES):
    # Fetch all devices
    devices = kismetdb.Devices(kismetdb_file)
    df_devices = DataFrame.from_records(devices.get_meta())

    # Create a new column of distance, in kilometers, between min and max lat/lon
    df_devices['haversine'] = df_devices.apply(
      lambda row: haversine((row.min_lat, row.min_lon), (row.max_lat, row.max_lon),
                  unit=distance_unit), axis=1)

    # Keep only creeps, those that were seen farther than distance threshold
    df_creeps = df_devices.loc[df_devices['haversine'] >= distance_threshold].sort_values(by=['haversine'],
                                                ascending=False)

    # Fetch all packets
    packets = kismetdb.Packets(kismetdb_file)

    # Prepare creeps' history
    creeps = dict()
    for _, creep in df_creeps.iterrows():
      df_packets = DataFrame.from_records(packets.get_meta(sourcemac=creep.devmac))
      df_packets = df_packets[(df_packets['lat'] != 0.0) & (df_packets['lon'] != 0.0)]\
        .drop_duplicates(subset=["ts_sec", "lat", "lon"])\
        .sort_values(by=['ts_sec', 'ts_usec'])

      creeps[creep.devmac] = df_packets[["ts_sec", "lat", "lon", "frequency", "signal", "destmac"]]

    return creeps

  @classmethod
  def create_map(CreepDetectorClass, kismetdb_file, output_file=None, distance_threshold=0.2, distance_unit=Unit.MILES):
    # Let's get our creeps!
    creeps = CreepDetectorClass.find_creeps(kismetdb_file, distance_threshold, distance_unit)

    # Create our GPS track
    snapshots = kismetdb.Snapshots(kismetdb_file)
    df_snapshots = DataFrame.from_records(snapshots.get_meta(snaptype="GPS")).sort_values(by=['ts_sec', 'ts_usec'])
    # Remove rows with no GPS lock
    df_snapshots = df_snapshots[(df_snapshots['lat'] != 0.0) & (df_snapshots['lon'] != 0.0)]\
      .drop_duplicates(subset=["ts_sec", "lat", "lon"])
    # Remove duplicate GPS points
    gps_track = df_snapshots[["lat", "lon"]].to_records(index=False)

    # Save our start point
    gps_start_coords = (df_snapshots.iloc[0]['lat'], df_snapshots.iloc[0]['lon'])

    # Generate our map
    creeps_map = Map(location=gps_start_coords, zoom_start=15)
    PolyLine(gps_track, line_opacity=0.5, weight=4).add_to(creeps_map)
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'beige', 'gray', 'pink', 'black', 'lightgreen',
          'darkblue', 'lightblue', 'lightred', 'darkpurple', 'darkred', 'cadetblue', 'lightgray', 'darkgreen']

    # Prepare a Devices instance
    devices = kismetdb.Devices(kismetdb_file)

    # Plot the creeps
    for i, creep in enumerate(creeps):
      creep_feature = FeatureGroup(name=creep)  # devmac
      creep_device = devices.get_all(devmac=creep).pop()
      creep_json = json.loads(creep_device['device'])
      creep_oui = creep_json['kismet.device.base.manuf']
      for _, marker in creeps[creep].iterrows():
        popup = Popup(f'MAC: {creep}<br>'
                f'OUI: {creep_oui}<br>'
                f'Type: {creep_device["type"]}<br>'
                f'RSSI: {marker["signal"]}', max_width=500)
        Marker(location=(marker["lat"], marker["lon"]), popup=popup,
             icon=Icon(color=colors[i % len(colors)], icon='user-secret',
                 prefix='fa')).add_to(creep_feature)
      creep_feature.add_to(creeps_map)

    # Add toggle controls for creeps
    LayerControl().add_to(creeps_map)

    # Save the map
    try:
      filename = Path(output_file).resolve()
    except TypeError:
      filename = Path(kismetdb_file).with_suffix('.html').resolve()
    finally:
      creeps_map.save(str(filename))
      print(f"Done! {len(creeps)} creeps found. Map file: {filename.resolve()}")


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('input_file', help="input file (KismetDB, normally ends in .kismet)")
  parser.add_argument('-o', '--output', dest='output_file', default=None, help="output file (default: <input_file>.html)")
  parser.add_argument('-d', '--distance', dest='dist_value', default="0.2", help="distance threshold to be considered a creep (default: 0.2)")
  parser.add_argument('-u', '--unit', dest='dist_unit', default="mi", help="km|m|mi|nmi|ft|in|rad|deg (default: mi)")
  args = parser.parse_args()
  
  CreepDetectorKDB.create_map(args.input_file, output_file=args.output_file, distance_threshold=float(args.dist_value), distance_unit=args.dist_unit)


if __name__ == "__main__":
  main()