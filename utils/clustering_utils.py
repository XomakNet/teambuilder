from typing import List

from sklearn.cluster import KMeans
from sklearn.cluster import SpectralClustering

from models.clusterings import Clusterings
from models.user import User
from utils.data_reader import DataReader
from utils.math import get_average_mutual_distances, avg


class ClusteringTools:
    KMEANS = "k-means"
    SPECTRAL = "spectral"

    @classmethod
    def build_clustering_tool(cls, clusters_count: int, max_cluster_size: int, tool_type: str):
        """

        :param clusters_count:
        :param max_cluster_size:
        :param tool_type:
        :return:
        """
        if tool_type == cls.KMEANS:
            return cls._build_kmeans_tool(clusters_count)
        elif tool_type == cls.SPECTRAL:
            return cls._build_spectral_tool(clusters_count, max_cluster_size)
        else:
            raise ValueError("Error creating clustering tool: wrong tool_type %s" % tool_type)

    @classmethod
    def _build_kmeans_tool(cls, clusters_count):
        """

        :param clusters_count:
        :return:
        """
        tool = KMeans(clusters_count)
        return tool

    @classmethod
    def _build_spectral_tool(cls, clusters_count, max_cluster_size):
        """

        :param clusters_count:
        :param max_cluster_size:
        :return:
        """
        tool = SpectralClustering(clusters_count, affinity='nearest_neighbors', n_neighbors=max_cluster_size)
        return tool


def cluster_users(clustering_tool, reader: DataReader, clustered_users: List[User], clusters_number: int,
                  lists_count: int) -> Clusterings:
    """
    Cluster users by lists with numbers from 0 to given lists_count.
    Users are stiling from the reader object.
    In result clusters appears all user from the reader except users in clustered_users.
    :param clustering_tool: tool from sci-kit for clustering
    :param reader: DataReader object
    :param clustered_users: list of users that won't appear in clusterings
    :param clusters_number: expected number of clusters
    :param lists_count: cluster by lists from 1 to lists_count
    :return: Clusterings object, representing clusterings by different lists
    """
    clustering = Clusterings(clusters_number)
    all_users = reader.get_all_users()

    for list_number in range(0, lists_count):
        features_matrix = get_matrix_by_list_for_not_clustered_users(all_users, list_number, clustered_users)
        clusters_list = clustering_tool.fit_predict(features_matrix)
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

    print("Min distance: %f" % min(users_mutual_distances))

    for user_index, user_distance in enumerate(users_mutual_distances):
        if user_distance == min(users_mutual_distances):
            print("Kicked user %d" % cluster[user_index].get_id())
            cluster.remove(cluster[user_index])
            users_mutual_distances.remove(user_distance)
            break

    users_mutual_distances = get_average_mutual_distances(cluster, lists_count)
    for user_index, user_distance in enumerate(users_mutual_distances):
        print("User #%d distance: %f; " % (cluster[user_index].get_id(), user_distance))

    return cluster


def balance_after_clustering(clusters, not_clustered_users_set, lists_count, max_cluster_size):
    """
    Distributes all users from not_clustered_users_set to clusters
    :param clusters: clustering - list of clusters
    :param not_clustered_users_set: list of not-clustered users
    :param lists_count: count of lists by which users have been clustered
    :param max_cluster_size: maximal count of users in a cluster
    :return: balanced clusters
    """

    while len(not_clustered_users_set) > 0:

        # Sort clusters by ascending of the items count in them
        clusters = sorted(clusters, key=lambda c: len(c))

        # For each user, find it's distance value for each cluster
        users_mutual_distances_in_clusters = {
            user.get_id(): {clust_index: avg(get_average_mutual_distances(clusters[clust_index] + [user], lists_count))
                            for clust_index in range(0, len(clusters)) if
                            not is_cluster_full(clusters[clust_index], max_cluster_size)}
            for user in not_clustered_users_set}

        # Put suitable user in the smallest cluster
        for cluster_index in range(0, len(clusters)):

            if not is_cluster_full(clusters[cluster_index], max_cluster_size):

                suitable_user_id, max_user_distance = None, -100

                # Find id of the suitable user for the cluster
                for user_id, clusters_distances in users_mutual_distances_in_clusters.items():
                    for user_cluster_index, user_distance in clusters_distances.items():

                        print("User #%d; Distances in cluster #%s: %f" % (
                            user_id, str([user.get_id() for user in clusters[user_cluster_index]]), user_distance))

                        if cluster_index == user_cluster_index and user_distance > max_user_distance:
                            suitable_user_id = user_id
                            max_user_distance = user_distance
                    print()

                # Put it user to the cluster and
                # escape from the cycle for recomputing mutual distances in clusters
                if suitable_user_id:
                    print("User #%d to cluster %s\n" %
                          (suitable_user_id, str([user.get_id() for user in clusters[cluster_index]])))
                    suitable_user = get_user_by_id(not_clustered_users_set, suitable_user_id)
                    clusters[cluster_index].append(suitable_user)
                    not_clustered_users_set.remove(suitable_user)
                    break
                else:
                    raise ValueError("Error balancing clusters")

    return clusters


def get_user_by_id(users_set, user_id):
    for user in users_set:
        if user.get_id() == user_id:
            return user

    return None


def is_cluster_full(cluster, max_cluster_size):
    return len(cluster) >= max_cluster_size
