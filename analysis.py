from random import uniform, choice
from numpy import std, mean, average
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
    print("Calculating...")
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
    allChunkScores = []

    chunkIndex = 0
    percent = 0
    # For each chunk sample samplingPer number of times
    for chunk in chunks:
        chunkScore = []

        sampleCoors.append([])
        sampleScores.append([])
        allChunkScores.append([])

        for sample in range(samplingPer):
            # Pick a random spot within the range
            sampleCoordinates = (uniform(chunk[0][0],chunk[1][0]), uniform(chunk[0][1],chunk[1][1]))

            # Get its score
            allSampleScores = SS.run_checks(sampleCoordinates[0], sampleCoordinates[1])
            sampleScore = allSampleScores[-1]
            chunkScore.append(sampleScore)

            # Sample Coordinates + scores
            sampleCoors[chunkIndex].append(sampleCoordinates)
            sampleScores[chunkIndex].append(sampleScore)
            allChunkScores[chunkIndex].append(allSampleScores[2:])

        # Once chunk is evaluated, finds its mean and STD
        chunkMean = mean(chunkScore)
        chunkStd = std(chunkScore)

        chunkScores.append(chunkScore)
        results.append((chunkMean, chunkStd))

        print ("\033[A                                                                               \033[A")
        print("Completed {:.1f} %".format(chunkIndex/len(chunks)*100))

        chunkIndex += 1

    print ("\033[A                                                                               \033[A")
    print("Completed 100.0%")

    return chunks, chunkScores, results, sampleCoors, sampleScores, allChunkScores

chunks, chunkScores, results, sampleCoors, sampleScores, allChunkScores = MonteCarlo()

def pseudocolor(val, minval=0, maxval=6):
    """ 
    Convert value in the range minval...maxval to a color between red and green.
    """
    f = ((val-minval) / (maxval-minval) ) * 255 if maxval - minval != 0 else 0
    r, g, b = 255 - f, f, 0

    return int(r), int(g), int(b)

print("Drawing map")

m = folium.Map(location=((topRightCorner[0] + bottomLeftCorner[0]) / 2, (topRightCorner[1] + bottomLeftCorner[1]) / 2), zoom_start = 12)

# Feature groups for the tile controll
samples = folium.FeatureGroup(name='Samples', overlay=True)
meanScoreChunks = folium.FeatureGroup(name='Chunk mean score', overlay=True)
fishingScoreChunks = folium.FeatureGroup(name='Chunk fishing score', overlay=True, show=False)
depthScoreChunks = folium.FeatureGroup(name='Chunk depth score', overlay=True, show=False)
incidentsScoreChunks = folium.FeatureGroup(name='Chunk incidents score', overlay=True, show=False)
coralScoreChunks = folium.FeatureGroup(name='Chunk coral score', overlay=True, show=False)
powerScoreChunks = folium.FeatureGroup(name='Chunk power score', overlay=True, show=False)
distanceScoreChunks = folium.FeatureGroup(name='Chunk distance score', overlay=True, show=False)
overallScoreChunks = folium.FeatureGroup(name='Chunk overall score', overlay=True, show=False)

samples.add_to(m)
meanScoreChunks.add_to(m)
fishingScoreChunks.add_to(m)
depthScoreChunks.add_to(m)
incidentsScoreChunks.add_to(m)
coralScoreChunks.add_to(m)
powerScoreChunks.add_to(m)
distanceScoreChunks.add_to(m)
overallScoreChunks.add_to(m)

folium.LayerControl().add_to(m)

meanScores = [row[0]*(1-row[1]) for row in results]

averaged_scores = [average(allChunkScores[index], axis=0) for index in range(len(allChunkScores))]
fishing_scores = [row[0] for row in averaged_scores]
depth_scores = [row[1] for row in averaged_scores]
incidents_scores = [row[2] for row in averaged_scores]
corals_scores = [row[3] for row in averaged_scores]
power_scores = [row[4] for row in averaged_scores]
distance_scores = [row[5] for row in averaged_scores]
overall_scores = [row[6] for row in averaged_scores]

chunkIndex = 0
for chunk in chunks:
    chunk_top_left = (chunk[0][0], chunk[1][1])
    chunk_top_right = chunk[0]
    chunk_bottom_left = chunk[1]
    chunk_bottom_right = (chunk[1][0], chunk[0][1])

    # Adding chunks in
    # Mean chunk
    color = '#%02x%02x%02x' % pseudocolor(meanScores[chunkIndex], min(meanScores), max(meanScores))
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

    # Fishing chunk
    color = '#%02x%02x%02x' % pseudocolor(fishing_scores[chunkIndex], 0, 1)
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = fishing_scores[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(fishingScoreChunks)

    # Depth chunk
    color = '#%02x%02x%02x' % pseudocolor(depth_scores[chunkIndex], 0, 1)
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = depth_scores[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(depthScoreChunks)

    # Incidents chunk
    color = '#%02x%02x%02x' % pseudocolor(incidents_scores[chunkIndex], 0, 1)
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = incidents_scores[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(incidentsScoreChunks)

    # Coral chunk
    color = '#%02x%02x%02x' % pseudocolor(corals_scores[chunkIndex], 0, 1)
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = corals_scores[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(coralScoreChunks)

    # Power chunk
    color = '#%02x%02x%02x' % pseudocolor(power_scores[chunkIndex], 0, 1)
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = power_scores[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(powerScoreChunks)

    # Distance chunk
    color = '#%02x%02x%02x' % pseudocolor(distance_scores[chunkIndex], 0, 1)
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = distance_scores[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(distanceScoreChunks)

    # Overall chunk
    color = '#%02x%02x%02x' % pseudocolor(overall_scores[chunkIndex], min(overall_scores), max(overall_scores))
    folium.vector_layers.Polygon(
        locations = [chunk_top_left, 
                    chunk_top_right, 
                    chunk_bottom_right, 
                    chunk_bottom_left
                    ],
        popup = overall_scores[chunkIndex],
        color = 'gray',
        fill_color = color
    ).add_to(overallScoreChunks)

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
m.add_child(fishingScoreChunks)
m.add_child(depthScoreChunks)
m.add_child(incidentsScoreChunks)
m.add_child(coralScoreChunks)
m.add_child(powerScoreChunks)
m.add_child(distanceScoreChunks)
m.add_child(overallScoreChunks)

m.save("index.html")

print("Done!")