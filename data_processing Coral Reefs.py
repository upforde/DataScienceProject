import sys

"""
if len(sys.argv) < 2: 
    print("Please, write the name of the file you wish to process")
    exit(0)
"""

#name = sys.argv[1].split("data/")
new_name = "processed_MilitaryTrainingZones" 
new_file = open(new_name, "a")

with open("MilitaryTrainingZones.gml", errors="ignore") as f:
    lines = f.readlines()
    for line in lines:
        # Template
        # if "" in line:
        #     new_file.write(line.split("")[1][1:-2] + "\n")

        # Add other stuff that is ge
        # ared towards any data
        if "<gml:posList>" in line:
            new_file.write(line.split("gml:posList")[1][1:-2] + "\n")