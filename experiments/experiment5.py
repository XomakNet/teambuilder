from numpy.core.multiarray import zeros
from sklearn.cluster import AgglomerativeClustering

from experiments.experiment5.balancer import Balancer
from models.user import User
from utils.data_reader import DataReader
from utils.json_serializer import Serializer
from utils.metrics import normalized_vector_distance
from utils.visualization import users_index_sets_to_users_sets, clusters_list_to_users_index_sets

__author__ = 'Xomak'


reader = DataReader("../data/users.json")


def get_distance_between(user1: User, user2: User):
    negative_threshold = -0.3

    desires_coeff = 0
    if user2 in user1.get_selected_people():
        desires_coeff += 0.5
    if user1 in user2.get_selected_people():
        desires_coeff += 0.5

    first_lists = user1.get_lists()
    second_lists = user2.get_lists()
    lists_total = 0
    list_weight = 1/len(first_lists)
    for list_index in range(0, len(first_lists)):
        dst = normalized_vector_distance(first_lists[list_index], second_lists[list_index])
        if dst <= negative_threshold:
            dst = 0
        else:
            dst = (dst-negative_threshold)/(1-negative_threshold)
        lists_total += list_weight*dst

    return desires_coeff*0.5 + lists_total*0.5


def get_distance_between_ids(user1_id: int, user2_id: int):
    user1 = reader.get_user_by_id(user1_id)
    user2 = reader.get_user_by_id(user2_id)
    return get_distance_between(user1, user2)

def get_distances(matrix):
    users_number = len(matrix)
    affinity_matrix = zeros(shape=(users_number, users_number))
    for i in range(0, users_number):
        for j in range(i, users_number):
            if i != j:
                user1_id = matrix[i][0]
                user2_id = matrix[j][0]
                distance = get_distance_between_ids(user1_id, user2_id)
            else:
                distance = 1
            affinity_matrix[i, j] = 1 - distance
            affinity_matrix[j, i] = 1 - distance
    return affinity_matrix


agg = AgglomerativeClustering(n_clusters=3, affinity=get_distances, linkage="complete")
users = reader.get_all_users()
users_list = []
for user in users:
    users_list.append([user.get_id()])
r = agg.fit_predict(users_list)
sets = users_index_sets_to_users_sets(clusters_list_to_users_index_sets(r), reader)
b = Balancer(3, sets, get_distance_between)
b.balance()
Serializer.serialize_to_file(sets, "../web-visualiser/data.json")
