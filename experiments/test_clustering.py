from utils.data_reader import DataReader
from utils.json_serializer import Serializer
from utils.metrics import TeamMetric
from utils.visualization import show_users_sets

# Gave good metric
# [6,13,20,24]
# [7,14,15,17]
# [9,12,18,19]
# [4,10,11,25]
# [5,16,21,22]

# The best clustering ever
# [10,20,18,9]
# [16,15,19,22]
# [17,14,7,5]
# [24,25,4,13]
# [6,11,12,21]

if __name__ == '__main__':
    reader = DataReader("../data/ms-sne_names.json")
    clusters_ids = [[41, 50, 51],
                    [42, 46, 47],
                    [43, 54],
                    [44, 53],
                    [45, 48]]

    # Create clusters of users
    clusters = [
        [reader.get_user_by_id(clusters_ids[cluster_index][user_index])
         for user_index in range(0, len(clusters_ids[cluster_index]))]
        for cluster_index in range(0, len(clusters_ids))]

    # Display clusters
    print("\nFinal clusters:")
    show_users_sets(clusters)

    # Display clusters metrics
    for user_set in clusters:
        metric = TeamMetric(set(user_set))
        print(metric)

    # Serialize to JSON file
    Serializer.serialize_to_file(clusters, "../web-visualiser/data.json")