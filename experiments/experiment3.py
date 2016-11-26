from math import *

import utils.clustering_utils as cu
from utils.data_reader import DataReader
from utils.json_serializer import Serializer
from utils.metrics import TeamMetric
from utils.visualization import show_users_sets


def experiment3(clustering_tool_type, clusters_number, input_data_file_name, lists_count):
    result_clusters = []
    is_all_clustered = False
    reader = DataReader(input_data_file_name)
    clustered_users = []
    users_count = len(cu.get_not_clustered_users_set(reader, clustered_users))
    max_cluster_size = int(ceil(users_count / clusters_number))

    while not is_all_clustered:

        # Get clusterings by lists
        clustering_tool = cu.ClusteringTools.build_clustering_tool(clusters_number, max_cluster_size,
                                                                   clustering_tool_type)
        clusterings = cu.cluster_users(clustering_tool, reader, clustered_users, clusters_number, lists_count)

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
            new_cluster = cu.kick_user_from_cluster(new_cluster, lists_count)

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
        if len(user_set) != 0:
            metric = TeamMetric(set(user_set))
            print(metric.get_final_metric_value())

    # There are clusters with more than maximum users? Fix it.
    result_clusters = cu.balance_after_clustering(result_clusters,
                                                  cu.get_not_clustered_users_set(reader, clustered_users),
                                                  lists_count,
                                                  max_cluster_size)

    # Display final clusters
    print("\nFinal clusters:")
    show_users_sets(result_clusters)

    # Display final clusters metrics
    final_metric_value = 0
    for user_set in result_clusters:
        metric = TeamMetric(set(user_set))
        final_metric_value += metric.get_final_metric_value()
        print(metric)

    return {"clusters": result_clusters, "metric": final_metric_value}


REPEATS_COUNT = 10
CLUSTERS_COUNT = 2
LISTS_COUNT = 2
INPUT_DATA_FILENAME = "../data/eltech-vector.json"
CLUSTERING_TOOL_TYPE = cu.ClusteringTools.KMEANS

if __name__ == '__main__':

    max_metric_value = 0
    max_metric_clusters = None

    for i in range(0, REPEATS_COUNT):
        experiment_result = experiment3(CLUSTERING_TOOL_TYPE, CLUSTERS_COUNT, INPUT_DATA_FILENAME, LISTS_COUNT)
        if experiment_result["metric"] > max_metric_value:
            max_metric_value = experiment_result["metric"]
            max_metric_clusters = experiment_result["clusters"]

    print(max_metric_value)
    Serializer.serialize_to_file(max_metric_clusters, "../web-visualiser/data.json")
