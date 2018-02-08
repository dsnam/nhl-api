"""
Wrapper for the NHL API, plus some functions that strip out specific info that I've needed
"""

import requests
import datetime

nhl_ep = 'https://statsapi.web.nhl.com/api/v1/'


def get(endpoint, params=[]):
    """
    :param endpoint: nhl api endpoint
    :param params: parameters such as startDate, etc. will list these at some point
    :return: json of the response
    """

    ep = nhl_ep + endpoint
    if params:
        data = requests.get(ep, params).json()
    else:
        data = requests.get(ep).json()

    return data


def get_schedule(start_date, end_date):
    """
    :param start_date: start date for the schedule pull
    :param end_date: end date for the schedule
    :return: json of the schedule data
    """

    ep = nhl_ep + 'schedule'
    params = {'startDate': start_date, 'endDate': end_date}
    return get(ep, params)


def get_remaining_games_against():
    """
    :return: remaining regular season games for each team, split by opponent
    """

    teams = get_teams()
    remaining_by_team = {team: {t: 0 for t in teams if t != team} for team in teams}
    today = datetime.datetime.now()
    # should be safe to assume the season ends sometime in April
    schedule = get_schedule(today.strftime("%Y-m-%d"), today.strftime("%Y")+'-04-30')
    for date in schedule['dates']:
        for game in date['games']:
            # only want unfinished regular season games
            if game['gameType'] == 'R' and game['status']['abstractGameState'] != 'Final':
                home = (game['teams']['home']['id'], game['teams']['home']['name'])
                away = (game['teams']['away']['id'], game['teams']['away']['name'])
                remaining_by_team[home][away] += 1
                remaining_by_team[away][home] += 1

    return remaining_by_team


def get_teams():
    ep = nhl_ep + 'teams'
    return get(ep)


def get_teams_list():
    data = get_teams()
    teams = []
    for team in data['teams']:
        teams.append((team['id'], team['name']))

    return teams


def get_standings():
    ep = nhl_ep + 'standings'

    return get(ep)


