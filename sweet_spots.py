potential_sweet_spots = []

# Open the databases
main = open("DataScience/DataScienceProject/processed data/processed_Plan_0000_Norge_25833_Sprstrandsoner_GML.gml", "r")
fish = open("DataScience/DataScienceProject/processed data/processed_kv_eiendom_kompleks.gml", "r")

# Read the main file and check the points with the criteria
lines = main.readlines()
for line in lines:
    coords = line.split(" ")
    i = 0
    while i < len(coords)-1:
        lat = coords[i]
        lon = coords[i+1]

        # Run the checks here

        i = i+2

# Save the points in a new file
potential_sweet_spot_locations = open("DataScience/DataScienceProject/potential_sweet_spots.txt", "a")

for spot in potential_sweet_spots:
    potential_sweet_spot_locations.write(spot)
    potential_sweet_spot_locations.write(", ")