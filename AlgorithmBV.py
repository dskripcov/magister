import pickle
from geopy.distance import great_circle
import random as rand
import datetime


'''
with open('centroid_data_example2', 'rb') as f:
    data = pickle.load(f)
f.close()
#data.insert(0, [59.93495, 30.31165])
data.insert(0, [59.98487, 30.32899])
n = len(data)
'''


print(datetime.datetime.now())


def generate_matrix_symmetric(dimension):
    randmatrix = []
    for i in range(dimension):
        randmatrix.append([])
        for j in range(i + 1):
            if i == j:
                randmatrix[i].append(float('inf'))
            else:
                randmatrix[i].append(rand.randint(1, 100))
    for i in range(dimension):
        for j in range(i + 1, dimension):
            randmatrix[i].append(randmatrix[j][i])
    #print_matrix(randmatrix)
    return randmatrix


n = 500
matrix = generate_matrix_symmetric(n)
print("Matrix generated")
print(datetime.datetime.now())

'''
matrix = []
for i in range(n):
    matrix.append([])
    for j in range(i + 1):
        if i == j:
            matrix[i].append(float('inf'))
        else:
            matrix[i].append(great_circle((data[i][0], data[i][1]), (data[j][0], data[j][1])).kilometers)
for i in range(n):
    for j in range(i + 1, n):
        matrix[i].append(matrix[j][i])
'''

def print_matrix(matrix):
    for i in range(len(matrix)):
        print(matrix[i])
    print()


path_list = []
path_length = []


for i in range(n):
    path_list.append([i])
    path_length.append(0)
    current_point = i

    while True:
        min_range = float('inf')

        for j in range(n):
            if current_point != j and j not in path_list[i] and matrix[current_point][j] < min_range:
                min_range = matrix[current_point][j]
                next_point = j

        path_length[i] += matrix[current_point][next_point]
        path_list[i].append(next_point)

        current_point = next_point

        if len(path_list[i]) == n:
            path_length[i] += matrix[current_point][i]
            break

print("Closest neighbour method done")
print(datetime.datetime.now())


def calc_path_length(some_path, some_matrix):
    length = 0
    for i in range(len(some_path) - 1):
        length += some_matrix[some_path[i]][some_path[i+1]]


best_path = path_list[path_length.index(min(path_length))]
best_path_index = path_length.index(min(path_length))
best_length = min(path_length)
print("Начальный эталонный маршрут: №" + str(best_path_index + 1) + " " + str(best_path) +
      "\nс длинной: " + str(best_length))


bv_matrix = []
for i in range(n):
    bv_matrix.append([])
    for j in range(n):
        bv_matrix[i].append(0)


def create_bv_matrix():
    for path in path_list:
        for i in range(len(path) - 1):
            bv_matrix[path[i]][path[i + 1]] += 1
        bv_matrix[path[-1]][path[0]] += 1


create_bv_matrix()
print("bv-matrix created")

def bv_method(best_path, best_length):
    b_path = best_path.copy()
    b_length = best_length
    subcount = 0
    while True:
        count = 0
        best_res_1_to_4 = [[[], float('inf'), 0, 0], [[], float('inf'), 0, 0], [[], float('inf'), 0, 0], [[], float('inf'), 0, 0]]
        for i in range(n):
            for j in range(n):
                if bv_matrix[i][j] > 0:
                    res1 = bv_smoothing(b_path, i, j)
                    if res1[1] < best_res_1_to_4[0][1]:
                        best_res_1_to_4[0][0] = res1[0].copy()
                        best_res_1_to_4[0][1] = res1[1]
                        best_res_1_to_4[0][2] = i
                        best_res_1_to_4[0][3] = j

                    if abs(i - j) >= 2:
                        res2 = bv_transposition(b_path, i, j)
                        res4 = bv_inversion_transport(b_path, i, j)
                        if res2[1] < best_res_1_to_4[1][1]:
                            best_res_1_to_4[1][0] = res2[0].copy()
                            best_res_1_to_4[1][1] = res2[1]
                            best_res_1_to_4[1][2] = i
                            best_res_1_to_4[1][3] = j
                        if res4[1] < best_res_1_to_4[3][1]:
                            best_res_1_to_4[3][0] = res4[0].copy()
                            best_res_1_to_4[3][1] = res4[1]
                            best_res_1_to_4[3][2] = i
                            best_res_1_to_4[3][3] = j

                    if abs(i - j) >= 3:
                        res3 = bv_inversion_transition(b_path, i, j)
                        if res3[1] < best_res_1_to_4[2][1]:
                            best_res_1_to_4[2][0] = res3[0].copy()
                            best_res_1_to_4[2][1] = res3[1]
                            best_res_1_to_4[2][2] = i
                            best_res_1_to_4[2][3] = j

        best_of_all = [best_res_1_to_4[0][1], best_res_1_to_4[1][1], best_res_1_to_4[2][1], best_res_1_to_4[3][1]]

        if min(best_of_all) < b_length:
            b_length = min(best_of_all)
            b_path = best_res_1_to_4[best_of_all.index(min(best_of_all))][0].copy()
            bv_matrix[best_res_1_to_4[best_of_all.index(min(best_of_all))][2]][best_res_1_to_4[best_of_all.index(min(best_of_all))][3]] = 0
            count += 1
            subcount += 1

        if count == 0:
            break

    print("Всего " + str(subcount) + " модификаций.")
    return [b_path, b_length]


def bv_smoothing(b_path, index1, index2):
    path = b_path.copy()
    i = path.index(index1)
    j = path.index(index2)
    path[i] = index2
    path[j] = index1

    length = 0
    for k in range(len(path) - 1):
        length += matrix[path[k]][path[k+1]]
    length += matrix[path[-1]][path[0]]

    return [path, length]


def bv_transposition(b_path, index1, index2):
    path = b_path.copy()
    i = path.index(index1)
    j = path.index(index2)
    if i < j:
        for k in range(j - i):
            path[k+i] = path[k+i+1]
        path[j] = index1
    else:
        for k in range(i - j):
            path[k+j] = path[k+j+1]
        path[i] = index2

    length = 0
    for k in range(len(path) - 1):
        length += matrix[path[k]][path[k + 1]]
    length += matrix[path[-1]][path[0]]

    return [path, length]


def bv_inversion_transition(b_path, index1, index2):
    path = b_path.copy()
    i = path.index(index1)
    j = path.index(index2)
    if i < j:
        temp = []
        for k in range(j - i - 1):
            temp.insert(0, path[k+i+1])
        c = 1
        for elem in temp:
            path[i+c] = elem
            c += 1
    else:
        temp = []
        for k in range(i - j - 1):
            temp.insert(0, path[k+j+1])
        c = 1
        for elem in temp:
            path[j + c] = elem
            c += 1

    length = 0
    for k in range(len(path) - 1):
        length += matrix[path[k]][path[k + 1]]
    length += matrix[path[-1]][path[0]]

    return [path, length]


def bv_inversion_transport(b_path, index1, index2):
    path = b_path.copy()
    i = path.index(index1)
    j = path.index(index2)
    if i < j:
        temp = []
        for k in range(j - i + 1):
            temp.insert(0, path[k+i])
        c = 0
        for elem in temp:
            path[i+c] = elem
            c += 1
    else:
        temp = []
        for k in range(j - i + 1):
            temp.insert(0, path[k+j])
        c = 0
        for elem in temp:
            path[j+c] = elem
            c += 1

    length = 0
    for k in range(len(path) - 1):
        length += matrix[path[k]][path[k + 1]]
    length += matrix[path[-1]][path[0]]

    return [path, length]


the_answer = bv_method(best_path, best_length)

print("Лучший маршрут после BV-метода: " + str(the_answer[0]) + "\nс длинной: " +
      str(the_answer[1]))
print(datetime.datetime.now())
