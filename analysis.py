from random import uniform, choice
from numpy import std, mean
import sweet_spots as SS


# Specify the parameters of the model

# Format - (lat,lon) - specify the top left and bottom right corner of a rectangle within which the search should be made
topRightCorner = ( 63.556504, 10.616752 )
bottomLeftCorner = ( 63.456658, 10.256998 )

# Granularity - how many squares to divide the region above into lat/lon - height/wdith
chunksLat = 10
chunksLon = 10          

# Monte Carlo parameters
samplingPer = 10         # How many random points to sample within a given region
calculateSTD = True             # Whether or not to calculate standard deviation

# The MonteCarlo itself
def MonteCarlo():

    # Bookeeping
    chunks = []             # A list of tuples with tuples of topRightCorner and bottomLeftCorner

    latDiff = (topRightCorner[0] - bottomLeftCorner[0])/chunksLat
    lonDiff = (topRightCorner[1] - bottomLeftCorner[1])/chunksLon

    # Divide the region into chunks
    for lon in range(chunksLon):
        for lat in range(chunksLat):
            chunks.append( ( ( lat*latDiff + bottomLeftCorner[0], lon*lonDiff + bottomLeftCorner[1]), 
                                  ( (lat+1)*latDiff + bottomLeftCorner[0], (lon+1)*lonDiff + bottomLeftCorner[1]) ) )

    results = []
    chunkScores = []
    
    # For each chunk sample samplingPer number of times
    for chunk in chunks:

        chunkScore = []

        for sample in range(samplingPer):
            # Pick a random spot within the range
            sampleCoordinates = (uniform(chunk[0][0],chunk[1][0]), uniform(chunk[1][0],chunk[1][1]))
            
            # Get its score
            sampleScore = SS.run_checks(sampleCoordinates[0], sampleCoordinates[1])
            chunkScore.append(sampleScore)

        # Once chunk is evaluated, finds its mean and STD
        chunkMean = mean(chunkScore)
        chunkStd = std(chunkScore)

        chunkScores.append(chunkScore)
        results.append((chunkMean, chunkStd))

    return chunks, chunkScores, results

print(MonteCarlo())