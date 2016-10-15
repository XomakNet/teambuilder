from dask.tests.test_base import np
from sklearn.cluster import KMeans

from utils.data_reader import DataReader
from utils.metrics import calculate_set_metrics, normalized_vector_distance, print_metrics
from utils.output import OutputWriter, OutFiles
from utils.visualization import clusters_list_to_users_index_sets, users_index_sets_to_users_sets, show_users_sets


def cmp_func(vector):
    return normalized_vector_distance(vector, [i for i in range(0, len(vector))])


def create_initial_centroids(clusters_count, features_matrix):
    """
        Count centroids for feature_matrix, using our provided algorithm (sorting vectors in matrix)
        :param clusters_count: count of clusters for k-means, also it's count of centroids
        :param features_matrix: matrix of features of each user (vectors with user's answers for one criteria)
        :return: centroids array in np.array() format with type of elements np.float64
    """

    features_matrix.sort(key=cmp_func, reverse=True)

    print("Sorted matrix:")
    for i in range(0, len(features_matrix)):
        print(str(i + 1) + ") " + str(features_matrix[i]))

    print("Vector distances:\n" + str([normalized_vector_distance([i for i in range(0, len(vector))], vector) for vector in features_matrix]))

    min_cluster_size = round(float(len(features_matrix)) / clusters_count)
    centroid_index, result_centroids = 0, []
    step = min_cluster_size / 2

    for i in range(0, clusters_count):
        result_centroids.append(features_matrix[
                                    int(centroid_index + step) if int(centroid_index + step) < len(features_matrix) else
                                    features_matrix[len(features_matrix) - 1]])
        centroid_index += min_cluster_size

    print("Centroids:\n" + str(result_centroids))
    np_centroids = np.array(result_centroids, np.float64)

    return np_centroids


# Experiment for checking matrix of mutual distances between vectors,
# using different centroids (random, k-means++ or custom).
# You can provide experiment with 1-st or 2-nd criteria (NOW WITH CRITERIA 1)
def experiment2(clusters_number, lists_number):
    reader = DataReader()  # "../data/test1.json")

    for i in range(lists_number - 1, lists_number):

        for j in range(0, 2):

            input_matrix = reader.get_matrix_by_list(i)

            if j == 1:
                kmeans = KMeans(n_clusters=clusters_number, init='k-means++')
            else:
                centroids = create_initial_centroids(clusters_number, input_matrix)
                kmeans = KMeans(n_clusters=clusters_number, n_init=1, init=centroids)

            clasterization = kmeans.fit_predict(input_matrix)

            sets = users_index_sets_to_users_sets(clusters_list_to_users_index_sets(clasterization), reader)
            print("\nClasterization by list %s" % i)
            show_users_sets(sets)

            out = OutputWriter()
            out.write_rewrite(OutFiles.centroids_custom if j == 0 else OutFiles.centroids_embedded, "")
            print("Metrics:")
            for user_set in sets:
                m = calculate_set_metrics(user_set, vectors_ids=[i], allow_relations=True,
                                          is_custom_centroids=(j == 0))
                print_metrics(m)


if __name__ == '__main__':
    experiment2(5, 1)  # number of clusters / criteria number (1 or 2)
