import math
from threading import Thread

# Stolen from stack overflow https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs, Verbose)
        self._return = None
    def run(self):
        if self._Thread__target is not None:
            self._return = self._Thread__target(*self._Thread__args,
                                                **self._Thread__kwargs)
    def join(self):
        Thread.join(self)
        return self._return

# Importance thresholds
search_radius = 50              # 50m around the point
depth = 40                      # 40m under water
proximity_area = 5000           # At least 5km away from anything

attributes = 1                  # Amount of attributes that are checked (Dumb desigh, needs to be updated every time a new attribute is being tested)
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

    return R * c

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

# Open the databases
main = open("DataScience/DataScienceProject/processed data/potential_points.gml", "r")
fish_data = open("DataScience/DataScienceProject/processed data/processed_kv_eiendom_kompleks.gml", "r")
depth_data = open("insert path to file here", "r")
# add more as more come in

# Actual searching functions
def look_for_fishing_sites(lat, lon):
    lines = fish_data.readlines()
    nearest_distance = math.inf
    # Check the fishing location database
    for line in lines:
        coords = line.split(", ")
        flat, flon = coords[0], coords[1]
        # Check if the coordinates are UMT, and if they are, convert to latlon
        if (isUMT(flat, flon)): flat, flon = utmToLatLng(flat, flon) 
        # Calculate the distance between the point and the phishing site
        distance = calculate_distance_in_latlong(lat, lon, flat, flon)
        # If it's too near, based on the proximity attribute, then stop the function and return the proximity
        if distance < proximity_area: return distance
        # If it's not too close, then keep finding the closest site
        if distance < nearest_distance: nearest_distance = distance
    # Return the distance to closest site so that a score can be calculated out of it
    return nearest_distance



# Read the main file and check the points with the criteria
lines = main.readlines()

sweet_spots = []
# Here relying on the point coordinates being one point per line, and 
# the points being in lat lon format
for line in lines:
    coords = line.split(", ")
    lat, lon = coords[0], coords[1]
    if (isUMT(lat, lon)): lat, lon = utmToLatLng(lat, lon)

    # Run the checks here
    fishing = ThreadWithReturnValue(target=look_for_fishing_sites, args=(lat, lon,))

    # Calculate metric
    # Joining the thread will return the value of the functions while waiting for the threads to terminate
    score = (fishing.join/proximity_area) / attributes

    sweet_spots.append([lat, lon, score])



# Save the points in a new file
potential_sweet_spot_locations = open("DataScience/DataScienceProject/potential_sweet_spots.txt", "a")

for spot in sweet_spots:
    potential_sweet_spot_locations.write(spot)
    potential_sweet_spot_locations.write("\n")