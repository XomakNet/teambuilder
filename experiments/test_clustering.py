from utils.data_reader import DataReader
from utils.metrics import TeamMetric
from utils.visualization import show_users_sets

# Gave good metric
# [6,13,20,24]
# [7,14,15,17]
# [9,12,18,19]
# [4,10,11,25]
# [5,16,21,22]

if __name__ == '__main__':
    reader = DataReader()
    clusters_ids = [[6, 13, 20, 24],
                    [7, 14, 15, 17],
                    [9, 12, 18, 19],
                    [4, 10, 11, 25],
                    [5, 16, 21, 22]]

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