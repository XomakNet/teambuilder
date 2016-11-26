import utils.clustering_utils as cu
from experiments.experiment3.values_clustering import ValuesClustering
from utils.data_reader import DataReader
from utils.json_serializer import Serializer
from utils.metrics import ClusteringMetric, MetricTypes

REPEATS_COUNT = 10
CLUSTERS_COUNT = 3
LISTS_COUNT = 2
INPUT_DATA_FILENAME = "../data/users.json"
CLUSTERING_TOOL_TYPE = cu.ClusteringTools.KMEANS
METRIC_TYPE = MetricTypes.LISTS

if __name__ == '__main__':

    reader = DataReader(INPUT_DATA_FILENAME)
    clustering = ValuesClustering(CLUSTERING_TOOL_TYPE, reader)

    result_clusters = clustering.cluster(CLUSTERS_COUNT, LISTS_COUNT, REPEATS_COUNT)

    result_metric = ClusteringMetric(list(map(lambda cluster: set(cluster), result_clusters)), METRIC_TYPE)

    print("\n%s" % str(result_metric))
    Serializer.serialize_to_file(result_clusters, "../web-visualiser/data.json")
