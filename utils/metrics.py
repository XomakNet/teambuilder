__author__ = 'Xomak'

from sklearn.metrics.pairwise import euclidean_distances


def calculate_set_metrics(user_set, vectors_ids=None, allow_relations=False):
    """
    Calculates metric of given users' set.
    :param user_set: Users' set
    :param vectors_ids: Vectors' ids, which should be included in metric
    :param allow_relations: Relations between users will be allowed in metrics calculation
    :return: Metrics list with length len(vector_ids)*2 + [1 (if allow_relations)]
    """

    threshold = 0.5
    users_number = len(user_set)
    metrics = []
    users_ids_set = set()
    for user in user_set:
        users_ids_set.add(user.get_id())
    if vectors_ids:
        for vector_id in vectors_ids:
            behind_threshold_elements = 0
            pairs_number = 0
            vector_distances = []
            for i in range(0, users_number):
                for j in range(i+1, users_number):
                    pairs_number += 1
                    distance = normalized_vector_distance(user_set[i].get_lists()[vector_id],
                                                          user_set[j].get_lists()[vector_id])
                    vector_distances.append(distance)
                    if distance < threshold:
                        behind_threshold_elements += 1
            vectors_average = sum(vector_distances)/len(vector_distances)
            vectors_threshold_coeff = 1 - behind_threshold_elements/pairs_number
            vectors_average_normalized = (vectors_average+1)/2
            metrics.append(vectors_threshold_coeff)
            metrics.append(vectors_average_normalized)

    if allow_relations:
        relations_number = 0
        good_relations_number = 0
        for user in user_set:
            selected_ids = set(user.get_selected_people_list())
            relations_number += len(selected_ids)
            sets_intersection = selected_ids.intersection(users_ids_set)
            good_relations_number += len(sets_intersection)
        relations_coeff = good_relations_number/relations_number
        metrics.append(relations_coeff)

    return metrics


def normalized_vector_distance(vector1, vector2):
    """
    Normalized distance in range [-1,1] between two rank vectors
    :param vector1: First vector
    :param vector2: Second vector
    :return: distance
    """
    if len(vector1) == len(vector2):
        n = len(vector1)
        distance = euclidean_distances([vector1], [vector2])[0][0]**2
        normalized = 1 - distance * 6 / (n * (n**2 - 1))
        return normalized
    else:
        raise ValueError()
