import librosa
import librosa.display
import IPython.display as ipd
from ipywidgets import widgets
import matplotlib.pyplot as plt
import glob
import numpy as np
from array import *
import sklearn
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as pp

audio_files = glob.glob('./audio/*.wav')

b = list()
mfcc_originals = list() #for plotting
chroma_originals = list() #for plotting


#Song filepath: B[i][0]
#Raw Song: B[i][1]
#Song_harmonic: B[i][2]
#Song_percussive: B[i][3]
#Tempo: B[i][4]
#Chromagram: B[i][5]
#mfcc1: B[i][6]
#beat features: B[i][7]
#beat chroma: B[i][8]
#chroma_cq: B[i][9]
#mfcc2: B[i][10]
#mfcc_chroma: B[i][11]
#mfcc_chroma_tempo: B[i][11]
#mfcc_tempo: B[i][11]
#chroma_tempo: B[i][11]


fs = 44100
for i in range(0,len(audio_files)):
    #create list to store song data
    song_data = list()
    b.append(song_data)
    b[i].append(audio_files[i])

    #create unique song tag
    song = 'song' + str(i)

    #load the song data
    song, sr = librosa.load(audio_files[i], duration = 30)

    #set hop length
    hop_length = 512

    #separate song into harmonic and percussive components
    song_harmonic, song_percussive = librosa.effects.hpss(song)

    #beat track on the percussive signal
    tempo, beat_frames = librosa.beat.beat_track(y=song_percussive,
                                                 sr=sr)
    tempo = [tempo]

    # compute mfcc features from the raw signal
    mfcc1 = librosa.feature.mfcc(y=song, sr=sr, hop_length=hop_length, n_mfcc=13)

    # And the first-order differences (delta features)
    mfcc_delta = librosa.feature.delta(mfcc1)

    # Stack and synchronize between beat events
    # This time, we'll use the mean value (default) instead of median
    beat_mfcc_delta = librosa.util.sync(np.vstack([mfcc1, mfcc_delta]),
                                        beat_frames)


    #calculate a chromagram from the harmonic component
    chromagram = librosa.feature.chroma_cqt(y=song_harmonic,
                                            sr=sr)

    #synchronize chroma and beat frames (beat events)
    beat_chroma = librosa.util.sync(chromagram,
                                    beat_frames,
                                    aggregate=np.median)

    # Finally, stack all beat-synchronous features together
    beat_features = np.vstack([beat_chroma, beat_mfcc_delta])

    #add the song to the song data list
    b[i].append(song)
    b[i].append(song_harmonic)
    b[i].append(song_percussive)
    b[i].append(tempo)
    b[i].append(chromagram)
    b[i].append(mfcc1)
    b[i].append(beat_features)
    b[i].append(beat_chroma)


    #extract chroma feature and add to feature list
    chroma_cq_og = np.array(librosa.feature.chroma_cqt(b[i][1], sr=sr))
    chroma_originals.append(chroma_cq_og)
    chroma_cq = chroma_cq_og.reshape(15504)
    b[i].append(chroma_cq)

    #extract mfccs and add to feature list
    mfcc_og = np.array(librosa.feature.mfcc(b[i][1], sr=sr))
    mfcc_originals.append(mfcc_og)
    mfcc2 = mfcc_og.reshape(25840)
    b[i].append(mfcc2)

    tempo = np.array(tempo)
    mfcc_chroma = np.concatenate([mfcc2, chroma_cq])
    mfcc_chroma_tempo = np.concatenate([mfcc_chroma, tempo])
    mfcc_tempo = np.concatenate([mfcc2, tempo])
    chroma_tempo = np.concatenate([chroma_cq, tempo])
    b[i].append(mfcc_chroma)
    b[i].append(mfcc_chroma_tempo)
    b[i].append(mfcc_tempo)
    b[i].append(chroma_tempo)

mfcc_total = []
for i in range(len(b)):
    x = b[i][10]
    #print(x)

    #y = np.concatenate(x, b[i][9])
    mfcc_total.append(b[i][10])
    #mfcc_total.append(y)

mfcc_total = np.array(mfcc_total)

#mfcc_chroma
mfcc_chroma_total = []
for i in range(len(b)):
    mfcc_chroma_total.append(b[i][11])

mfcc_chroma_total = np.array(mfcc_chroma_total)

#mfcc_chroma_tempo
mfcc_chroma_tempo_total = []
for i in range(len(b)):
    mfcc_chroma_tempo_total.append(b[i][12])

mfcc_chroma_tempo_total = np.array(mfcc_chroma_tempo_total)

#mfcc_tempo
mfcc_tempo_total = []
for i in range(len(b)):
    mfcc_tempo_total.append(b[i][13])

mfcc_tempo_total = np.array(mfcc_tempo_total)

#chroma_tempo
chroma_tempo_total = []
for i in range(len(b)):
    chroma_tempo_total.append(b[i][14])

chroma_tempo_total = np.array(chroma_tempo_total)

tempo_total = []
for i in range(len(b)):
    tempo_total.append(b[i][4])
tempo_total = np.array(tempo_total)

chroma_total = []
for i in range(len(b)):
    chroma_total.append(b[i][9])
chroma_total = np.array(chroma_total)

x1 = []
for i in range(len(b)):
    x1.append(np.linspace(0, 1, 15504))
x1 = np.array(x1)

x2 = []
for i in range(len(b)):
    x2.append(np.linspace(0, 1, 25840))
x2 = np.array(x2)

#kmeans with mfcc
kmeans = KMeans(n_clusters=6, max_iter=100).fit(mfcc_total)
for j in range(6):
    print("mfcc cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans.labels_ == j)[0])):
        song_index = np.where(kmeans.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end = "\n")

mfcc_songs_cluster1 = np.where(kmeans.labels_ == 0)[0]
plt.figure(figsize= (20,8 ))
plt.suptitle('MFCC Cluster 1', fontsize=16)
for i in range(len(mfcc_songs_cluster1)):
    plt.subplot(len(mfcc_songs_cluster1),1,i+1)
    librosa.display.specshow(mfcc_originals[mfcc_songs_cluster1[i]], x_axis='time')
    subtitle = "MFCC of Song " + str(mfcc_songs_cluster1[i])
    plt.title(subtitle)
    plt.colorbar()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

#show mfcc's of songs in each cluster using mfcc
mfcc_songs_cluster2 = np.where(kmeans.labels_ == 1)[0]
plt.figure(figsize= (20,8 ))
plt.suptitle('MFCC Cluster 2', fontsize=16)
for i in range(len(mfcc_songs_cluster2)):
    plt.subplot(len(mfcc_songs_cluster2),1,i+1) # dynamically create subplots
    librosa.display.specshow(mfcc_originals[mfcc_songs_cluster2[i]], x_axis='time') #create mfcc
    subtitle = "MFCC of Song " + str(mfcc_songs_cluster2[i])
    plt.title(subtitle)
    plt.colorbar()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

mfcc_songs_cluster3 = np.where(kmeans.labels_ == 2)[0]
plt.figure(figsize= (20,8 ))
plt.suptitle('MFCC Cluster 3', fontsize=16)
for i in range(len(mfcc_songs_cluster3)):
    plt.subplot(len(mfcc_songs_cluster3),1,i+1)
    librosa.display.specshow(mfcc_originals[mfcc_songs_cluster3[i]], x_axis='time')
    subtitle = "MFCC of Song " + str(mfcc_songs_cluster3[i])
    plt.title(subtitle)
    plt.colorbar()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

#kmeans with tempo
kmeans2 = KMeans(n_clusters=6, max_iter=100).fit(tempo_total)
for j in range(6):
    print("tempo cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans2.labels_ == j)[0])):
        song_index = np.where(kmeans2.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")



tempoc1y = []
for i in range(len(tempo_total[kmeans2.labels_ == 0])):
    tempoc1y.append(2)
tempoc2y = []
for i in range(len(tempo_total[kmeans2.labels_ == 1])):
    tempoc2y.append(2)
tempoc3y = []
for i in range(len(tempo_total[kmeans2.labels_ == 2])):
    tempoc3y.append(2)
tempoclustery = [2,2,2,2,2,2]
fig1, ax1 = plt.subplots()
ax1.scatter(tempo_total[kmeans2.labels_ == 0], tempoc1y, c= 'green')
ax1.scatter(tempo_total[kmeans2.labels_ == 1], tempoc2y, c= 'blue')
ax1.scatter(tempo_total[kmeans2.labels_ == 2], tempoc3y, c= 'black')
ax1.scatter(kmeans2.cluster_centers_, tempoclustery, marker='*', c = 'red')
ax1.get_yaxis().set_visible(False)



#kmeans with chroma
kmeans3 = KMeans(n_clusters=6, max_iter=100).fit(chroma_total)
for j in range(6):
    print("chroma cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans3.labels_ == j)[0])):
        song_index = np.where(kmeans3.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")

#kmeans with mfcc and chroma
kmeans4 = KMeans(n_clusters=6, max_iter=100).fit(mfcc_chroma_total)
for j in range(6):
    print("mfcc & chroma cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans4.labels_ == j)[0])):
        song_index = np.where(kmeans4.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")

#kmeans with mfcc and chroma and tempo
kmeans5 = KMeans(n_clusters=6, max_iter=100).fit(mfcc_chroma_tempo_total)
for j in range(6):
    print("mfcc & chroma & tempo cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans5.labels_ == j)[0])):
        song_index = np.where(kmeans5.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")

#kmeans with mfcc and tempo
kmeans6 = KMeans(n_clusters=6, max_iter=100).fit(mfcc_tempo_total)
for j in range(6):
    print("mfcc & tempo cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans6.labels_ == j)[0])):
        song_index = np.where(kmeans6.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")

#kmeans with chroma and tempo
kmeans7 = KMeans(n_clusters=6, max_iter=100).fit(chroma_tempo_total)
for j in range(6):
    print("chroma & tempo cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans7.labels_ == j)[0])):
        song_index = np.where(kmeans7.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")

#plot chroma_cq
plt.figure()
plt.suptitle("overall chroma")
plt.subplot(2,1,1)
librosa.display.specshow(chroma_originals[0], y_axis='chroma')
plt.title('chroma_cq1')
plt.colorbar()
plt.subplot(2,1,2)
librosa.display.specshow(chroma_originals[1], y_axis='chroma', x_axis='time')
plt.title('chroma_cq2')
plt.colorbar()
plt.tight_layout()
plt.show()

#plot mfcc
plt.figure(figsize=(10, 4))
librosa.display.specshow(mfcc_originals[0], x_axis='time')
plt.colorbar()
plt.title('MFCC')
plt.tight_layout()
plt.show()



###########################
###Chroma Plot###

chroma_plot = np.zeros(12*21).reshape(21,12)

chroma_total = []
for i in range(len(b)):

    x = b[i][5]

    chroma_total.append(b[i][5])

    numberOfWindows = b[i][5].shape[1] #A

    freqVal = b[i][5].argmax( axis = 1 ) #B

    histogram, bin = np.histogram( freqVal, bins = 12 ) #C

    normalized_hist = histogram.reshape( 1, 12 ).astype( float ) / numberOfWindows #D

    chroma_plot[i] = normalized_hist


#kmeans with chroma
kmeans3 = KMeans(n_clusters=6, max_iter=1000).fit(chroma_plot)
for j in range(6):
    print("chroma cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans3.labels_ == j)[0])):
        song_index = np.where(kmeans3.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")


plt.scatter(chroma_plot[kmeans3.labels_==0,0], chroma_plot[kmeans3.labels_==0,1], c='b')
plt.scatter(chroma_plot[kmeans3.labels_==1,0], chroma_plot[kmeans3.labels_==1,1], c='r')
plt.scatter(chroma_plot[kmeans3.labels_==2,0], chroma_plot[kmeans3.labels_==2,1], c='y')
plt.scatter(chroma_plot[kmeans3.labels_==3,0], chroma_plot[kmeans3.labels_==3,1], c='g')
plt.scatter(chroma_plot[kmeans3.labels_==4,0], chroma_plot[kmeans3.labels_==4,1], c='k')
plt.scatter(chroma_plot[kmeans3.labels_==5,0], chroma_plot[kmeans3.labels_==5,1], c='c')
plt.scatter(chroma_plot[kmeans3.labels_==6,0], chroma_plot[kmeans3.labels_==6,1], c='c')
plt.scatter(chroma_plot[kmeans3.labels_==7,0], chroma_plot[kmeans3.labels_==7,1], c='c')
plt.xlabel('Frequency of Note x')
plt.ylabel('Frequency of Note y')
plt.legend(('Class 0', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7'))
plt.show()



#############################
#Kmeans with chroma, tempo, and mfcc_chroma

mfcc_plot = np.zeros(13*21).reshape(21,13)

mfcc_total = []
for i in range(len(b)):

    mfcc_total.append(b[i][6])

    avgMfcc = b[i][6].mean( axis = 1 ) #B

    mfcc_plot[i] = avgMfcc


tempo_total = []
for i in range(len(b)):
    tempo_total.append(b[i][4])
tempo_total = np.array(tempo_total)


mfcc_chroma_tempo = np.concatenate((mfcc_plot, chroma_plot, tempo_total), axis = 1)



#kmeans with mfcc_chroma_tempo
kmeans10 = KMeans(n_clusters=8, max_iter=1000).fit(mfcc_chroma_tempo)
for j in range(8):
    print("chroma average and mfcc average and tempo cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans10.labels_ == j)[0])):
        song_index = np.where(kmeans10.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")


plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==0,0], mfcc_chroma_tempo[kmeans10.labels_==0,1], c='b')
plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==1,0], mfcc_chroma_tempo[kmeans10.labels_==1,1], c='r')
plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==2,0], mfcc_chroma_tempo[kmeans10.labels_==2,1], c='y')
plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==3,0], mfcc_chroma_tempo[kmeans10.labels_==3,1], c='g')
plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==4,0], mfcc_chroma_tempo[kmeans10.labels_==4,1], c='k')
plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==5,0], mfcc_chroma_tempo[kmeans10.labels_==5,1], c='c')
plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==6,0], mfcc_chroma_tempo[kmeans10.labels_==6,1], c='c')
plt.scatter(mfcc_chroma_tempo[kmeans10.labels_==7,0], mfcc_chroma_tempo[kmeans10.labels_==7,1], c='c')
plt.xlabel('Frequency of Note x')
plt.legend(('Class 0', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7'))
plt.show()



#Kmeans with beat features

beat_features_plot = np.zeros(38*21).reshape(21,38)

beat_features_total = []
for i in range(len(b)):

    beat_features_total.append(b[i][7])

    avgBeatFeatures = b[i][7].mean( axis = 1 ) #B

    beat_features_plot[i] = avgBeatFeatures



#kmeans with beat features
kmeans11 = KMeans(n_clusters=8, max_iter=1000).fit(beat_features_plot)
for j in range(8):
    print("chroma cluster " + str(j+1) + ": ", end = "")
    for i in range(len(np.where(kmeans11.labels_ == j)[0])):
        song_index = np.where(kmeans11.labels_ == j)[0][i]
        song_path = audio_files[song_index]
        song = song_path[8:-4]
        print(song, end = ", ")
    print("", end ="\n")


plt.scatter(beat_features_plot[kmeans11.labels_==0,0], beat_features_plot[kmeans11.labels_==0,1], c='b')
plt.scatter(beat_features_plot[kmeans11.labels_==1,0], beat_features_plot[kmeans11.labels_==1,1], c='r')
plt.scatter(beat_features_plot[kmeans11.labels_==2,0], beat_features_plot[kmeans11.labels_==2,1], c='y')
plt.scatter(beat_features_plot[kmeans11.labels_==3,0], beat_features_plot[kmeans11.labels_==3,1], c='g')
plt.scatter(beat_features_plot[kmeans11.labels_==4,0], beat_features_plot[kmeans11.labels_==4,1], c='k')
plt.scatter(beat_features_plot[kmeans11.labels_==5,0], beat_features_plot[kmeans11.labels_==5,1], c='c')
plt.scatter(beat_features_plot[kmeans11.labels_==6,0], beat_features_plot[kmeans11.labels_==6,1])
plt.scatter(beat_features_plot[kmeans11.labels_==7,0], beat_features_plot[kmeans11.labels_==7,1])
plt.xlabel('Frequency of Note x')
plt.ylabel('Frequency of Note y')
plt.legend(('Class 0', 'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7'))
plt.show()
