__author__ = 'Xomak'


class User:

    _id = None
    _lists = []
    _selected_people = []

    def __init__(self, id, lists, selected_people):
        self._id = id
        self._lists = lists
        self._selected_people = selected_people

    def __str__(self):
        return str(self._id)

    def get_id(self):
        return self._id

    def get_lists(self):
        return self._lists

    def get_selected_people_list(self):
        return self._selected_people