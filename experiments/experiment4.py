from math import ceil

from experiments.experiment4.preferences_clustering import PreferencesClustering
from utils.data_reader import DataReader
from utils.json_serializer import Serializer
from utils.metrics import TeamDesiresMetric

__author__ = 'Xomak'

reader = DataReader("../data/ms-sne.json")
pc = PreferencesClustering(reader.get_all_users(), 6)
result = pc.clusterize()
for current_set in result:
    output = []
    for user in current_set:
        output.append(str(user))
    print(','.join(output))
    print(TeamDesiresMetric(current_set))
Serializer.serialize_to_file(result, "../web-visualiser/data.json")

