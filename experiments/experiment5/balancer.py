from numbers import Number
from typing import List, Set, Callable

from math import ceil

import numpy

from models.user import User

__author__ = 'Xomak'


class Balancer:
    """
    Balancer class is intended to balance teams, if they have uneven cluster size.
    Now it is intended to work only if teams number is correct at the input.
    """

    def __init__(self, required_teams_number: int, teams: List[Set[User]],
                 affinity_function: Callable[[User, User], Number]):
        """
        Inits balancer
        :param required_teams_number:  Required teams number
        :param teams: Current teams
        :param affinity_function: Function, which is used to calculate distances between 2 users
        """
        if len(teams) != required_teams_number:
            raise NotImplementedError("Teams count balancing is not supported yet.")
        self.required_teams_number = required_teams_number
        self.affinity_function = affinity_function
        total_number = 0
        for team in teams:
            total_number += len(team)
        self.team_size = int(ceil(total_number / required_teams_number))
        self.teams = teams

    def get_affinity_to_all(self, user: User, team: Set[User]) -> Number:
        """
        Calculates average affinity from current user to all users in team
        :param user: User
        :param team: Team
        :return: Average affinity
        """
        avgs = []
        for team_member in team:
            if team_member != user:
                avgs.append(self.affinity_function(user, team_member))
        return numpy.mean(avgs)

    def balance(self) -> None:
        """
        Performs balancing
        :return:
        """
        odd_members = self.cut_odd_members()
        self.populate_little_teams_with(odd_members)
        self.distribute_members(odd_members)

    def get_worst_member(self, team) -> User:
        """
        Finds and returns the worst member in the given team
        :param team: Team to find in
        :return: The worst member
        """
        worst_member = None
        worst_member_result = 0
        for member in team:
            member_result = self.get_affinity_to_all(member, team)
            if worst_member is None or worst_member_result < member_result:
                worst_member = member
                worst_member_result = member_result
        return worst_member

    def find_too_big_team(self) -> Set[User]:
        """
        Returns any team with members count more than required
        :return: team or none
        """
        for team in self.teams:
            if len(team) > self.team_size:
                return team
        return None

    def get_free_teams(self) -> List[Set[User]]:
        """
        Returns team, which has vacant places for members
        :return: List of free teams
        """
        result = list()
        for team in self.teams:
            if len(team) < self.team_size:
                result.append(team)
        return result

    def distribute_members(self, members: Set[User]) -> None:
        """
        Distributes members from given set into teams, which has free places, with respect to their
        pairwise distances
        :param members: Members to distribute
        :return:
        """
        while len(members) > 0:
            member = next(iter(members))
            free_teams = self.get_free_teams()
            most_suitable_team = None
            most_suitable_team_result = 0
            for team in free_teams:
                team_result = self.get_affinity_to_all(member, team)
                if most_suitable_team is None or team_result > most_suitable_team_result:
                    most_suitable_team_result = team_result
                    most_suitable_team = team
            most_suitable_team.append(member)
            members.remove(member)

    def cut_odd_members(self) -> Set[User]:
        """
        Removes the worst members from the team with members count more than required and returns them as set
        :return: Set of odd_members
        """
        has_too_big_teams = True
        odd_members = set()
        while has_too_big_teams:
            big_team = self.find_too_big_team()
            if big_team is not None:
                while len(big_team) != self.team_size:
                    worst_member = self.get_worst_member(big_team)
                    big_team.remove(worst_member)
                    odd_members.add(worst_member)
            else:
                has_too_big_teams = False
        return odd_members

    def populate_little_teams_with(self, members: Set[User]) -> None:
        """
        Populate teams with members count less than required_size - 1 by users from members set, with respect to
        their pairwise_distances
        :param members: Members, which will be used (items will being removed, until there is little teams)
        :return:
        """
        for team in self.teams:
            if len(team) < self.team_size - 1:
                most_suitable_member = None
                most_suitable_member_result = 0
                for member in members:
                    member_result = self.get_affinity_to_all(member, team)
                    if most_suitable_member is None or member_result > most_suitable_member_result:
                        most_suitable_member_result = member_result
                        most_suitable_member = member
                members.remove(most_suitable_member)
                team.append(most_suitable_member)

