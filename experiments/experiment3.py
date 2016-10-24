from math import *

from sklearn.cluster import KMeans

from models.clusterings import Clusterings
from utils.data_reader import DataReader
from utils.metrics import TeamMetric, normalized_vector_distance
from utils.visualization import show_users_sets

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


def get_not_clustered_users_set(reader, clustered_users=None):
    """
    Returns set of the users which haven't been clustered
    :param reader: data reader object for getting all users
    :param clustered_users: list of the users which have already been clustered
    :return: set of not-clustered users
    """

    if clustered_users is None:
        clustered_users = []

    return set(reader.get_all_users()).difference(set(clustered_users))  # all_users EXCEPT clustered_users


def get_average_mutual_distances(cluster, lists_count):
    """
    Calculate normalized average mutual distances for each user in a cluster
    :param cluster: list of users, which where grouped in cluster
    :param lists_count: count of lists, by which we're clustering
    :return:
    """
    users_mutual_distances = [0 for user in cluster]

    for user_number_1 in range(0, len(cluster) - 1):
        for user_number_2 in range(user_number_1 + 1, len(cluster)):

            distance_all_lists = 0
            for list_number in range(0, lists_count):
                curr_list_distance = normalized_vector_distance(cluster[user_number_1].get_lists()[list_number],
                                                                cluster[user_number_2].get_lists()[list_number])
                distance_all_lists += curr_list_distance

            users_mutual_distances[user_number_1] += distance_all_lists
            users_mutual_distances[user_number_2] += distance_all_lists

    return users_mutual_distances


def kick_user_from_cluster(cluster, lists_count):
    """
    Finding "the weakest node" in the cluster and remove it.
    "The weakest node" - the user, which has the weakest relations with the other users in the cluster.
    Relations with other users mean mutual normalized vector distances between each pair of users by ALL lists (:D)
    :param cluster: list of the users' indexes
    :param lists_count: count of the lists by which we're clustering
    :return: cluster without a user
    """
    # Calculate special metric for each user - the smaller it is, the less suitable is a user for the clusters
    users_mutual_distances = get_average_mutual_distances(cluster, lists_count)

    for user_index, user_distance in enumerate(users_mutual_distances):
        if user_distance == min(users_mutual_distances):
            print("Kicked user %d" % cluster[user_index].get_id())
            cluster.remove(cluster[user_index])
            break

    return cluster


def is_cluster_full(cluster, max_cluster_size):
    return len(cluster) >= max_cluster_size


def get_user_by_id(users_set, user_id):
    for user in users_set:
        if user.get_id() == user_id:
            return user

    return None


def avg(lst):
    if len(lst) == 0:
        return 0

    return sum(lst) / len(lst)


def balance_after_clustering(clusters, not_clustered_users_set, lists_count, max_cluster_size):
    if len(not_clustered_users_set) == 0:
        return clusters

    users_mutual_distances_in_clusters = {
        user.get_id(): {cluster_index: avg(get_average_mutual_distances(clusters[cluster_index] + [user], lists_count))
                        for cluster_index in range(0, len(clusters)) if
                        not is_cluster_full(clusters[cluster_index], max_cluster_size)}
        for user in not_clustered_users_set}

    for user_id, user_distances in users_mutual_distances_in_clusters.items():

        # Sorting by descending of the distance value (the best cluster index on the top)
        user_distances = {cluster_index: value for cluster_index, value in sorted(user_distances.items())}

        for cluster_index, distance in user_distances.items():
            if not is_cluster_full(clusters[cluster_index], max_cluster_size):
                clusters[cluster_index].append(get_user_by_id(not_clustered_users_set, user_id))
                break

    return clusters


def experiment3(clusters_number, lists_count):
    result_clusters = []
    is_all_clustered = False
    reader = DataReader()  # "../data/test1.json"
    clustered_users = []
    max_cluster_size = ceil(len(get_not_clustered_users_set(reader, clustered_users)) / clusters_number)

    while not is_all_clustered:

        # Clustering
        clusterings = cluster_users_using_kmeans(reader, clustered_users, clusters_number, lists_count)

        # Displaying info about the clustering (temporary)
        print("\nClustering by list %s" % 1)
        show_users_sets(clusterings.get_clustering_by_list_number(0))
        print("Clustering by list %s" % 2)
        show_users_sets(clusterings.get_clustering_by_list_number(1))

        # Find the maximum common part of the clusters of the different lists
        new_cluster = clusterings.get_max_common_part_of_clusterings()
        print("Common part: " + str([user.get_id() for user in new_cluster]))

        # Is it necessary to kick the user?
        while len(new_cluster) > max_cluster_size:
            new_cluster = kick_user_from_cluster(new_cluster, lists_count)

        # Remember users which have been clustered
        clustered_users.extend(new_cluster)

        # Save cluster and reduce required clusters number
        result_clusters.append(new_cluster)
        clusters_number -= 1

        # Check the terminal condition
        is_all_clustered = True if len(result_clusters) >= CLUSTERS_COUNT else False

    # Display clusters before balancing
    print("\nClusters before balancing:")
    show_users_sets(result_clusters)

    # Display clusters metrics
    for user_set in result_clusters:
        metric = TeamMetric(set(user_set))
        print(metric.get_final_metric_value())

    # There are clusters with more than maximum users? Fix it.
    result_clusters = balance_after_clustering(result_clusters,
                                               get_not_clustered_users_set(reader, clustered_users),
                                               lists_count,
                                               max_cluster_size)

    # Display final clusters
    print("\nFinal clusters:")
    show_users_sets(result_clusters)

    # Display final clusters metrics
    for user_set in result_clusters:
        metric = TeamMetric(set(user_set))
        print(metric.get_final_metric_value())


if __name__ == '__main__':
    experiment3(CLUSTERS_COUNT, 2)
