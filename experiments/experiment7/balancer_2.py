from math import ceil

from utils.clustering_utils import get_user_by_id, is_cluster_full
from utils.math import get_average_mutual_distances, avg


class Balancer2:
    def __init__(self, required_teams_number, clusters, affinity_function):

        if len(clusters) != required_teams_number:
            raise NotImplementedError("Teams count balancing is not supported yet.")
        self.required_teams_number = required_teams_number
        self.affinity_function = affinity_function
        total_number = 0
        for cluster in clusters:
            total_number += len(cluster)
        self.max_cluster_size = int(ceil(total_number / required_teams_number))
        self.clusters = clusters
        self.not_clustered_users_set = []
        self._kick_overhead_users()

    def _kick_overhead_users(self):
        for cluster_index in range(0, len(self.clusters)):
            while len(self.clusters[cluster_index]) > self.max_cluster_size:
                self.clusters[cluster_index] = self._kick_user_from_cluster(self.clusters[cluster_index])

    def balance(self):
        """
        Distributes all users from not_clustered_users_set to clusters
        :return: balanced clusters
        """

        while len(self.not_clustered_users_set) > 0:

            # Sort clusters by ascending of the items count in them
            self.clusters = sorted(self.clusters, key=lambda c: len(c))

            # For each user, find it's distance value for each cluster
            users_mutual_distances_in_clusters = {
                user.get_id(): {
                    clust_index: avg(self._get_affinities_in_cluster(self.clusters[clust_index] + [user]))
                    for clust_index in range(0, len(self.clusters)) if
                    not is_cluster_full(self.clusters[clust_index], self.max_cluster_size)}
                for user in self.not_clustered_users_set}

            # Put suitable user in the smallest cluster
            for cluster_index in range(0, len(self.clusters)):

                if not is_cluster_full(self.clusters[cluster_index], self.max_cluster_size):

                    suitable_user_id, max_user_distance = None, -100

                    # Find id of the suitable user for the cluster
                    for user_id, clusters_distances in users_mutual_distances_in_clusters.items():
                        for user_cluster_index, user_distance in clusters_distances.items():

                            if cluster_index == user_cluster_index and user_distance > max_user_distance:
                                suitable_user_id = user_id
                                max_user_distance = user_distance

                    # Put it user to the cluster and
                    # escape from the cycle for recomputing mutual distances in clusters
                    if suitable_user_id:
                        suitable_user = get_user_by_id(self.not_clustered_users_set, suitable_user_id)
                        self.clusters[cluster_index].append(suitable_user)
                        self.not_clustered_users_set.remove(suitable_user)
                        break
                    else:
                        raise ValueError("Error balancing clusters")

        return self.clusters

    def _kick_user_from_cluster(self, cluster):
        """
        Finding "the weakest node" in the cluster and remove it.
        "The weakest node" - the user, which has the weakest relations with the other users in the cluster.
        :param cluster: list of the users' indexes
        :return: cluster without a user
        """
        # Calculate special metric for each user - the smaller it is, the less suitable is a user for the clusters
        users_mutual_distances = self._get_affinities_in_cluster(cluster)

        for user_index, user_distance in enumerate(users_mutual_distances):
            if user_distance == min(users_mutual_distances):

                self.not_clustered_users_set.append(cluster[user_index])

                cluster.remove(cluster[user_index])
                users_mutual_distances.remove(user_distance)
                break

        return cluster

    def _get_affinities_in_cluster(self, cluster):

        users_mutual_distances = [0 for user in cluster]

        for user_number_1 in range(0, len(cluster) - 1):
            for user_number_2 in range(user_number_1 + 1, len(cluster)):
                users_affinity = self.affinity_function(cluster[user_number_1], cluster[user_number_2])
                users_mutual_distances[user_number_1] += users_affinity
                users_mutual_distances[user_number_2] += users_affinity

        # Normalize affinities
        for user_index in range(0, len(cluster)):
            users_mutual_distances[user_index] /= (len(cluster) - 1)

        return users_mutual_distances
