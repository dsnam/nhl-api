"""
Tests for NHL API
"""

from nhl_api import NHL


def test_remaining_games():
    nhl = NHL()
    remaining = nhl.get_remaining_games_against()

    assert isinstance(remaining, dict)
    assert remaining[(18,'Nashville Predators')]

def test_team_list():
    nhl = NHL()
    teams = nhl.get_teams_list()

    assert isinstance(teams, list)
    print(teams)

def test_standings():
    nhl = NHL()
    table = nhl.get_points_gp()
    assert isinstance(table, dict)
    print(table)

test_standings()
#test_team_list()
#test_remaining_games()