from math import ceil
from typing import List

import utils.clustering_utils as cu
from models.user import User
from utils.data_reader import DataReader
from utils.metrics import TeamMetric
from utils.visualization import show_users_sets


class ValuesClustering:
    def __init__(self, clustering_tool_type: str, reader: DataReader):
        self.reader = reader
        self.clustering_tool_type = clustering_tool_type

    def cluster(self, clusters_number: int, lists_count: int, accuracy: int=10) -> List[List[User]]:
        """
        Cluster users from reader into <clusters_number> clusters.
        Clustering is taking place by lists from 0 to <lists_count> - 1.
        Function uses clustering algorithm specified in <self._clustering_tool_type>.
        Clustering will be repeated <accuracy> times.
        Finally, list of clusters which has the best total metric value will be returned.
        :param clusters_number: number of clusters
        :param lists_count: count of lists by which users will be clustered
        :param accuracy: number of times algorithm will be applied
        :return: List of clusters. Every cluster represented as List of Users.
        """

        max_metric_value = 0
        max_metric_clusters = None

        for i in range(0, accuracy):
            experiment_result = self._cluster(clusters_number, lists_count)
            if experiment_result["metric"] > max_metric_value:
                max_metric_value = experiment_result["metric"]
                max_metric_clusters = experiment_result["clusters"]

        return max_metric_clusters

    def _cluster(self, clusters_number, lists_count):
        """
        Run clustering algorithm for <clusters_count> clusters.
        Clustering by <lists_count> lists.
        :param clusters_number: number of expected clusters
        :param lists_count: count of lists by which users will be clustered
        :return: Dictionary consisted total metric value and clustered
        """
        result_clusters = []
        is_all_clustered = False
        clustered_users = []
        users_count = len(cu.get_not_clustered_users_set(self.reader, clustered_users))
        max_cluster_size = ceil(users_count / clusters_number)

        remaining_clusters_number = clusters_number
        while not is_all_clustered:

            # Get clusterings by lists
            clustering_tool = cu.ClusteringTools.build_clustering_tool(remaining_clusters_number, int(max_cluster_size),
                                                                       self.clustering_tool_type)
            clusterings = cu.cluster_users(clustering_tool, self.reader, clustered_users, remaining_clusters_number,
                                           lists_count)

            # Find the maximum common part of the clusters of the different lists
            new_cluster = clusterings.get_max_common_part_of_clusterings()

            # Is it necessary to kick the user?
            while len(new_cluster) > max_cluster_size:
                new_cluster = cu.kick_user_from_cluster(new_cluster, lists_count)

            # Remember users which have been clustered
            clustered_users.extend(new_cluster)

            # Save cluster and reduce required clusters number
            result_clusters.append(new_cluster)
            remaining_clusters_number -= 1

            # Check the terminal condition
            is_all_clustered = True if len(result_clusters) >= clusters_number else False

        # Display clusters metrics
        for user_set in result_clusters:
            if len(user_set) != 0:
                metric = TeamMetric(set(user_set))

        # There are clusters with more than maximum users? Fix it.
        result_clusters = cu.balance_after_clustering(result_clusters,
                                                      cu.get_not_clustered_users_set(self.reader, clustered_users),
                                                      lists_count,
                                                      max_cluster_size)

        # Calculate final clusters metrics
        final_metric_value = 0
        for user_set in result_clusters:
            metric = TeamMetric(set(user_set))
            final_metric_value += metric.get_final_metric_value()

        return {"clusters": result_clusters, "metric": final_metric_value}
