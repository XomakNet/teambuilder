from sklearn.cluster import KMeans
from math import *
from utils.data_reader import DataReader
from utils.metrics import TeamMetric
from utils.visualization import users_index_sets_to_users_sets, show_users_sets

CLUSTERS_COUNT = 5


def convert_clusters_list_to_users_indexes_sets(clusters_array, clustered_users_indexes=None):
    """
    Converts clusters list, got from scikit to the sets of users' indexes
    It's taken into account, that users with some indexes can be already clustered.
    So, clustered_users_indexes == [3, 4, 5] and clusters_array == [0 0 0 1 2 2 3]
    will produce [[0, 1, 2], [6], [7, 8], [9]]
    :param clusters_array: Array of clusters' ids
    :param clustered_users_indexes: Array of users' indexes, which have been already clustered
    :return: List of lists with users' indexes
    """

    if clustered_users_indexes is None:
        clustered_users_indexes = []

    clusters_number = max(clusters_array) + 1
    teams = [[] for i in range(0, clusters_number)]
    exists_indexes = [i for i in clustered_users_indexes]

    for user, cluster in enumerate(clusters_array):
        curr_index = user

        while curr_index in exists_indexes:
            curr_index += 1

        exists_indexes.append(curr_index)
        teams[cluster].append(curr_index)

    return teams


def get_matrix_by_list_for_not_clustered_users(all_users, list_number, clustered_users_ids=None):
    """
    Create the matrix of the features for users which id doesn't appear in clustered_users_ids
    Matrix is creating only for the list with number = list_number
    :param all_users: list of User objects
    :param list_number: number of the criteria (from 0)
    :param clustered_users_ids: list of users' ids (which have already been clustered)
    :return: matrix of the not-clustered users' features for the list with number = list_number
    """

    if clustered_users_ids is None:
        clustered_users_ids = []
    result_matrix = []

    for user in all_users:
        user_id = user.get_id()
        if user_id not in clustered_users_ids:
            result_matrix.append(user.get_lists()[list_number])

    return result_matrix


def get_not_clustered_users_count(all_users, clustered_users_ids=None):
    """
    Returns count of the users which id doesn't appear in clustered_users_ids
    :param all_users: list of the User objects
    :param clustered_users_ids: list of the users' ids (which have already been clustered)
    :return: count of the not-clustered users
    """

    if clustered_users_ids is None:
        clustered_users_ids = []

    all_users_ids = [user.get_id() for user in all_users]
    return len(set(all_users_ids).difference(set(clustered_users_ids)))  # length(all_users EXCEPT clustered_users)


def kick_user_from_cluster(cluster):
    """
    Finding "the weakest node" in the cluster and remove it.
    "The weakest node" - the user, which has the weakest relations with the other users in the cluster.
    :param cluster: list of the users' indexes
    :return: modified cluster without one user
    """
    # Finding an user for kicking
    # user = None
    # cluster.remove(user)


def experiment3(clusters_number, lists_count):
    result_clusters = []
    is_all_clustered = False
    reader = DataReader()  # "../data/test1.json"
    all_users = reader.get_all_users()
    clustered_users_ids, clustered_users_indexes = [], []

    while not is_all_clustered:

        # Clustering
        max_cluster_size = ceil(get_not_clustered_users_count(all_users, clustered_users_ids) / clusters_number)
        kmeans = KMeans(n_clusters=clusters_number)
        clustering = []
        for list_number in range(0, lists_count):
            features_matrix = get_matrix_by_list_for_not_clustered_users(all_users, list_number, clustered_users_ids)
            clusters_list = kmeans.fit_predict(features_matrix)
            clustering.append(convert_clusters_list_to_users_indexes_sets(clusters_list, clustered_users_indexes))

        # Displaying info about the clustering
        print("\nClustering by list %s" % 1)
        show_users_sets(users_index_sets_to_users_sets(clustering[0], reader))
        print("Clustering by list %s" % 2)
        show_users_sets(users_index_sets_to_users_sets(clustering[1], reader))
        print("\n")

        # Find the maximum common part of the clusters of the different lists
        max_length_of_common_part = 0
        common_parts_for_debug = []
        new_cluster_indexes = []
        for list_number in range(0, len(clustering)):

            for list_number_2 in range(list_number + 1, len(clustering)):

                for cluster_number in range(0, len(clustering[list_number])):

                    for cluster_number_2 in range(0, len(clustering[list_number_2])):

                        # Find common part for two clusters from different lists
                        common_part_of_two_clusters = set(clustering[list_number][cluster_number]).intersection(
                            set(clustering[list_number_2][cluster_number_2]))

                        # Save the debugging information
                        common_parts_for_debug.append(
                            [clustering[list_number][cluster_number], clustering[list_number_2][cluster_number_2],
                             common_part_of_two_clusters, len(common_part_of_two_clusters)])

                        # Is length of the common part greater than length of the maximum common part?
                        if len(common_part_of_two_clusters) > max_length_of_common_part:
                            max_length_of_common_part = len(common_part_of_two_clusters)
                            new_cluster_indexes = list(common_part_of_two_clusters)     # remember new cluster

        # Display the debugging information
        print("Common parts of the clusters:")
        for part in common_parts_for_debug:
            print(str(part))
        print("Max common part: %s\nLength = %d\n\n" % (str(new_cluster_indexes), max_length_of_common_part))

        # Is it necessary to kick the user?
        while max_length_of_common_part > max_cluster_size:
            kick_user_from_cluster(new_cluster_indexes)
            max_length_of_common_part -= 1

        # Remember indexes of the clustered users
        clustered_users_indexes.extend(new_cluster_indexes)

        # Remember ids of the clustered users
        new_cluster_ids = users_index_sets_to_users_sets([new_cluster_indexes], reader)[0]
        clustered_users_ids.extend([user.get_id() for user in new_cluster_ids])

        # Save cluster and reduce required clusters number
        result_clusters.append(new_cluster_ids)
        clusters_number -= 1

        # Check the terminal condition
        is_all_clustered = True if len(result_clusters) >= CLUSTERS_COUNT else False

    # Display final clusters
    print("Final clusters:")
    show_users_sets(result_clusters)

    # Display final clusters metrics
    for user_set in result_clusters:
        metric = TeamMetric(user_set)
        print(metric)

if __name__ == '__main__':
    experiment3(CLUSTERS_COUNT, 2)
