from random import uniform, choice
from numpy import std, mean
import sweet_spots as SS
import folium
import math

# Specify the parameters of the model

# Format - (lat,lon) - specify the top left and bottom right corner of a rectangle within which the search should be made
topRightCorner = ( 63.556504, 10.616752 )
bottomLeftCorner = ( 63.456658, 10.256998 )

# Granularity - how many squares to divide the region above into lat/lon - height/wdith
chunksLat = 5
chunksLon = 5         

# Monte Carlo parameters
samplingPer = 10         # How many random points to sample within a given region
calculateSTD = True             # Whether or not to calculate standard deviation

# The MonteCarlo itself
def MonteCarlo():

    # Bookeeping
    chunks = []             # A list of tuples with tuples of topRightCorner and bottomLeftCorner

    latDiff = abs(topRightCorner[0] - bottomLeftCorner[0])/chunksLat
    lonDiff = abs(topRightCorner[1] - bottomLeftCorner[1])/chunksLon

    # Divide the region into chunks
    for lon in range(chunksLon):
        for lat in range(chunksLat):
            chunks.append( ( ( lat*latDiff + bottomLeftCorner[0], lon*lonDiff + bottomLeftCorner[1]), 
                            ( (lat+1)*latDiff + bottomLeftCorner[0], (lon+1)*lonDiff + bottomLeftCorner[1]) ) )

    results = []
    chunkScores = []
    sampleCoors = []
    sampleScores = []
    
    chunkIndex = 0
    # For each chunk sample samplingPer number of times
    for chunk in chunks:
        chunkScore = []

        sampleCoors.append([])
        sampleScores.append([])

        for sample in range(samplingPer):
            # Pick a random spot within the range
            sampleCoordinates = (uniform(chunk[0][0],chunk[1][0]), uniform(chunk[0][1],chunk[1][1]))

            # Get its score
            sampleScore = SS.run_checks(sampleCoordinates[0], sampleCoordinates[1])[-1]
            chunkScore.append(sampleScore)

            # Sample Coordinates + scores
            sampleCoors[chunkIndex].append(sampleCoordinates)
            sampleScores[chunkIndex].append(sampleScore)

        # Once chunk is evaluated, finds its mean and STD
        chunkMean = mean(chunkScore)
        chunkStd = std(chunkScore)

        chunkScores.append(chunkScore)
        results.append((chunkMean, chunkStd))


        print(chunkIndex, chunkMean)

        chunkIndex += 1

    return chunks, chunkScores, results, sampleCoors, sampleScores


chunks, chunkScores, results, sampleCoors, sampleScores = MonteCarlo()
#print(sampleScores)

def pseudocolor(val, minval=0, maxval=6):
    """ Convert value in the range minval...maxval to a color between red and green.
    """

    f = ((val-minval) / (maxval-minval) ) * 255
    r, g, b = 255 - f, f, 0

    return int(r), int(g), int(b)

print("Drawing map")

m = folium.Map(location=((topRightCorner[0] + bottomLeftCorner[0]) / 2, (topRightCorner[1] + bottomLeftCorner[1]) / 2), zoom_start = 12)

# Feature groups for the tile controll
samples = folium.FeatureGroup(name='Samples', overlay=True)
meanScoreChunks = folium.FeatureGroup(name='Chunk mean score', overlay=True)

samples.add_to(m)
meanScoreChunks.add_to(m)

folium.LayerControl().add_to(m)


meanScores = [row[0]*(1-row[1]) for row in results]
minMeanScore, maxMeanScore = min(meanScores), max(meanScores)

chunkIndex = 0
for chunk in chunks:
    chunk_top_left = (chunk[0][0], chunk[1][1])
    chunk_top_right = chunk[0]
    chunk_bottom_left = chunk[1]
    chunk_bottom_right = (chunk[1][0], chunk[0][1])

    # Adding chunks in
    # Calculate the color for the mean chunk
    color = '#%02x%02x%02x' % pseudocolor(meanScores[chunkIndex], minMeanScore, maxMeanScore)
    # Add mean chunk
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = results[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(meanScoreChunks)

    # Adding Samples
    sampleIndex = 0
    for sample in sampleCoors[chunkIndex]:
        folium.Circle(
            radius = 2**(sampleScores[chunkIndex][sampleIndex]),
            location=sample,
            popup= str(sampleScores[chunkIndex][sampleIndex]) ,
            color="crimson",
            fill_color='crimson',
            fill=True,
            fill_opacity = 1
        ).add_to(samples)

        sampleIndex += 1

    chunkIndex += 1

m.add_child(samples)
m.add_child(meanScoreChunks)

m.save("index.html")