from typing import List

__author__ = 'Xomak'


class User:

    _id = None
    _lists = []
    _selected_people = []

    def __init__(self, id, lists, selected_people):
        self._id = id
        self._lists = lists
        self._selected_people = selected_people

    def copy(self):
        """
        Returns copy of this user.
        WARNING! Connections to other users are NOT copied
        :return:
        """
        return User(self._id, self._lists, None)

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._id

    def __str__(self):
        return str(self._id)

    def get_id(self):
        return self._id

    def get_lists(self):
        return self._lists

    def set_selected_people(self, selected_people):
        self._selected_people = selected_people

    def get_selected_people(self):
        return self._selected_people