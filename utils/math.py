from sklearn.metrics import euclidean_distances


def normalized_vector_distance(vector1, vector2):
    """
    Normalized distance in range [-1,1] between two rank vectors
    :param vector1: First vector
    :param vector2: Second vector
    :return: distance
    """
    if len(vector1) == len(vector2):
        n = len(vector1)
        distance = euclidean_distances([vector1], [vector2])[0][0] ** 2
        normalized = 1 - distance * 6 / (n * (n ** 2 - 1))
        return normalized
    else:
        raise ValueError()


def get_average_mutual_distances(cluster, lists_count):
    """
    Calculate normalized average mutual distances for each user in a cluster
    :param cluster: list of users, which where grouped in cluster
    :param lists_count: count of lists, by which we're clustering
    :return: list of values, each value represents average mutual distance to other users for user from cluster
    """

    if len(cluster) <= 1:
        raise ValueError("Error getting average mutual distances for the cluster: cluster size less or equal 1")

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

    # Normalize distances
    for user_index in range(0, len(cluster)):
        users_mutual_distances[user_index] /= (len(cluster) - 1)

    return users_mutual_distances


def avg(lst):
    if len(lst) == 0:
        return 0

    return sum(lst) / len(lst)


