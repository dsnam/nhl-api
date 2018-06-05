"""
Wrapper for the NHL API, plus some functions that strip out specific info that I've needed
All get_ functions return json responses. Other functions return processed results as lists, dicts, etc.
Format for all years is YYYY-MM-DD
"""

import requests
from datetime import date
from collections import namedtuple


class NHL:

    def __init__(self):
        self.nhl_endpoint = 'https://statsapi.web.nhl.com/api/v1/'
        self.Team = namedtuple('Team', ['team_id', 'name'])
        self.Player = namedtuple('Player', ['player_id', 'name'])
        self.teams = []
        self.players = []

    def get(self, endpoint, params=None):
        """
        :param endpoint: nhl api endpoint
        :param params: parameters for the endpoint. see specific get_ methods for detail
        :return: json of the response
        """
        endpoint = self.nhl_endpoint + endpoint
        if params:
            return requests.get(endpoint, params).json()

        return requests.get(endpoint).json()

    def get_schedule(self, start_date=date.today().strftime("%Y-%m-%d"), end_date=date.today().strftime("%Y-%m-%d"),
                     linescores=False, broadcasts=False, ticket_info=False, team_id=None):
        """
        :param start_date: start date for the schedule pull
        :param end_date: end date for the schedule
        :param linescores: include linescore for completed games
        :param broadcasts: show broadcasts of the game
        :param ticket_info: show ticket purchasing info
        :param team_id: limit the schedule result to a team or list of teams
        :return: json of the schedule data
        """
        endpoint = 'schedule'
        params = {'startDate': start_date, 'endDate': end_date}
        expand_params = []
        if linescores:
            expand_params.append('schedule.linescore')
        if ticket_info:
            expand_params.append('schedule.ticket')
        if broadcasts:
            expand_params.append('schedule.broadcasts')
        if expand_params:
            params['expand'] = expand_params
        if team_id:
            params['id'] = team_id

        return self.get(endpoint, params)

    def remaining_games_against(self, start_date=date.today(), team_id=None):
        """
        :param start_date: start date for calculating games remaining. attempts to be smart: if the provided date
               is after when the regular season usually ends, then it will try to find schedule info for next year
        :param team_id: limit result to a team or list of teams
        :return: remaining regular season games for each team, split by opponent
        """
        teams = self.teams_list()
        remaining_by_team = {team: {t: 0 for t in teams if t != team} for team in teams}

        schedule = self.get_schedule(start_date.strftime("%Y-%m-%d"), start_date.strftime("%Y")+'-04-30')
        for game_dates in schedule['dates']:
            for game in game_dates['games']:
                if game['gameType'] == 'R' and game['status']['abstractGameState'] != 'Final':
                    home = (game['teams']['home']['team']['id'], game['teams']['home']['team']['name'])
                    away = (game['teams']['away']['team']['id'], game['teams']['away']['team']['name'])
                    remaining_by_team[home][away] += 1
                    remaining_by_team[away][home] += 1

        return remaining_by_team

    def get_teams(self):
        """
        :return: json of the teams list
        """
        endpoint = 'teams'

        return self.get(endpoint)

    def teams_list(self, refresh=False):
        """
        :param refresh: calls the api again instead of returning cached data
        :return: processes the response to return a list of Team namedtuples
        """
        if refresh or not self.teams:
            for team in self.get_teams()['teams']:
                self.teams.append(self.Team(str(team['id']), team['name']))

        return self.teams

    def get_standings(self, season=None, as_of_date=None, detail=False):
        """
        :param season: needs to be a string of format YYYYYYYY such as 20172018
        :param as_of_date: standings up to a certain date YYYY-MM-DD
        :param detail: include detailed information like home and away records
        :return:
        """
        endpoint = 'standings'
        params = {}
        if season:
            params['season'] = season
        if date:
            params['date'] = as_of_date
        if detail:
            params['expand'] = 'standings.record'

        return self.get(endpoint, params)

    def points_games_played(self):
        standings = self.get_standings()
        table = {}
        for record in standings['records']:
            div = (record['division']['id'], record['division']['name'])
            conf = (record['conference']['id'], record['conference']['name'])
            for team_record in record['teamRecords']:
                team = self.Team(team_record['team']['id'], team_record['team']['name'])
                table[team] = {'conference': conf, 'division': div, 'points': team_record['points'],
                               'games_played': team_record['gamesPlayed']}

        return table

    def get_roster(self, team_id: str):
        endpoint = ''.join(['teams/', team_id, '/roster'])

        return self.get(endpoint)

    def team_roster(self, team_id: str):
        """

        :param team_id: team for which to look up the roster
        :return: A list of Player named tuples
        """
        roster = []
        for player in self.get_roster(team_id)['roster']:
            roster.append(self.Player(player['person']['id'], player['person']['fullName']))

        return roster

    def player_list(self, refresh=False, ):
        """
        :param refresh: calls the api again instead of returning cached data
        :return: a list of Player namedtuples
        """
        if refresh or not self.players:
            for team in self.teams_list():
                roster = self.get_roster(team.team_id)['roster']
                for player in roster:
                    self.players.append(self.Player(str(player['person']['id']), player['person']['fullName']))

        return self.players

    def get_player(self, player_id: str):
        endpoint = ''.join(['people/', player_id])

        return self.get(endpoint)

    def get_player_stats(self, player_id: str, goals_by_situation=False, season=None):
        """
        :param player_id: id of player to fetch stats for
        :param goals_by_situation: include goals by situation data
        :return: json player stats response
        """
        endpoint = ''.join(['people/', player_id, '/stats'])
        params = {}
        stats = []
        if season:
            params['season'] = season
        if goals_by_situation:
            stats.append('goalsByGameSituation')
        if stats:
            params['stats'] = stats

        return self.get(endpoint, params)

    def player_goal_situations(self, season=None):
        player_goal_situations = {}
        self.players = self.player_list()
        for player in self.players:
            player_stats = self.get_player_stats(player.player_id, goals_by_situation=True, season=season)['stats']
            goal_situations = {x: player_stats[0]['splits'][0]['stat'][x]
                               for x in player_stats[0]['splits'][0]['stat'].keys()}
            player_goal_situations[player] = goal_situations

        return player_goal_situations
