__author__ = 'Xomak'

from sklearn.metrics.pairwise import euclidean_distances


def calculate_set_metric(user_set, vectors_ids=None, allow_relations=False):
    """
    Calculates metric of given users' set.
    :param user_set: Users' set
    :param vectors_ids: Vectors' ids, which should be included in metric
    :param allow_relations: Relations between users will be allowed in metrics calculation
    :return: Metric
    """

    #TODO: Add metric for relations
    metrics = []
    if vectors_ids:
        for vector_id in vectors_ids:
            vector_metrics = []
            for i in range(0, len(user_set)):
                metric1 = user_set[i].get_lists()[vector_id]
                for j in range(i+1, len(user_set)):
                    metric2 = user_set[j].get_lists()[vector_id]
                    vector_metrics.append(normalized_vector_distance(metric1, metric2))
            vector_metrics.sort()
            vector_size = len(vector_metrics)
            if vector_size % 2 == 0:
                median = (vector_metrics[int(vector_size/2)]-vector_metrics[int(vector_size/2)-1])/2
            else:
                median = vector_metrics[int(vector_size/2)]
            metrics.append(median)
    #TODO: Calculate complex metric, using theese metrics
    return sum(metrics)


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
