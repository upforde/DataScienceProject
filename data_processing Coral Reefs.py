import sys

"""
if len(sys.argv) < 2: 
    print("Please, write the name of the file you wish to process")
    exit(0)
"""

#name = sys.argv[1].split("data/")
new_name = "processed_MilitaryTrainingZones" 
new_file = open(new_name, "a")

with open("Depth", errors="ignore") as f:
    lines = f.readlines()
    odd = True
    for line in lines:
        # Template
        # if "" in line:
        #     new_file.write(line.split("")[1][1:-2] + "\n")

        # Add other stuff that is ge
        # ared towards any data
        if odd:
            new_file.write(line.replace("\n", ","))
            odd = False
        else:
            new_file.write(line)
            odd = True

