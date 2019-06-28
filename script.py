import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
import os

stop_name = 'Parnell Train Station'
subscription_key = os.environ.get('AUCKLAND_TRANSPORT_SUBSCRIPTION_KEY')

def request_at_json(path):
    try:
        headers = {'Ocp-Apim-Subscription-Key': subscription_key}
        params = urllib.parse.urlencode({ })
        conn = http.client.HTTPSConnection('api.at.govt.nz')
        conn.request("GET", path + "?%s" % params, "{body}", headers)
        response = conn.getresponse()
        json_data = json.loads(response.read())
        if (json_data['status'] == 'OK' and not json_data['error']):
            conn.close()
            return json_data['response']
        else:
            print('Error in response')
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

def sort_departure_time(stop):
    return stop['departure_time']

def get_stop_id():
    all_stops_response = request_at_json('/v2/gtfs/stops')
    station = next((s for s in all_stops_response if s['stop_name'] == stop_name), None)
    return station['stop_id'] if station else None

def get_stops_at_station(station_stop_id):
    stops_at_station = request_at_json("/v2/gtfs/stopTimes/stopId/" + station_stop_id)
    stops_at_station.sort(key=sort_departure_time)
    return stops_at_station

def get_updates_for_stop_id(stop_id):
    all_trip_updates_response = request_at_json("/v2/public/realtime/tripupdates")
    all_trip_updates = all_trip_updates_response['entity']
    updates = []
    for trip in all_trip_updates:
        stop_at_update = trip['trip_update']['stop_time_update']['stop_id']
        if stop_at_update == stop_id:
            updates.append(trip)
    return updates

def main():
    station_stop_id = get_stop_id()
    station_stops = get_stops_at_station(station_stop_id)
    updates = get_updates_for_stop_id(station_stop_id)
    # for stop in station_stops:
    #     print(stop)
    print(updates)

main()