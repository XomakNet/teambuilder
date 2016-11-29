from experiments.experiment3.values_clustering import ValuesClustering
from experiments.experiment4.preferences_clustering import PreferencesClustering
from experiments.experiment5.balancer import Balancer
from experiments.experiment5.users_agglomerative_clustering import UsersAgglomerativeClustering
from experiments.experiment7.balancer_2 import Balancer2
from experiments.experiment7.spectral_clustering import UsersSpectralClustering
from utils.clustering_utils import ClusteringTools
from utils.data_reader import DataReader
from utils.metrics import ClusteringMetric, MetricTypes


class ResultHolder:

    def __init__(self, files_names):
        self.data_files_names = files_names
        self.data = {f: {} for f in self.data_files_names}

    def add_metric_for(self, file_name, teams_number, metric_value):
        metric_value = round(metric_value, 4)
        if self.data[file_name].get(str(teams_number)):
            self.data[file_name][str(teams_number)].append(str(metric_value))
        else:
            self.data[file_name][str(teams_number)] = [str(metric_value)]

    def seriallize(self, out_file_name):
        with open(out_file_name, 'w') as f:
            for file_name, teams_metrics in self.data.items():
                sorted_sizes = sorted(teams_metrics.keys(), key=lambda s: int(s))
                for team_size in sorted_sizes:
                    out_string = "%s %s %s\n" % (file_name, str(team_size), " ".join(teams_metrics[team_size]))
                    f.write(out_string)

desires_weight = 1
need_balance = True
metric_type = MetricTypes.DESIRES
data_files_names = ["../data/ms-sne_names.json", "../data/eltech-vector.json", "../data/users.json"]

results = ResultHolder(data_files_names)

for data_file_name in data_files_names:

    reader = DataReader(data_file_name)
    max_teams = int(len(reader.get_all_users()) / 2)
    for teams in range(2, max_teams + 1):

        print("\n\nTEAMS: %d\n" % teams)

        # Spectral
        clustering_alg = UsersSpectralClustering(reader, teams, desires_weight=desires_weight, need_balance=need_balance)
        sets = clustering_alg.cluster()
        results.add_metric_for(data_file_name, teams, ClusteringMetric(sets, metric_type).get_final_metric())

        # Agglomerative
        clustering_alg = UsersAgglomerativeClustering(reader, teams, desires_weight=desires_weight, need_balance=need_balance, balancer=Balancer)
        sets = clustering_alg.clusterize()
        results.add_metric_for(data_file_name, teams, ClusteringMetric(sets, metric_type).get_final_metric())

        # Lists
        clustering_alg = ValuesClustering(ClusteringTools.KMEANS, reader)
        sets = clustering_alg.cluster(teams, 2, 5)
        results.add_metric_for(data_file_name, teams, ClusteringMetric(sets, metric_type).get_final_metric())

        # Desires
        clustering_alg = PreferencesClustering(reader.get_all_users(), teams, need_balance=need_balance)
        sets = clustering_alg.clusterize()
        results.add_metric_for(data_file_name, teams, ClusteringMetric(sets, metric_type).get_final_metric())

results.seriallize("../out_data/metrics.txt")