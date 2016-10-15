from math import ceil

from experiments.experiment4.preferences_clustering import PreferencesClustering
from utils.data_reader import DataReader

__author__ = 'Xomak'

reader = DataReader()
pc = PreferencesClustering.cluster(reader.get_all_users(), 5)
for current_set in pc:
    output = []
    for user in current_set:
        output.append(str(user))
    print(','.join(output))

