from sklearn.cluster import KMeans

from utils.data_reader import DataReader
from utils.metrics import calculate_set_metric
from utils.visualization import clusters_list_to_users_index_sets, users_index_sets_to_users_sets, show_users_sets

__author__ = 'Xomak'


def experiment1(clusters_number, lists_number):
    reader = DataReader()#"../data/test1.json"
    kmeans = KMeans(n_clusters=clusters_number)
    clasterizations = []
    for i in range(0, lists_number):
        clasterization = kmeans.fit_predict(reader.get_matrix_by_list(i))
        sets = users_index_sets_to_users_sets(clusters_list_to_users_index_sets(clasterization), reader)
        print("Clasterisation by list %s" % i)
        show_users_sets(sets)
        for user_set in sets:
            m = calculate_set_metric(user_set, vectors_ids=[0], allow_relations=False)
            print("Metric is: %s" % m)
        #clasterizations.append(kmeans.fit_predict(reader.get_matrix_by_list(i)))



if __name__ == '__main__':
    experiment1(5, 1)