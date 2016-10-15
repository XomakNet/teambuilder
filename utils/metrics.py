from utils.output import OutputWriter, OutFiles
from sklearn.metrics.pairwise import euclidean_distances

__author__ = 'Xomak'


class MetricsFields:
    threshold = "Threshold coefficient"
    average = "Average coefficient"
    desires = "Users desires coefficient"


def print_metrics(metrics_dict):
    """
    Print to the console dict of the metrics as string (in the convenient way like [<metric1>, <metric2>, ...])
    :param metrics_dict: dict of the metrics
    :return: None
    """

    metrics_array = []

    keys = list(metrics_dict.keys())
    keys.sort()
    for k in keys:
        metrics_array.append(metrics_dict[k])

    print(str(metrics_array))


def calculate_set_metrics(user_set, vectors_ids=None, allow_relations=False, is_custom_centroids=None):
    """
    Calculates metric of given users' set.
    :param user_set: Users' set
    :param vectors_ids: Vectors' ids, which should be included in metric
    :param allow_relations: Relations between users will be allowed in metrics calculation
    :param is_custom_centroids: Which centroids we are checking now? Put None, if it's not necessary to check centroids.
    :return: Metrics list with length len(vector_ids)*2 + [1 (if allow_relations)]
    """

    if len(user_set) <= 1:
        return {}

    significant_threshold = 0.5
    negative_threshold = -0.3
    users_number = len(user_set)
    metrics = {}

    if is_custom_centroids is not None:
        out = OutputWriter()
        out_file_name = OutFiles.centroids_custom if is_custom_centroids else OutFiles.centroids_embedded

    if vectors_ids:
        for vector_id in vectors_ids:
            behind_significant_threshold_elements = 0
            behind_negative_threshold_elements = 0
            pairs_number = 0
            vector_distances = []
            for i in range(0, users_number):
                for j in range(i + 1, users_number):
                    pairs_number += 1
                    distance = normalized_vector_distance(user_set[i].get_lists()[vector_id],
                                                          user_set[j].get_lists()[vector_id])
                    vector_distances.append(distance)
                    if distance < significant_threshold:
                        behind_significant_threshold_elements += 1
                    if distance < negative_threshold:
                        behind_negative_threshold_elements += 1

            copy_vector_distances = [str(distance) for distance in vector_distances]
            copy_vector_distances.sort()

            if is_custom_centroids is not None:
                out.write_append(out_file_name, " ".join(copy_vector_distances) + "\n")

            vectors_average = sum(vector_distances) / len(vector_distances)
            vectors_threshold_coeff = 1 - behind_significant_threshold_elements / pairs_number
            if behind_negative_threshold_elements > 0:
                vectors_threshold_coeff = 0
            vectors_average_normalized = (vectors_average + 1) / 2
            metrics[MetricsFields.threshold] = (round(vectors_threshold_coeff, 2))
            metrics[MetricsFields.average] = (round(float(vectors_average_normalized), 2))

    if allow_relations:

        users_ids_set = set()
        for user in user_set:
            users_ids_set.add(user.get_id())

        relations_number = 0
        good_relations_number = 0
        users_good_relations_counts = []
        for user in user_set:
            selected_ids = user.get_selected_people()
            relations_number += len(selected_ids)
            sets_intersection = selected_ids.intersection(user_set)
            good_relations_number += len(sets_intersection)
            if len(selected_ids) > 0:  # if user peeks someone
                users_good_relations_counts.append(round(len(sets_intersection) / len(selected_ids), 2))

        # Desires coefficient
        average_suggestions_considerations_coeff = 0 if len(users_good_relations_counts) == 0 else sum(
            users_good_relations_counts) / len(users_good_relations_counts)
        metrics[MetricsFields.desires] = (round(average_suggestions_considerations_coeff, 2))

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
        distance = euclidean_distances([vector1], [vector2])[0][0] ** 2
        normalized = 1 - distance * 6 / (n * (n ** 2 - 1))
        return normalized
    else:
        raise ValueError()
