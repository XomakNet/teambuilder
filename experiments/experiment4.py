from math import ceil

from experiments.experiment4.preferences_clustering import PreferencesClustering
from utils.data_reader import DataReader
from utils.json_serializer import Serializer
from utils.metrics import TeamDesiresMetric

__author__ = 'Xomak'

reader = DataReader()
pc = PreferencesClustering.cluster(reader.get_all_users(), 4)
for current_set in pc:
    output = []
    for user in current_set:
        output.append(str(user))
    print(','.join(output))
    print(TeamDesiresMetric(current_set))
print(Serializer.serialize(pc))

