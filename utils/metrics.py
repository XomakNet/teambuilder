from typing import List
from typing import Set

from math import ceil

from numpy import mean
from sklearn.metrics.pairwise import euclidean_distances

from models.user import User

__author__ = 'Xomak'


class ClusteringMetric:

    balance_weight = 0.5
    average_weight = 0.5

    def __init__(self, users_sets: List[Set[User]]):

        self.sets_metrics = []
        self.total_users_count = 0
        self.balance_metric = 0

        for user_set in users_sets:
            self.total_users_count += len(user_set)

        self.team_size = int(ceil(self.total_users_count / len(users_sets)))
        overload_members_count = 0
        lack_members_count = 0

        total_metrics = []

        for user_set in users_sets:
            set_metric = TeamMetric(user_set)

            self.sets_metrics.append(set_metric)
            total_metrics.append(set_metric.get_final_metric_value())

            overload = len(user_set) - self.team_size
            lack = self.team_size - 1 - len(user_set)
            if overload > 0:
                overload_members_count += overload
            if lack > 0:
                lack_members_count += lack

        self.balance_metric = 1 - (lack_members_count + overload_members_count)/self.total_users_count
        self.average_metric = mean(total_metrics)
        self.min_metric = min(total_metrics)
        self.max_metric = max(total_metrics)

    def get_final_metric(self):
        return self.balance_metric*self.balance_weight + self.average_metric*self.average_weight

    def __str__(self):
        return "Average: {}, min: {}, max: {}, balance: {}".format(self.average_metric, self.min_metric,
                                                                   self.max_metric, self.balance_metric)


class TeamMetric:
    _list_metric_weight = 0.5
    _desires_metric_weight = 0.5

    def __init__(self, users_set):
        self._lists_count = len(next(iter(users_set)).get_lists())  # Kostiyl' was suggested by Kostya
        self._lists_metrics = []

        for list_id in range(0, self._lists_count):
            self._lists_metrics.append(TeamListMetric(users_set, list_id))

        self._desires_metric = TeamDesiresMetric(users_set)

        self._calc_final_metric_value()

    def _calc_final_metric_value(self):
        """
        Calculate final metric of the team, and set it to private field self._final_metric_value.
        Final metric = sum(correct_final_list_metric)/correct_final_list_metric_count
        :return: nothing :)
        """

        self._final_metric_value = 0

        # Calculate final lists metric
        correct_list_metrics_count = 0
        list_metrics_value = 0
        for list_id in range(0, self._lists_count):

            if self._lists_metrics[list_id].is_valid():
                list_metrics_value += self._lists_metrics[list_id].get_final_metric_value()
                correct_list_metrics_count += 1
        if correct_list_metrics_count > 0:
            list_metrics_value /= correct_list_metrics_count

        # Calculate final desires metric
        final_desires_metric = self._desires_metric.get_final_metric_value()

        # Calculate final metric
        self._final_metric_value = list_metrics_value * self._list_metric_weight + \
                                   final_desires_metric * self._desires_metric_weight

    def __str__(self):
        result_str = "\nMetrics of the team:"

        for list_metric in self._lists_metrics:
            result_str += "\n%s" % str(list_metric)

        result_str += "\n%s" % str(self._desires_metric)
        result_str += "\nFINAL METRIC: %s" % str(self._final_metric_value)

        return result_str

    def __cmp__(self, other):
        if self._final_metric_value > other.get_final_metric_value():
            return 1
        elif self._final_metric_value < other.get_final_metric_value():
            return -1
        else:
            return 0

    def get_final_metric_value(self):
        return self._final_metric_value

    def get_all_lists_metrics(self):
        return self._lists_metrics

    def get_list_metric_by_list_number(self, list_number):
        """
        Returns TeamListMetric object for the list with number list_number
        :param list_number: number of the list
        :return: None if list_number < 0 or list_number >= len(lists_metrics), otherwise - TeamListMetric object
        """

        if list_number < -1 or list_number >= len(self._lists_metrics):
            return None

        return self._lists_metrics[list_number]

    def get_desires_metric(self):
        """
        Returns desires metric for the team
        :return: TeamDesiresMetric object
        """
        return self._desires_metric


class TeamDesiresMetric:
    def __init__(self, users_set):
        self._is_valid = False
        self._desires_coeff = 0
        self._desires_of_users_list = []
        self._all_desires_count = 0
        self._all_satisfied_desires_count = 0

        self._calculate_metric(users_set)

    def is_valid(self):
        return self._is_valid

    def __str__(self):
        if self._is_valid:
            return "Desires metric = %s" % self._desires_coeff
        else:
            return "Desires metric isn't valid"

    def get_final_metric_value(self):
        return self._desires_coeff

    def _calculate_metric(self, users_set):

        # Create set of users' ids
        users_ids_set = set()
        for user in users_set:
            users_ids_set.add(user.get_id())

        for user in users_set:
            # Get users which have been selected by user
            users_selected_by_user = user.get_selected_people()
            desires_of_user_count = len(users_selected_by_user)
            satisfied_desires_count = len(users_selected_by_user.intersection(users_set))

            # Increment global counters
            self._all_desires_count += desires_of_user_count
            self._all_satisfied_desires_count += satisfied_desires_count

            # Append desires data for the user
            satisfied_desires_percentage = 0 if desires_of_user_count == 0 else \
                round(satisfied_desires_count / desires_of_user_count, 2)
            self._desires_of_users_list.append({"id": user.get_id(),
                                                "desires_count": desires_of_user_count,
                                                "satisfied_desires_count": satisfied_desires_count,
                                                "satisfied_desires_percentage": satisfied_desires_percentage})

        # Calculating desires coefficient
        if self._all_desires_count == 0:
            self._desires_coeff = 0
        else:
            self._desires_coeff = round(self._all_satisfied_desires_count / self._all_desires_count, 2)

        self._is_valid = True


class TeamListMetric:
    _significant_threshold = 0.5
    _negative_threshold = -0.3

    _average_coeff_weight = 0.4
    _threshold_coeff_weight = 0.6

    def __init__(self, users_set, list_id):
        self._is_valid = False
        self._list_id = list_id
        self._average_coeff = 0
        self._threshold_coeff = 0
        self._pair_distances = []
        self._pairs_count = 0
        self._users_count = 0
        self._behind_significant_threshold_count = 0
        self._behing_negative_threshold_count = 0

        self._calculate_metric(users_set)

    def get_list_id(self):
        return self._list_id

    def is_valid(self):
        return self._is_valid

    def __str__(self):
        if self._is_valid:
            return "List %d, avg = %s, threshold = %s" % (self._list_id, self._average_coeff, self._threshold_coeff)
        else:
            return "Metric of list %d isn't valid" % self._list_id

    def get_final_metric_value(self):
        return self._average_coeff_weight * self._average_coeff + self._threshold_coeff_weight * self._threshold_coeff

    def get_average_coeff(self):
        """
        Returns normalized (0..1) average pair distance
        :return: average coefficient
        """
        return self._average_coeff

    def get_threshold_coeff(self):
        """
        Returns normalized(0..1) value, that shows quality of connections between users.
        C = 1 - (behind_significant_threshold_pairs_count / pairs_count), or
        C = 0, if there are at least 1 pair with distance < behind_negative_threshold
        :return: threshold coefficient
        """
        return self._threshold_coeff

    def _calculate_metric(self, user_set):

        if len(user_set) <= 1:
            return

        self._users_count = len(user_set)
        user_list = list(user_set)
        # Calculate and compare distances between different users
        for first_user_index in range(0, self._users_count):
            for second_user_index in range(first_user_index + 1, self._users_count):

                self._pairs_count += 1
                distance = normalized_vector_distance(user_list[first_user_index].get_lists()[self._list_id],
                                                      user_list[second_user_index].get_lists()[self._list_id])
                self._pair_distances.append(distance)

                if distance < self._significant_threshold:
                    self._behind_significant_threshold_count += 1

                if distance < self._negative_threshold:
                    self._behing_negative_threshold_count += 1

        # Calculating average coefficient
        average_pair_distance = sum(self._pair_distances) / len(self._pair_distances)
        average_pair_distance_normalized = (average_pair_distance + 1) / 2
        self._average_coeff = (round(float(average_pair_distance_normalized), 2))

        # Calculating threshold coefficient
        self._threshold_coeff = 1 - self._behind_significant_threshold_count / self._pairs_count
        if self._behing_negative_threshold_count > 0:
            self._threshold_coeff = 0
        self._threshold_coeff = (round(self._threshold_coeff, 2))

        self._is_valid = True


def normalized_vector_distance(vector1, vector2):
    """
    Normalized distance in range [-1,1] between two rank vectors
    :param vector1: First vector
    :param vector2: Second vector
    :return: distance
    """
    if len(vector1) == len(vector2):
        n = len(vector1)
        distance = euclidean_distances([vector1], [vector2])[0][0] ** 2
        normalized = 1 - distance * 6 / (n * (n ** 2 - 1))
        return normalized
    else:
        raise ValueError()
