import math
from multiprocessing.pool import ThreadPool

import json
from geopy import distance
import requests

# Importance thresholds (These are all subject to change)
depth_threshold = 40                      # 40m under water
depth_wiggle = 10
proximity_area = 500           # At least 500m away from fishing areas
power_proximity = 10_000         # Best if at most 50km away, but not a problem otherwise
ankering_proximity = 500        # Best if it's at least 500m away from ankering areas
# military_proximity = 5000       # Best if at least 5km awawy from any military areas
coral_proximity = 500          # At least 50m away from coral reaves
incident_proximity = 500       # At least 1km away from an incident cite
distance_tolerance = 5000.0       # Tolerable distance up to 5km.

# add more as more come in

# Function definitions
def calculate_distance_in_latlong(latA, lonA, latB, lonB):
    # Radius of the Earth
    R = 6373.0

    lat1 = math.radians(latA)
    lon1 = math.radians(lonA)
    lat2 = math.radians(latB)
    lon2 = math.radians(lonB)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c * 1000

# Stolen from Stack Overflow https://stackoverflow.com/questions/343865/how-to-convert-from-utm-to-latlng-in-python-or-javascript
def utmToLatLng(easting, northing, zone=33, northernHemisphere=True):
    if not northernHemisphere:
        northing = 10000000 - northing

    a = 6378137
    e = 0.081819191
    e1sq = 0.006739497
    k0 = 0.9996

    arc = northing / k0
    mu = arc / (a * (1 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))

    ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (1 + math.pow((1 - e * e), (1 / 2.0)))

    ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

    cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
    cc = 151 * math.pow(ei, 3) / 96
    cd = 1097 * math.pow(ei, 4) / 512
    phi1 = mu + ca * math.sin(2 * mu) + cb * math.sin(4 * mu) + cc * math.sin(6 * mu) + cd * math.sin(8 * mu)

    n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

    r0 = a * (1 - e * e) / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
    fact1 = n0 * math.tan(phi1) / r0

    _a1 = 500000 - easting
    dd0 = _a1 / (n0 * k0)
    fact2 = dd0 * dd0 / 2

    t0 = math.pow(math.tan(phi1), 2)
    Q0 = e1sq * math.pow(math.cos(phi1), 2)
    fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

    fact4 = (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0) * math.pow(dd0, 6) / 720

    lof1 = _a1 / (n0 * k0)
    lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
    lof3 = (5 - 2 * Q0 + 28 * t0 - 3 * math.pow(Q0, 2) + 8 * e1sq + 24 * math.pow(t0, 2)) * math.pow(dd0, 5) / 120
    _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
    _a3 = _a2 * 180 / math.pi

    latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

    if not northernHemisphere:
        latitude = -latitude

    longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3

    return (latitude, longitude)

def isUMT(lat, lon):
    if lat > 360 and lon > 360: return True
    elif lat > 360 and lon < -360: return True
    elif lat < -360 and lon > 360: return True
    elif lat < -360 and lon < -360: return True
    return False

# Actual searching functions
# Many of these functions can be written better, or at least more generically, but I really can't right now, too tired to think about that
def look_for_fishing_sites(lat, lon):
    fish_data = open("processed data/processed_kv_eiendom_kompleks.gml", "r", encoding='utf-8-sig')
    lines = fish_data.readlines()
    nearest_distance = math.inf
    # Check the fishing location database
    for line in lines:
        coords = line.split(",")
        flat, flon = float(coords[0]), float(coords[1])
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(flat, flon)): flat, flon = utmToLatLng(flat, flon) 
        # Calculate the distance between the point and the phishing site
        distance = calculate_distance_in_latlong(lat, lon, flat, flon)
        # If it's not too close, then keep finding the closest site
        if distance < nearest_distance: nearest_distance = distance
    # Return the distance to closest site so that a score can be calculated out of it
    return nearest_distance

def look_for_depth(lat, lon):
    depth_data = open("processed data/processed_Depth", "r", encoding='utf-8-sig')
    lines = depth_data.readlines()
    nearest_distance = math.inf
    current_depth = 0
    # Check the fishing location database
    for line in lines:
        coords = line.rstrip().split(",")
        dlat, dlon = float(coords[0]), float(coords[1])
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(dlat, dlon)): dlat, dlon = utmToLatLng(dlat, dlon) 
        # Calculate the distance between the sweet spot and the depth gauging place 
        distance = calculate_distance_in_latlong(lat, lon, dlat, dlon)
        # If the distance is nearer than the nearest distance to date, then replace the distance and the depth with current values
        if distance < nearest_distance: 
            nearest_distance = distance
            current_depth = float(coords[2])
    # Returns the depth of the area that is the closest to the current sweet spot
    return current_depth

def look_for_incidents(lat, lon):
    incidents_data = open("processed data/processed_vts_hendelser.gml", "r", encoding='utf-8-sig')
    lines = incidents_data.readlines()
    nearest_distance = math.inf
    # Check the fishing location database
    for line in lines:
        coords = line.split(",")
        ilat, ilon = float(coords[0]), float(coords[1])
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(ilat, ilon)): ilat, ilon = utmToLatLng(ilat, ilon)
        # Calculate the distance between the point and the incident site
        distance = calculate_distance_in_latlong(lat, lon, ilat, ilon)
        # If it's too near, based on the proximity attribute, then stop the function and return the proximity
        if distance < incident_proximity: return distance
        # If it's not too close, then keep finding the closest site
        if distance < nearest_distance: nearest_distance = distance
    # Return the distance to closest site so that a score can be calculated out of it
    return nearest_distance

def look_for_coral(lat, lon):
    coral_data = open("processed data/processed_CoralReef", "r")
    lines = coral_data.readlines()
    nearest_distance = math.inf
    # Check the fishing location database
    for line in lines:
        coords = line.split(",")
        clat, clon = float(coords[0]), float(coords[1])
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(clat, clon)): clat, clon = utmToLatLng(clat, clon)
        # Calculate the distance between the point and the coral reaves site
        distance = calculate_distance_in_latlong(lat, lon, clat, clon)
        # If it's not too close, then keep finding the closest site
        if distance < nearest_distance: nearest_distance = distance
    # Return the distance to closest site so that a score can be calculated out of it
    return nearest_distance

def look_for_water_power(lat, lon):
    water_power_data = open("processed data/Vannkraft_Vannkraftverk.txt", "r", encoding='utf-8-sig')
    lines = water_power_data.readlines()
    nearest_distance = math.inf
    # Check the fishing location database
    for line in lines:
        coords = line.split(", ")
        wlat, wlon = float(coords[0]), float(coords[1])
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(wlat, wlon)): wlat, wlon = utmToLatLng(wlat, wlon)
        # Calculate the distance between the point and the water power site
        distance = calculate_distance_in_latlong(lat, lon, wlat, wlon)
        if distance < nearest_distance: nearest_distance = distance
    # Return the distance to closest site so that a score can be calculated out of it
    return nearest_distance

def look_for_wind_power(lat, lon):
    wind_power_data = open("processed data/Vindkraft_Vindkraftanlegg.txt", "r", encoding='utf-8-sig')
    lines = wind_power_data.readlines()
    nearest_distance = math.inf
    # Check the fishing location database
    for line in lines:
        coords = line.split(", ")
        wlat, wlon = float(coords[0]), float(coords[1])
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(wlat, wlon)): wlat, wlon = utmToLatLng(wlat, wlon)
        # Calculate the distance between the point and the wind power site
        distance = calculate_distance_in_latlong(lat, lon, wlat, wlon)
        if distance < nearest_distance: nearest_distance = distance
    # Return the distance to closest site so that a score can be calculated out of it
    return nearest_distance

def look_for_damn_power(lat, lon):
    damn_data = open("processed data/Vannkraft_DamPunkt.txt", "r", encoding='utf-8-sig')
    lines = damn_data.readlines()
    nearest_distance = math.inf
    # Check the damn location database
    for line in lines:
        coords = line.split(", ")
        dlat, dlon = float(coords[0]), float(coords[1])
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(dlat, dlon)): dlat, dlon = utmToLatLng(dlat, dlon)
        # Calculate the distance between the point and the dam power site
        distance = calculate_distance_in_latlong(lat, lon, dlat, dlon)
        if distance < nearest_distance: nearest_distance = distance
    # Return the distance to closest site so that a score can be calculated out of it
    return nearest_distance

def distance_between_two_points(lat1, lon1, lat2, lon2):
    starting_point = (str(lat1), str(lon1)) 
    destination = (str(lat2), str(lon2))
    total_distance = distance.distance(starting_point, destination).m

    return total_distance

# def look_for_ankering(lat, lon):
#     ankering_data = open("DataScience/DataScienceProject/processed data/kyv_ankringsomraderflate.sos", "r", encoding='utf-8-sig')
#     lines = ankering_data.readlines()
#     for line in lines:
#         return
#     return

# def look_for_military_nono(lat, lon):
#     military_nono_zones = open("DataScience/DataScienceProject/processed data/processed_MilitaryNoNoZones", "r", encoding='utf-8-sig')
#     lines = military_nono_zones.readlines()
#     newarest_distance = math.inf
#     for line in lines:
#         coords = line.split()
#     return

# def look_for_military_training(lat, lon):
#     military_training_zones = open("DataScience/DataScienceProject/processed data/processed_MilitaryTrainingZones", "r", encoding='utf-8-sig')
#     return

# add more as they come in

def run_checks(lat, lon):
    '''
    Takes in `lat` and `lon` of a point, and returns all of the things
    '''

    if (isUMT(lat, lon)): lat, lon = utmToLatLng(lat, lon)

    #Run the checks here
    pool = ThreadPool(processes=9)

    fishing = pool.apply_async(look_for_fishing_sites, (lat, lon))

    depth = pool.apply_async(look_for_depth, (lat, lon))

    incidents = pool.apply_async(look_for_incidents, (lat, lon))

    corals = pool.apply_async(look_for_coral, (lat, lon))

    water_power = pool.apply_async(look_for_water_power, (lat, lon))

    wind_power = pool.apply_async(look_for_wind_power, (lat, lon))

    dam_power = pool.apply_async(look_for_damn_power, (lat, lon))

    # Just using Trondheim Havn and Equinor Resarch center for now.
    hq_dist = pool.apply_async(distance_between_two_points, (63.4278768, 10.3841791, 63.4388664 , 10.4760904))
    harbor_dist = pool.apply_async(distance_between_two_points, (63.4278768, 10.3841791, lat, lon))

    # ankering = ThreadWithReturnValue(target=look_for_ankering, args=(lat, lon))
    # ankering.start()

    # military_nono = ThreadWithReturnValue(target=look_for_military_nono, args=(lat, lon))
    # military_nono.start()

    # military_training = ThreadWithReturnValue(target=look_for_military_training, args=(lat, lon))
    # military_training.start()

    # Calculate metrics

    # Setting the scores between 0 and 2, where below 1 is bad, and above 1 is good

    # Don't know atm if I should keep the thing 0-2 thing, can't come up with anything better right now tho
    # I can see several issues with the approach that I've come up with here, but just like Fermat, I won't
    # comment on them or explain them here. You gotto figure it out or ask me in person
    fishing_result, depth_result, incidents_result, corals_result, water_power_result, wind_power_result, dam_power_result, hq_dist_result, harbor_dist_result = fishing.get(), depth.get(), incidents.get(), corals.get(), water_power.get(), wind_power.get(), dam_power.get(), hq_dist.get(), harbor_dist.get()

    """
    # OLD way

    fishing_score = 0 if fishing_result < proximity_area else fishing_result/proximity_area if fishing_result/proximity_area < 2 else 2

    depth_score = depth_result/depth_threshold if depth_result/depth_threshold < 2 else 2

    incident_score = incidents_result/incident_proximity if incidents_result/incident_proximity < 2 else 2

    coral_score = 0 if corals_result < coral_proximity else corals_result/coral_proximity if corals_result/coral_proximity < 2 else 2

    distance_score = (hq_dist_result + harbor_dist_result)/distance_tolerance if (hq_dist_result + harbor_dist_result)/distance_tolerance < 2 else 2

    water_power_score = 2 - water_power_result/power_proximity
    if water_power_score < 0: water_power_score = 0

    wind_power_score = 2 - wind_power_result/power_proximity
    if wind_power_score < 0: wind_power_score = 0

    dam_power_score = 2 - dam_power_result/power_proximity
    if dam_power_score < 0: dam_power_score = 0
    
    # ankering_score = something here
    # military_nono_score = something here
    # military_training_score = something here

    # This calculation takes the average of the results from the checks. The calculations are set up so that
    # result values less than 1 are bad, and values more than 1 are good for the spot.
    overall_score = (fishing_score + depth_score + incident_score + coral_score + water_power_score + wind_power_score + dam_power_score + distance_score) #/ 8
    #  print(lat, lon, fishing_score, depth_score, incident_score, coral_score, water_power_score, wind_power_score, dam_power_score,  distance_score, overall_score)
    return (lat, lon, fishing_score, depth_score, incident_score, coral_score, water_power_score, wind_power_score, dam_power_score, distance_score, overall_score)

    """

    # NEW way
    # Fishing requirements
    if (fishing_result > proximity_area): fishing_score = 1
    else: fishing_score = 0

    # Checking depth requirements
    if (depth_result > depth_threshold + depth_wiggle or depth_result < depth_threshold - depth_wiggle ): depth_score = 0
    else: depth_score = 1

    # Proximity to corals
    if (corals_result > coral_proximity): corals_score = 1
    else: corals_score = 0

    # Incidents
    if (incidents_result > incident_proximity): incidents_score = 1
    else: incidents_score = 0

    # Power 
    if water_power_result < power_proximity : water_power_score = 1
    else: water_power_score = 0

    if wind_power_result < power_proximity : wind_power_score = 1
    else: wind_power_score = 0

    if dam_power_result < power_proximity : dam_power_score = 1
    else: dam_power_score = 0

    if water_power_score > 0 or wind_power_score > 0 or dam_power_score > 0:  
        total_power_score = 1 
    else: total_power_score = 0

    # Distance
    distance_score = 0 if (hq_dist_result + harbor_dist_result)/distance_tolerance < 1 else 1

    overall_score = ( depth_score + fishing_score + corals_score + incidents_score + total_power_score + distance_score) 
    #  print(lat, lon, fishing_score, depth_score, incident_score, coral_score, water_power_score, wind_power_score, dam_power_score,  distance_score, overall_score)
    return (lat, lon, fishing_score, depth_score, incidents_score, corals_score , total_power_score, distance_score, overall_score)