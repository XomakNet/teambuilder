import json

from models.user import User

__author__ = 'Xomak'


class DataFields:
    lists = "lists"
    user_id = "id"
    people = "selectedPeople"


# noinspection PyAttributeOutsideInit
class DataReader:
    _data = None
    _users_count = 0

    def __init__(self, filename="../data/users.json"):
        with open(filename) as input_file:
            self._data = json.load(input_file)
        self.get_not_clustered_users_count()

    def get_user_by_index(self, index):
        user_dict = self._data[index]
        u = User(int(user_dict[DataFields.user_id]), user_dict[DataFields.lists], user_dict[DataFields.people])
        return u

    def get_user_id_by_index(self, index):
        return int(self._data[index][DataFields.user_id])

    def get_matrix_by_list(self, list_id, clustered_users=[]):
        result = []
        for user in self._data:
            user_id = int(user[DataFields.user_id])
            if user_id not in clustered_users:
                result.append(user[DataFields.lists][list_id])
        # result = [user[DataFields.lists][list_id] for user in self._data if
        #           int(user[DataFields.user_id]) not in clustered_users]
        return result

    def get_not_clustered_users_count(self, clustered_users=[]):
        self._count = 0
        for user in self._data:
            if int(user[DataFields.user_id]) not in clustered_users:
                self._count += 1
        return self._count
