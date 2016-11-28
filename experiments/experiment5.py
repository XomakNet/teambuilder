from experiments.experiment4.preferences_clustering import PreferencesClustering
from experiments.experiment5.users_agglomerative_clustering import UsersAgglomerativeClustering
from utils.data_reader import DataReader
from utils.json_serializer import Serializer
from utils.metrics import ClusteringMetric

__author__ = 'Xomak'

variants = ["../data/users.json", "../data/ms-sne.json", "../data/eltech-vector.json"]


def complete_vs_avg(teams_number):
    for variant in variants:
        reader = DataReader(variant)

        def form_line(metric: ClusteringMetric):
            return "{},{},{}".format(metric.average_metric, metric.min_metric, metric.max_metric)

        clustering_alg = UsersAgglomerativeClustering(reader, teams_number)
        clustering_alg.linkage = "complete"
        sets = clustering_alg.clusterize()

        complete = ClusteringMetric(sets)

        clustering_alg = UsersAgglomerativeClustering(reader, teams_number)
        clustering_alg.linkage = "average"
        sets = clustering_alg.clusterize()

        average = ClusteringMetric(sets)

        print(form_line(average) + "," + form_line(complete))
        #Serializer.serialize_to_file(sets, "../web-visualiser/data.json")


def agglomerative_vs_pc(teams_number):

    for variant in variants:
        reader = DataReader(variant)

        clustering_alg = UsersAgglomerativeClustering(reader, teams_number, desires_weight=1)
        sets_agg = clustering_alg.clusterize()

        agglomerative = ClusteringMetric(sets_agg).get_average_desires_metric()

        pc = PreferencesClustering(reader.get_all_users(), teams_number)
        sets_pc = pc.clusterize()
        if variant == "../data/users.json":
            Serializer.serialize_to_file(sets_pc, "../web-visualiser/pc.json")
            Serializer.serialize_to_file(sets_agg, "../web-visualiser/agg.json")
        my = ClusteringMetric(sets_pc).get_average_desires_metric()

        print("{};{}".format(agglomerative, my))


def clusterize(filename, teams_number):
    reader = DataReader(filename)
    clustering_alg = UsersAgglomerativeClustering(reader, teams_number)
    cl = clustering_alg.clusterize()
    Serializer.serialize_to_file(cl, "../web-visualiser/data.json")

clusterize("../data/users.json", 5)
