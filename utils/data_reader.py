import json

from models.user import User

__author__ = 'Xomak'


class DataFields:
    lists = "lists"
    user_id = "id"
    people = "selectedPeople"


class DataReader:

    _data = None

    def __init__(self, filename="../data/users.json"):
        with open(filename) as input_file:
            self._data = json.load(input_file)

    def get_user_by_index(self, index):
        user_dict = self._data[index]
        u = User(user_dict[DataFields.user_id], user_dict[DataFields.lists], user_dict[DataFields.people])
        return u

    def get_user_id_by_index(self, index):
        return self._data[index][DataFields.user_id]

    def get_matrix_by_list(self, list_id):
        result = [user[DataFields.lists][list_id] for user in self._data]
        return result