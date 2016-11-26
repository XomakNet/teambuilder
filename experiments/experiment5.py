from experiments.experiment5.users_agglomerative_clustering import UsersAgglomerativeClustering
from utils.data_reader import DataReader
from utils.json_serializer import Serializer

__author__ = 'Xomak'


reader = DataReader("../data/users.json")
clustering_alg = UsersAgglomerativeClustering(reader, 3)
sets = clustering_alg.clusterize()
Serializer.serialize_to_file(sets, "../web-visualiser/data.json")
