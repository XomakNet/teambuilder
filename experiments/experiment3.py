from sklearn.cluster import KMeans
from math import *

from models.clusterings import Clusterings
from utils.data_reader import DataReader
from utils.metrics import TeamMetric
from utils.visualization import users_index_sets_to_users_sets, show_users_sets

CLUSTERS_COUNT = 5


def cluster_users_using_kmeans(reader, clustered_users, clusters_number, lists_count):
    kmeans = KMeans(n_clusters=clusters_number)
    clustering = Clusterings(clusters_number)
    all_users = reader.get_all_users()

    for list_number in range(0, lists_count):
        features_matrix = get_matrix_by_list_for_not_clustered_users(all_users, list_number, clustered_users)
        clusters_list = kmeans.fit_predict(features_matrix)
        clustering.add_clustering_for_list(convert_clusters_list_to_users_sets(reader, clusters_list, clustered_users),
                                           list_number)

    return clustering


def convert_clusters_list_to_users_sets(reader, clusters_array, clustered_users=None):
    """
    Converts clusters list, got from scikit to the sets of users' indexes
    It's taken into account, that users with some indexes can be already clustered.
    If clustered_users ==[user_with_index_3, user_with_index_4, user_with_index_5] and clusters_array == [0 0 0 1 2 2 3]
    it will produce [[user_with_index_0, user_with_index_1, user_with_index_2],
                     [user_with_index_6],
                     [user_with_index_7, user_with_index_8],
                     [user_with_index_9]]
    :param reader: DataReader object for finding users' indexes
    :param clusters_array: Array of clusters' ids
    :param clustered_users: Array of users, which have been already clustered
    :return: List of users' teams
    """

    if clustered_users is None:
        clustered_users = []

    clusters_number = max(clusters_array) + 1
    teams = [[] for i in range(0, clusters_number)]
    indexes_of_clustered_users = [reader.get_user_index_by_id(user.get_id()) for user in clustered_users]

    for user, cluster in enumerate(clusters_array):
        curr_index = user

        while curr_index in indexes_of_clustered_users:
            curr_index += 1

        indexes_of_clustered_users.append(curr_index)
        teams[cluster].append(reader.get_user_by_index(curr_index))

    return teams


def get_matrix_by_list_for_not_clustered_users(all_users, list_number, clustered_users=None):
    """
    Create the matrix of the features for users which id doesn't appear in clustered_users
    Matrix is creating only for the list with number = list_number
    :param all_users: list of User objects
    :param list_number: number of the criteria (from 0)
    :param clustered_users: list of the users which have already been clustered
    :return: matrix of the not-clustered users' features for the list with number = list_number
    """

    if clustered_users is None:
        clustered_users = []
    result_matrix = []

    for user in all_users:
        if user not in clustered_users:
            result_matrix.append(user.get_lists()[list_number])

    return result_matrix


def get_not_clustered_users_count(reader, clustered_users=None):
    """
    Returns count of the users which id doesn't appear in clustered_users_ids
    :param all_users: list of the User objects
    :param clustered_users: list of the users which have already been clustered
    :return: count of the not-clustered users
    """

    if clustered_users is None:
        clustered_users = []

    return len(set(reader.get_all_users()).difference(set(clustered_users)))  # length(all_users EXCEPT clustered_users)


def kick_user_from_cluster(cluster):
    """
    Finding "the weakest node" in the cluster and remove it.
    "The weakest node" - the user, which has the weakest relations with the other users in the cluster.
    Relations with other users mean mutual normalized vector distances between each pair of users by ALL lists (:D)
    :param cluster: list of the users' indexes
    :return:
    """
    # Finding an user for kicking
    # user = None
    #
    # cluster.remove(user)
    # return cluster


def experiment3(clusters_number, lists_count):
    result_clusters = []
    is_all_clustered = False
    reader = DataReader()  # "../data/test1.json"
    clustered_users = []

    while not is_all_clustered:

        # Clustering
        clusterings = cluster_users_using_kmeans(reader, clustered_users, clusters_number, lists_count)

        # Displaying info about the clustering (temporary)
        print("\nClustering by list %s" % 1)
        show_users_sets(clusterings.get_clustering_by_list_number(0))
        print("Clustering by list %s" % 2)
        show_users_sets(clusterings.get_clustering_by_list_number(1))
        print("\n")

        # Find the maximum common part of the clusters of the different lists
        new_cluster = clusterings.get_max_common_part_of_clusterings()

        # Is it necessary to kick the user?
        max_cluster_size = ceil(get_not_clustered_users_count(reader, clustered_users) / clusters_number)
        # while len(new_cluster) > max_cluster_size:
        #     new_cluster = kick_user_from_cluster(new_cluster)

        # Remember users which have been clustered
        clustered_users.extend(new_cluster)

        # Save cluster and reduce required clusters number
        result_clusters.append(new_cluster)
        clusters_number -= 1

        # Check the terminal condition
        is_all_clustered = True if len(result_clusters) >= CLUSTERS_COUNT else False

    # Display final clusters
    print("Final clusters:")
    show_users_sets(result_clusters)

    # Display final clusters metrics
    for user_set in result_clusters:
        metric = TeamMetric(set(user_set))
        print(metric)


if __name__ == '__main__':
    experiment3(CLUSTERS_COUNT, 2)
