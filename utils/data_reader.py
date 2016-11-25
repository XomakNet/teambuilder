import json
from typing import Set

from models.user import User

__author__ = 'Xomak'


class DataFields:
    lists = "lists"
    user_id = "id"
    people = "selectedPeople"
    name = "name"


# noinspection PyAttributeOutsideInit
class DataReader:

    _data = None
    _users = dict()
    _user_ids = dict()

    def __init__(self, filename="../data/users.json"):
        with open(filename) as input_file:
            self._data = json.load(input_file)
            for index in range(0, len(self._data)):
                user = self._get_user_by_index(index)
                id = user.get_id()
                self._user_ids[index] = id
                self._users[id] = user

            for index in range(0, len(self._data)):
                selected_people = set()
                selected_people_ids = self._data[index][DataFields.people]
                for id in selected_people_ids:
                    selected_people.add(self.get_user_by_id(id))
                self.get_user_by_index(index).set_selected_people(selected_people)

    def get_user_by_id(self, id: int) -> User:
        """Returns user object by his id."""
        return self._users[id]

    def get_user_by_index(self, index: int) -> User:
        """
        Returns user by its index.
        :param index: Index in file of needed user
        :return: User
        """
        id = self._user_ids[index]
        return self.get_user_by_id(id)

    def _get_user_by_index(self, index: int) -> User:
        user_dict = self._data[index]
        name = user_dict[DataFields.name] if DataFields.name in user_dict else None
        u = User(int(user_dict[DataFields.user_id]), user_dict[DataFields.lists], set(), name)
        return u

    def get_user_id_by_index(self, index: int) -> User:
        return int(self._data[index][DataFields.user_id])

    def get_user_index_by_id(self, user_id: int) -> int:
        """
        Finds index of the user with given user_id
        :param user_id: id of the user
        :return: index of the user
        """
        for user_index in range(0, len(self._data)):
            if int(self._data[user_index][DataFields.user_id]) == user_id:
                return user_index

        raise IndexError("Error finding user with id == %d" % user_id)

    def get_matrix_by_list(self, list_id: int):
        result = [user[DataFields.lists][list_id] for user in self._data]
        return result

    def get_all_users(self) -> Set[User]:
        users = set()
        for index in range(0, len(self._data)):
            users.add(self.get_user_by_index(index))
        return users
