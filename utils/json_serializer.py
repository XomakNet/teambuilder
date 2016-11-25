import json

from utils.metrics import TeamMetric, normalized_vector_distance

__author__ = 'Xomak'


class Serializer:

    @classmethod
    def serialize_to_file(cls, sets_list, file):
        with open(file, "w") as file:
            file.write(cls.serialize(sets_list))

    @classmethod
    def serialize(cls, sets_list):
        result = dict()
        users = []
        cluster_id = 0
        all_users = []
        result['clusters'] = []
        for users_set in sets_list:
            current_cluster = dict()
            current_cluster['id'] = cluster_id
            current_cluster['users_ids'] = []
            for user in users_set:
                current_cluster['users_ids'].append(user.get_id())
                all_users.append(user)
                users.append(cls._get_user(user))
            current_cluster['metric'] = cls._get_metrics(users_set)
            result['clusters'].append(current_cluster)
            cluster_id += 1
        result['users'] = users
        result['pairDistances'] = cls._get_pairwise_distances(all_users)
        return json.dumps(result)

    @classmethod
    def _get_pairwise_distances(cls, all_users):
        result = []
        for first_user_index in range(0, len(all_users)):
            for second_user_index in range(first_user_index+1, len(all_users)):
                current_pair = dict()
                user1 = all_users[first_user_index]
                user2 = all_users[second_user_index]
                current_pair['user1'] = user1.get_id()
                current_pair['user2'] = user2.get_id()
                current_pair['distances'] = []
                for list_id in range(0, len(user1.get_lists())):
                    current_list = dict()
                    current_list['id'] = list_id
                    current_list['distance'] = normalized_vector_distance(user1.get_lists()[list_id], user2.get_lists()[list_id])
                    current_pair['distances'].append(current_list)
                result.append(current_pair)
        return result

    @classmethod
    def _get_metrics(cls, users_set):
        result = dict()
        tm = TeamMetric(users_set)
        result['listsMetrics'] = cls._get_lists_metrics(tm)
        result['desiresMetric'] = cls._get_desires_metric(tm)
        result['finalMetric'] = tm.get_final_metric_value()
        return result

    @classmethod
    def _get_desires_metric(cls, metric):
        result = dict()
        dm = metric.get_desires_metric()
        result['value'] = dm.get_final_metric_value()
        return result

    @classmethod
    def _get_lists_metrics(cls, metric):
        result = []
        for list_metric in metric.get_all_lists_metrics():
            current_list = dict()
            current_list['id'] = list_metric.get_list_id()
            current_list['final'] = list_metric.get_final_metric_value()
            current_list['average'] = list_metric.get_average_coeff()
            current_list['threshold'] = list_metric.get_threshold_coeff()
            result.append(current_list)
        return result

    @classmethod
    def _get_user(cls, user):
        result = dict()
        result['id'] = user.get_id()
        result['name'] = user.get_name()
        result['selectedPeople'] = [selected_user.get_id() for selected_user in user.get_selected_people()]
        result['lists'] = []
        i = 0
        for list in user.get_lists():
            current_list = dict()
            current_list['id'] = i
            current_list['items'] = list
            result['lists'].append(current_list)
            i += 1

        return result

