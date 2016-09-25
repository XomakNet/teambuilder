__author__ = 'Xomak'


def clusters_list_to_users_index_sets(clusters_array, clustered_users_indexes=[]):
    """
    Converts clusters list, got from scikit to the sets of users' indexes
    [0 0 0 1 2 2 3] will produce [[0, 1, 2], [3], [4, 5], [6]]
    :param clustered_users_indexes: Array of user's indexes, which have been already clustered
    :param clusters_array: Array of clusters' ids
    :return: List of lists with users' indexes
    """
    clusters_number = max(clusters_array) + 1
    teams = [[] for i in range(0, clusters_number)]
    exists_indexes = [i for i in clustered_users_indexes]

    for user, cluster in enumerate(clusters_array):
        curr_index = user

        while curr_index in exists_indexes:
            curr_index += 1

        exists_indexes.append(curr_index)
        teams[cluster].append(curr_index)

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
