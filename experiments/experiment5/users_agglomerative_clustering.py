from typing import Set, List

from numpy import zeros, ndarray
from sklearn.cluster import AgglomerativeClustering

from experiments.experiment5.balancer import Balancer
from models.user import User
from utils.data_reader import DataReader
from utils.metrics import normalized_vector_distance
from utils.visualization import users_index_sets_to_users_sets, clusters_list_to_users_index_sets

__author__ = 'Xomak'


class UsersAgglomerativeClustering:
    """
    Skicit-learn AgglomerativeCustering-based algorithm
    """

    def __init__(self, reader: DataReader, teams_number: int, desires_weight: float=0.5,
                 lists_weights: List[float]=None, need_balance: bool=True):
        """
        Instantiates algorithm of users' clustering
        :param reader: Reader instance
        :param teams_number: Required teams number
        :param desires_weight: Weight of desires. Should be in range 0 - 1.
        :param lists_weights: Weights of lists. If empty, all lists will have same weight
        :param need_balance: Should teams be balanced
        """
        if lists_weights is not None and sum(lists_weights) > 1:
            raise ValueError("Sum of list weights is more than one.")
        self.desires_weight = desires_weight
        self.linkage = "average"
        self.reader = reader
        self.need_balance = need_balance
        self.lists_weight = lists_weights
        self.teams_number = teams_number
        self.negative_threshold = -0.3

    def get_affinity_between(self, user1: User, user2: User) -> float:
        """
        Calculates and return distance affinity two users. A lot of parameters from object's attributes are used.
        :param user1: User 1
        :param user2: User 2
        :return: float. The more float is, the more degree of affinity users have
        """

        desires_coeff = 0
        if user2 in user1.get_selected_people():
            desires_coeff += 0.5
        if user1 in user2.get_selected_people():
            desires_coeff += 0.5

        first_lists = user1.get_lists()
        second_lists = user2.get_lists()
        lists_total = 0

        list_weight = 1 / len(first_lists)
        for list_index in range(0, len(first_lists)):
            dst = normalized_vector_distance(first_lists[list_index], second_lists[list_index])
            if dst <= self.negative_threshold:
                dst = 0
            else:
                dst = (dst - self.negative_threshold) / (1 - self.negative_threshold)
            if self.lists_weight is not None:
                if list_index < len(self.lists_weight):
                    list_weight = self.lists_weight[list_index]
                else:
                    list_weight = 0
            lists_total += list_weight * dst

        return desires_coeff * self.desires_weight + lists_total * (1-self.desires_weight)

    def get_affinity_between_ids(self, user1_id: int, user2_id: int):
        """
        Calculates and return distance affinity two users. A lot of parameters from object's attributes are used.
        :param user1_id: User 1 id
        :param user2_id: User 2 id
        :return: float. The more float is, the more degree of affinity users have
        """
        user1 = self.reader.get_user_by_id(user1_id)
        user2 = self.reader.get_user_by_id(user2_id)
        return self.get_affinity_between(user1, user2)

    def get_affinity_matrix(self, matrix) -> ndarray:
        """
        Returns affinity matrix.
        According to the requirements of skicit-learn, the less affinity is, the more degree of affinity users have
        :param matrix: Matrix with samples and users
        :return: Affinity matrix
        """
        users_number = len(matrix)
        affinity_matrix = zeros(shape=(users_number, users_number))
        for i in range(0, users_number):
            for j in range(i, users_number):
                if i != j:
                    user1_id = matrix[i][0]
                    user2_id = matrix[j][0]
                    distance = self.get_affinity_between_ids(user1_id, user2_id)
                else:
                    distance = 1
                affinity_matrix[i, j] = 1 - distance
                affinity_matrix[j, i] = 1 - distance
        return affinity_matrix

    def clusterize(self) -> List[Set[User]]:
        """
        Performs clustering
        :return:
        """

        users = self.reader.get_all_users()
        users_list = []
        for user in users:
            users_list.append([user.get_id()])

        agg = AgglomerativeClustering(n_clusters=self.teams_number, affinity=self.get_affinity_matrix, linkage=self.linkage)
        r = agg.fit_predict(users_list)
        sets = users_index_sets_to_users_sets(clusters_list_to_users_index_sets(r), self.reader)
        if self.need_balance:
            b = Balancer(self.teams_number, sets, lambda user1, user2: self.get_affinity_between(user1, user2))
            b.balance()
        return sets
