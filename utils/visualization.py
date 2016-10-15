__author__ = 'Xomak'


def clusters_list_to_users_index_sets(clusters_array):
    """
    Converts clusters list, got from scikit to the sets of users' indexes
    [0 0 0 1 2 2 3] will produce [[0, 1, 2], [3], [4, 5], [6]]
    :param clusters_array: Array of clusters' ids
    :return: List of lists with users' indexes
    """

    clusters_number = max(clusters_array) + 1
    teams = [[] for i in range(0, clusters_number)]

    for user, cluster in enumerate(clusters_array):
        teams[cluster].append(user)

    return teams


def show_users_sets(sets):
    """
    Shows users' sets
    :param sets: Set to be showed
    :return:
    """
    for i in range(0, len(sets)):
        line = ""
        for user in sets[i]:
            if len(line) > 0:
                line += ","
            line += str(user)
        print("%d) [%s]" % (i + 1, line))


def users_index_sets_to_users_sets(users_index_sets, reader):
    """
    Converts set of users' indexes sets into set of users' set
    :param users_index_sets: Input set
    :param reader: Reader, which is used to get all information about user by index
    :return: Set of sets of users
    """
    result = []
    for users_index_set in users_index_sets:
        current = []
        for user_index in users_index_set:
            current.append(reader.get_user_by_index(user_index))
        result.append(current)
    return result
