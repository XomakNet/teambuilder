from sklearn.metrics.pairwise import euclidean_distances

__author__ = 'Xomak'


class TeamMetric:

    def __init__(self, users_set):
        self._lists_count = len(users_set[0].get_lists())     # Kostil' suggested by Kostya
        self._lists_metrics = []

        for list_id in range(0, self._lists_count):
                self._lists_metrics.append(TeamListMetric(users_set, list_id))

        self._desires_metric = TeamDesiresMetric(users_set)

    def __str__(self):
        result_str = "\nMetrics of the team:"

        for list_metric in self._lists_metrics:
            result_str += str(list_metric)

        result_str += str(self._desires_metric)

        return result_str

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
            return "\nDesires metric = %s" % self._desires_coeff
        else:
            return "Desires metric isn't valid"

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

    def is_valid(self):
        return self._is_valid

    def __str__(self):
        if self._is_valid:
            return "\nList %d, avg = %s, threshold = %s" % (self._list_id, self._average_coeff, self._threshold_coeff)
        else:
            return "\nMetric of list %d isn't valid" % self._list_id

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
        # Calculate and compare distances between different users
        for first_user_index in range(0, self._users_count):
            for second_user_index in range(first_user_index + 1, self._users_count):

                self._pairs_count += 1
                distance = normalized_vector_distance(user_set[first_user_index].get_lists()[self._list_id],
                                                      user_set[second_user_index].get_lists()[self._list_id])
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
