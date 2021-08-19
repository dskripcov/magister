import csv
from geopy.distance import great_circle
from random import choice, uniform
import pickle
from copy import deepcopy


def create_centroid(points):
    sumLat = 0
    sumLong = 0
    for point in points:
        sumLat = sumLat + point[1]
        sumLong = sumLong + point[2]
    return [round(sumLat/len(points), 6), round(sumLong/len(points), 6)]


def clustering_quality(cluster_data):
    F = 0
    j = 0
    for cluster in cluster_data[1]:
        for point in cluster:
            F = F + great_circle((point[1], point[2]), (cluster_data[2][j][0], cluster_data[2][j][1])).kilometers
        j = j + 1
    return F


r_file = open("geooutput-example2.csv")
file_reader = csv.reader(r_file, delimiter=";")
r_data_const = list(file_reader)
r_data_const.pop(0)
r_data_const.pop(0)
r_dict_const = {}
for row in r_data_const:
    row[0] = int(row[0]) - 1
    row[3] = float(row[3])
    row[4] = float(row[4])
    row[5] = 0
    r_dict_const[row[0]] = [row[3], row[4], row[5]]
    row.pop(1)
    row.pop(1)
    for i in range(8):
        row.pop(4)

r_file.close()


w_data = []
count = 0
for row in r_data_const:
    for i in range(0, len(r_data_const)-row[0]):
        w_data.append([])
        w_data[count].append(row[0])
        w_data[count].append(r_data_const[row[0] + i][0])
        w_data[count].append(great_circle((row[1], row[2]), (r_data_const[row[0] + i][1], r_data_const[row[0] + i][2])).kilometers)
        count += 1

# --------------------------------- FOREL

R = 0.5

clusterList = []
centroidList = []
all_clusters = []
r_dict = []
r_data = []

for count in range(0, 1000):
    i = 0
    r_dict = r_dict_const.copy()
    r_data = r_data_const.copy()
    clusterList.clear()
    centroidList.clear()

    while True:
        if len(r_dict) == 0:
            break
        i = i + 1

        newCenterPointKey = choice(list(r_dict.keys()))

        r_data[newCenterPointKey - 1][3] = i

        del r_dict[newCenterPointKey]

        clusterList.append([])
        clusterList[i - 1].append(r_data[newCenterPointKey - 1])

        if len(r_dict) == 0:
            centroidList.append([r_data[newCenterPointKey - 1][1], r_data[newCenterPointKey - 1][2]])
            break

        for elem in w_data:
            if elem[0] == newCenterPointKey and elem[2] <= R and elem[1] in r_dict:
                r_data[elem[1] - 1][3] = i
                clusterList[i - 1].append(r_data[elem[1] - 1])
                del r_dict[elem[1]]
            elif elem[1] == newCenterPointKey and elem[2] <= R and elem[0] in r_dict:
                r_data[elem[0] - 1][3] = i
                clusterList[i - 1].append(r_data[elem[0] - 1])
                del r_dict[elem[0]]
            if len(r_dict) == 0:
                break

        centroidList.append(create_centroid(clusterList[i - 1]))

        while True:
            j = 0
            for key in deepcopy(r_dict):
                if great_circle(centroidList[i - 1], (r_data[key - 1][1], r_data[key - 1][2])).kilometers <= R:
                    j = j + 1
                    r_data[key - 1][3] = i
                    clusterList[i - 1].append(r_data[key - 1])
                    del r_dict[key]

            if j == 0:
                break
            else:
                centroidList[i - 1] = create_centroid(clusterList[i - 1])

    all_clusters.append([deepcopy(r_data), deepcopy(clusterList), deepcopy(centroidList)])
    all_clusters[-1].append(clustering_quality(all_clusters[-1]))


i = 0
min_val = float('inf')
min_clust = 0
min_len = 0
for data in all_clusters:
    i = i + 1

    if min_val > data[3]:
        min_val = data[3]
        min_clust = i
        min_len = len(data[1]) - 1


print("\nНаилучший результат показало разбиение №" + str(min_clust) +
      "\nсо значением функционала = " + str(min_val) +
      "\nи колличеством кластеров = " + str(min_len))

for cluster in all_clusters[min_clust - 1][1]:
    temp = ""
    for point in cluster:
        temp = temp + str(point[0]) + " "
    print("Кластер " + str(cluster[0][3]) + " включает точки с индексами: " + temp)

print("Центроиды кластеров: ")
i = 0
for centroid in all_clusters[min_clust - 1][2]:
    i += 1
    print("Центроид кластера " + str(i) + ": " + str(centroid))


with open('centroid_data_example2', 'wb') as f:
    pickle.dump(all_clusters[min_clust - 1][2], f)
f.close()

print("Создан файл centroid_data_example2 с данными о центроидах")

