"""
Wrapper for the NHL API, plus some functions that strip out specific info that I've needed
"""

import requests
import datetime


class NHL:

    def __init__(self):
        self.nhl_ep = 'https://statsapi.web.nhl.com/api/v1/'

    def get(self, endpoint, params=[]):
        """
        :param endpoint: nhl api endpoint
        :param params: parameters such as startDate, etc. will list these at some point
        :return: json of the response
        """
        ep = self.nhl_ep + endpoint
        if params:
            data = requests.get(ep, params).json()
        else:
            data = requests.get(ep).json()

        return data

    def get_schedule(self, start_date, end_date):
        """
        :param start_date: start date for the schedule pull
        :param end_date: end date for the schedule
        :return: json of the schedule data
        """

        ep = 'schedule'
        params = {'startDate': start_date, 'endDate': end_date}
        return self.get(ep, params)

    def get_remaining_games_against(self):
        """
        :return: remaining regular season games for each team, split by opponent
        """

        teams = self.get_teams_list()
        remaining_by_team = {team: {t: 0 for t in teams if t != team} for team in teams}
        today = datetime.datetime.now()
        # should be safe to assume the season ends sometime in April
        schedule = self.get_schedule(today.strftime("%Y-%m-%d"), today.strftime("%Y")+'-04-30')
        for date in schedule['dates']:
            for game in date['games']:
                # only want unfinished regular season games
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
        ep = 'teams'
        return self.get(ep)

    def get_teams_list(self):
        """
        :return: processes the response to return a list of (id, name) tuples
        """
        data = self.get_teams()
        teams = []
        for team in data['teams']:
            teams.append((team['id'], team['name']))

        return teams

    def get_standings(self):
        ep = 'standings'

        return self.get(ep)

    def get_points_gp(self):
        standings = self.get_standings()
        table = {}
        for record in standings['records']:
            div = (record['division']['id'], record['division']['name'])
            conf = (record['conference']['id'], record['conference']['name'])
            for team_record in record['teamRecords']:
                team = (team_record['team']['id'], team_record['team']['name'])
                table[team] = {'conf': conf, 'div': div, 'pts': team_record['points'], 'gp': team_record['gamesPlayed']}

        return table




