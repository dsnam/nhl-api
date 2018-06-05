# nhl-api
The get_ functions just return the json response, the other functions return processed data as lists or dicts.

Currently supported:

json results for teams, schedule, standings, players, teams, stats, player stats.

You can also get a list of namedtuples of teams and their api ids
```python
('18', 'Nashville Predators')
```
These namedtuples are used to index into the other processed data. Players are handled the same way.

points/games played and conference/division info for each team: 
```python
{('18', 'Nashville Predators): {'conference': 'Western', 'division': 'Central', 'points': 72, 'games_played': 52}}
```

as well as each team's remaining games against every other team:
```python
{('id', 'Team Name'): {('id', 'Team Name'): games_remaining ... } }
```

Still to come:
Full support for all endpoint parameters

Support for game, prospects, awards, draft endpoints