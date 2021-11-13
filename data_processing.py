import sys

if len(sys.argv) < 2: 
    print("Please, write the name of the file you wish to process")
    exit(0)

name = sys.argv[1].split("data/")
new_name = "/home/bigdikdinko/Documents/NTNU/DataScience/DataScienceProject/processed data/processed_" + name[1]
new_file = open(new_name, "a")

with open(sys.argv[1]) as f:
    lines = f.readlines()
    for line in lines:
        # Template
        # if "" in line:
        #     new_file.write(line.split("")[1][1:-2] + "\n")

        if "<gml:posList>" in line:
            new_file.write(line.split("gml:posList")[1][1:-2] + "\n")

        if "<gml:coordinates>" in line:
            new_file.write(line.split("gml:coordinates")[1][1:-2] + "\n")

        if "<ogr:navn>" in line:
            new_file.write(line.split("ogr:navn")[1][1:-2] + "\n")

        if "<ogr:kompleksnavn>" in line:
            new_file.write(line.split("ogr:kompleksnavn")[1][1:-2] + "\n")