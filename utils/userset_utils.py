__author__ = 'Xomak'


class UserSet(set):
    """
    Set of users. Intended to simplify work with users' sets, for example, to maintain connections between objects,
    when performing set reduction
    """

    def __init__(self, origin):
        """
        Creates set, containing only new User instances, based on given set
        :param users_set: Original user's set
        :return:
        """

        super().__init__()
        new_users = dict()
        for user in origin:
            new_users[user] = user.copy()
            self.add(new_users[user])

        for user in origin:
            selected_people = user.get_selected_people()
            new_selected_people = [new_users[selected_user] for selected_user in selected_people]
            new_users[user]._selected_people = new_selected_people

    def remove_by_id(self, id):
        """
        Removes users from the set with given id
        :param id: Id of user, which we should delete
        :return:
        """
        for user in self:
            if user.get_id() == id:
                self.remove(user)
                break

    def normalize_set(self):
        """
        Removes from selected_people users, which are not presented in users_set
        :param users_set:
        :return:
        """
        for user in self:
            selected_people = user.get_selected_people()
            illegal_users = [selected_user for selected_user in selected_people if selected_user not in self]
            for illegal_users in illegal_users:
                selected_people.remove(illegal_users)

    def get_by_id(self, id):
        """
        Returns user with given id
        :param id:
        :return:
        """
        for user in self:
            if user.get_id() == id:
                return user

