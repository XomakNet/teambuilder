from math import ceil
from typing import List
from typing import Set

from experiments.experiment5.balancer import Balancer
from models.user import User

__author__ = 'Xomak'


class PreferencesClustering:
    DEBUG = False

    def __init__(self, users: Set[User], teams_number: int, need_balance: bool=True):
        """
        Instantiates algorithms.
        :param users: Set of users
        :param teams_number: Required teams number
        """
        self.need_balance = need_balance
        self.users = users
        self.teams_number = teams_number

    def clusterize(self) -> List[Set[User]]:
        """
        Performs clustering
        :return: List of sets of users
        """
        return self.__class__.cluster(self.users, self.teams_number, self.need_balance)

    @classmethod
    def _construct_graph(cls, users):
        """
        Construct graph, based on users set
        :param users: Given users set
        :return: nodes dict
        """

        nodes = dict()

        for user in users:
            nodes[user] = Node(user)

        for current_user, node in nodes.items():
            selected_people = current_user.get_selected_people()
            for selected_user in selected_people:
                selected_user_node = nodes[selected_user]
                node.add_outbound(selected_user_node)
                selected_user_node.add_inbound(node)
        return nodes

    @classmethod
    def _construct_teams(cls, nodes, teams, team_size, only_mutual):
        """
        Goes through the graph nodes and find connected components in it, then add such sets to teams
        :param nodes: Graph with connections between users
        :param teams: Teams
        :param team_size: Maximal size of constructed teams
        :param only_mutual: Construct, if users has mutual link
        :return:
        """
        for user, node in nodes.items():
            sb = cls._construct_team(node, only_mutual)
            if len(sb) > 0:
                #cls._reduce_set(sb, team_size)
                teams.append(sb)

    @classmethod
    def _construct_teams_on_lonely_users(cls, nodes, teams):
        """
        Distribute all lonely users from the graph to their own team, including only themselves
        :param nodes: Graph with connections
        :param teams: Teams set, in which new teams will be added
        :return:
        """
        for user, node in nodes.items():
            if node._is_free:
                sb = set()
                sb.add(node)
                node.set_not_free()
                teams.append(sb)

    @staticmethod
    def get_distance_between_users(user1: User, user2: User):
        result = 0
        if user1 in user2.get_selected_people():
            result += 0.5
        if user2 in user1.get_selected_people():
            result += 0.5
        return result

    @classmethod
    def cluster(cls, users, teams_number, need_balance):
        """
        Divides users into teams_number teams
        :param need_balance: It balancing required
        :param users: Set of users
        :param teams_number: Required teams number
        :return: List of sets of users
        """
        if teams_number > len(users):
            raise ValueError("Teams number should be less or equal to users count")
        nodes = cls._construct_graph(users)
        teams = list()
        team_size = int(ceil(len(users) / teams_number))

        cls._construct_teams(nodes, teams, team_size, True)
        cls._construct_teams(nodes, teams, team_size, False)
        cls._construct_teams_on_lonely_users(nodes, teams)

        # cls._balance_teams(nodes, teams, team_size, teams_number)
        # cls._divide_teams(teams, team_size, teams_number)

        result = []
        for team in teams:
            new_team = set()
            for node in team:
                new_team.add(node.get_user())
            result.append(new_team)
        if need_balance:
            b = Balancer(teams_number, result, PreferencesClustering.get_distance_between_users)
            b.balance()
        return result

    @classmethod
    def _find_set_to_merge_with(cls, teams, current_set, nodes, set_size):
        """
        Finds (or creates from existing) set of size set_size, mostly suitable to merge with current_set
        :param teams: Teams sets
        :param current_set: Set, for which we find
        :param nodes: Graph
        :param set_size: Required set size
        :return:
        """
        merge_candidates = cls._get_sets_with_nearest_size(teams, set_size, current_set)
        set_to_merge = None
        max_connections = None
        if cls.DEBUG:
            print("Looking up for set to merge with %s" % next(iter(current_set)))
        merge_candidates.sort(key=lambda x: len(x))
        for candidate in merge_candidates:
            connections_number = cls._calculate_set_connections(current_set, candidate)
            if cls.DEBUG:
                print("Candadate %s (%d) with cn: %s" % (next(iter(candidate)), len(candidate), connections_number))
            if max_connections is None or connections_number > max_connections:
                max_connections = connections_number
                set_to_merge = candidate
        if len(set_to_merge) > set_size:
            cls._reduce_set(set_to_merge, set_size)
            cls._construct_teams_on_lonely_users(nodes, teams)

        return set_to_merge

    @classmethod
    def _balance_teams(cls, nodes, teams, max_team_size, teams_number):
        """
        Balances teams and reduces their count to teams_number or less than teams_number
        :param nodes: Graph with connections between users
        :param teams: Teams set
        :param max_team_size: Maximum team size
        :param teams_number: Number of team
        :return:
        """
        is_balanced = cls._check_team_set_balance(teams, max_team_size)
        while not is_balanced or len(teams) > teams_number:
            # From small teams to bigger
            teams.sort(key=lambda x: len(x))
            for current_set in teams:
                current_length = len(current_set)
                if current_length < max_team_size - 1 or (is_balanced and current_length < max_team_size):
                    if cls.DEBUG:
                        print("Trying to merge with {}".format(current_set))
                    needed_merge_size = max_team_size - current_length
                    set_to_merge = cls._find_set_to_merge_with(teams, current_set, nodes, needed_merge_size)
                    cls._merge_teams(teams, current_set, set_to_merge)
                    break
            is_balanced = cls._check_team_set_balance(teams, max_team_size)

    @classmethod
    def _find_poorest_two(cls, teams, max_team_size):
        """
        Finds at least two poorest members
        :param teams: teams set
        :param max_team_size: Maximal team size
        :return: dict with poorest members as keys and their team as values
        """
        poorest_members = dict()
        size = max_team_size
        while len(poorest_members) < 2:
            for current_set in teams:
                if len(current_set) == size:
                    poorest_members[cls._find_poorest_member(current_set)] = current_set
            size -= 1
        return poorest_members

    @classmethod
    def _divide_teams(cls, teams, max_team_size, required_teams_number):
        """
        Creates new teams, while total number of teams is less then required.
        New teams are formed from worst-connected members from existing full teams.
        :param teams: Teams set
        :param max_team_size: Maximal team size
        :param required_teams_number: Required number of teams
        :return:
        """
        if len(teams) < required_teams_number:
            while len(teams) < required_teams_number:
                poorest_members = cls._find_poorest_two(teams, max_team_size)

                sorted_members = list(poorest_members.keys())
                sorted_members.sort()

                member1 = sorted_members.pop()
                member2 = sorted_members.pop()

                # Remove members from their current teams
                poorest_members[member1].remove(member1)
                poorest_members[member2].remove(member2)
                t = set()
                t.add(member1)
                t.add(member2)
                teams.append(t)

    @classmethod
    def _check_team_set_balance(cls, teams, max_team_size):
        """
        Check, if all the teams are balanced.
        Balance means, that they have max_team_size or (max_team_size-1) members
        :param teams: Teams set
        :param max_team_size: Maximal team size
        :return:
        """
        for current_set in teams:
            if len(current_set) < max_team_size - 1:
                return False
        return True

    @classmethod
    def _merge_teams(cls, teams, team1, team2):
        """
        Merges team2 into team1 and removed team2 from the teams set
        :param teams: Teams set
        :param team1: Team 1
        :param team2: Team 2
        :return:
        """
        teams.remove(team2)
        teams.remove(team1)
        teams.append(team1.union(team2))

    @classmethod
    def _get_sets_with_nearest_size(cls, sets, needed_size, except_set):
        """
        Returns all sets, having size equal or less than needed_size.
        If no such set exists, returns first set with size more than needed_size.
        Except_set is not considered.
        :param sets: List of sets
        :param needed_size: Size
        :param except_set: This set will not be present in result
        :return: list of found sets
        """
        if needed_size < 1:
            raise ValueError("needed_size should be > 0: %s" % needed_size)
        sizes = dict()
        for current_set in sets:
            if current_set != except_set:
                size = len(current_set)
                if size not in sizes.keys():
                    sizes[size] = list()
                sizes[size].append(current_set)
        result = []
        size = needed_size
        while size > 0:
            try:
                result += sizes[size]
            except KeyError:
                pass
            size -= 1
        size = needed_size + 1
        while len(result) == 0:
            try:
                result += sizes[size]
            except KeyError:
                pass
            size += 1
        return result

    @classmethod
    def _calculate_set_connections(cls, set1, set2):
        """
        Calculates number of connections between nodes from set1 and set2
        :param set1:
        :param set2:
        :return: Number of connections
        """
        connections = 0
        for node in set1:
            connections += len(node.get_outbound().intersection(set2))
            connections += len(node.get_inbound().intersection(set2))
        return connections

    @classmethod
    def _reduce_set(cls, set_to_reduce, needed_size):
        """
        Reduces set size to the given size.
        Reducing is based on removing nodes with poorest connection number
        :param set_to_reduce: Given set
        :param needed_size: Size
        :return:
        """
        if needed_size < len(set_to_reduce):
            cls._calculate_connections_number(set_to_reduce)
            nodes_list = list(set_to_reduce)
            nodes_list.sort()
            i = 0
            for current_size in range(len(set_to_reduce), needed_size, -1):
                set_to_reduce.remove(nodes_list[i])
                nodes_list[i].set_free()
                i += 1

    @classmethod
    def _find_poorest_member(cls, team):
        """
        Returns member of the team, who has minimal connectivity rank with other members in his team
        :param team: Team - users set
        :return: Poorest member
        """
        cls._calculate_connections_number(team)
        return min(team)

    @classmethod
    def _calculate_connections_number(cls, set_to_calculate):
        """
        Calculates connections number between nodes and sets these values as properties in nodes
        :param set_to_calculate:
        :return:
        """
        for node in set_to_calculate:
            node.clear_metrics()
            for neighbor in node.get_outbound():
                if neighbor not in set_to_calculate:
                    node.external_connections_number += 1
                else:
                    if neighbor in node.get_inbound():
                        node.mutual_connections_number += 1
                    else:
                        node.single_connections_number += 1
            for neighbor in node.get_inbound():
                if neighbor not in set_to_calculate:
                    node.external_connections_number += 1
                else:
                    if neighbor not in node.get_outbound():
                        node.single_connections_number += 1

    @classmethod
    def _construct_team(cls, start_node, only_mutual):
        """
        Construct team, starting from start_node and connecting another linked nodes
        :param start_node: BFS will start from this node
        :param only_mutual: Set to True, if all connections between nodes should be mutual
        :return: set of connected nodes
        """
        subgraph = set()
        queue = list()
        queue.append(start_node)
        while len(queue) > 0:
            current_node = queue.pop()
            if current_node.is_free():
                current_node.set_not_free()
                subgraph.add(current_node)
                for neighbor in current_node.get_outbound():
                    if not only_mutual or current_node in neighbor.get_outbound():
                        queue.insert(0, neighbor)
                if not only_mutual:
                    for neighbor in current_node.get_outbound():
                        queue.insert(0, neighbor)
        if len(subgraph) == 1:
            subgraph.pop().set_free()
        return subgraph


class Node:
    """
    Represents node in connectivity graph
    """

    def __str__(self):
        return str(self._user)

    def __init__(self, user):
        self._user = user
        self._inbound_connections = set()
        self._outbound_connections = set()
        self._is_free = True

    def clear_metrics(self):
        # Number of mutual connections to the group's members
        self.mutual_connections_number = 0
        # Number of single connections to the group'd members
        self.single_connections_number = 0
        # Number of any external connections
        self.external_connections_number = 0

    def set_not_free(self):
        self._is_free = False
        self.clear_metrics()

    def set_free(self):
        self._is_free = True

    def is_free(self):
        return self._is_free

    def get_outbound(self):
        return self._outbound_connections

    def get_inbound(self):
        return self._inbound_connections

    def add_outbound(self, node):
        self._outbound_connections.add(node)

    def add_inbound(self, node):
        self._inbound_connections.add(node)

    def get_user(self):
        return self._user

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __cmp__(self, other):
        mutual_diff = self.mutual_connections_number - other.mutual_connections_number
        single_diff = self.single_connections_number - other.single_connections_number
        # This is not an error! The more external connections we have, the less we are
        external_diff = other.external_connections_number - self.external_connections_number

        return 0.5 * mutual_diff + 0.25 * single_diff + 0.5 * external_diff
