from sklearn.cluster import KMeans
from math import *
from utils.data_reader import DataReader
from utils.metrics import calculate_set_metrics, print_metrics
from utils.visualization import clusters_list_to_users_index_sets, users_index_sets_to_users_sets, show_users_sets

CLUSTERS_NUMBER = 5


def kick_user_from_cluster(cluster):
    # Finding an user for kicking
    user = None
    cluster.remove(user)


def experiment3(clusters_number, lists_number):
    result_clusters = []
    is_all_clustered = False
    reader = DataReader()  # "../data/test1.json"
    clustered_users_ids, clustered_users_indexes = [], []

    while not is_all_clustered:

        max_cluster_size = ceil(reader.get_not_clustered_users_count(clustered_users_ids) / clusters_number)
        kmeans = KMeans(n_clusters=clusters_number)
        clusterizations = []
        for i in range(0, lists_number):
            matrix = reader.get_matrix_by_list(i, clustered_users_ids)
            clusterization = kmeans.fit_predict(matrix)
            clusterizations.append(clusters_list_to_users_index_sets(clusterization, clustered_users_indexes))

        max_common_part = 0
        common_parts = []
        cluster_indexes = []

        print("\nClasterisation by list %s" % 1)
        show_users_sets(users_index_sets_to_users_sets(clusterizations[0], reader))
        print("Clasterisation by list %s" % 2)
        show_users_sets(users_index_sets_to_users_sets(clusterizations[1], reader))
        print("\n")

        for i in range(0, len(clusterizations)):

            for j in range(i + 1, len(clusterizations)):

                for k in range(0, len(clusterizations[i])):

                    for l in range(0, len(clusterizations[j])):

                        intersection = set(clusterizations[i][k]).intersection(set(clusterizations[j][l]))

                        common_parts.append(
                            [clusterizations[i][k], clusterizations[j][l], intersection, len(intersection)])

                        if len(intersection) > max_common_part:
                            max_common_part = len(intersection)
                            cluster_indexes = list(intersection)

        for part in common_parts:
            print(str(part))
        print(
            max_common_part)  # Выбирать максимально совпадающую, группировать в команду, удалять из списка юзеров и снова вызывать k-means
        # Если будет больше, чем нужно - выкидывать лишнего

        while max_common_part > max_cluster_size:  # Kick users if it's necessary
            kick_user_from_cluster(cluster_indexes)
            max_common_part -= 1

        clustered_users_indexes.extend(cluster_indexes)  # Extend clustered users indexes array

        cluster_ids = users_index_sets_to_users_sets([cluster_indexes], reader)[0]
        clustered_users_ids.extend([user.get_id() for user in cluster_ids])  # Extend clustered users ids array

        result_clusters.append(cluster_ids)  # Save cluster
        clusters_number -= 1  # Reduce required clusters number

        is_all_clustered = True if len(result_clusters) == CLUSTERS_NUMBER else False

    print("Clusters:")
    show_users_sets(result_clusters)
    for i in range(0, lists_number):
        print("Metrics by criteria #%d:" % (i + 1))
        for user_set in result_clusters:
            m = calculate_set_metrics(user_set, vectors_ids=[i], allow_relations=True)
            print_metrics(m)


if __name__ == '__main__':
    experiment3(CLUSTERS_NUMBER, 2)
