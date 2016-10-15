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

    def __init__(self, filename="../data/users.json"):
        with open(filename) as input_file:
            self._data = json.load(input_file)

    def get_user_by_index(self, index):
        user_dict = self._data[index]
        u = User(int(user_dict[DataFields.user_id]), user_dict[DataFields.lists], user_dict[DataFields.people])
        return u

    def get_user_id_by_index(self, index):
        return int(self._data[index][DataFields.user_id])

    def get_all_users(self):
        all_users = [self.get_user_by_index(user_index) for user_index in range(0, len(self._data))]
        return all_users

