# nhl-api
Most of the get_ functions just return the json response, other functions were written specifically to
process the data for another project, so they may not be too useful to anyone else.

Currently supported:

json results for teams, schedule, standings

You can also get a list of teams and their api ids 
```python
(18, 'Nashville Predators')
```
This tuple format is used to index into the other processed data.

points/games played and conference/division info for each team: 
```python
{(18, 'Nashville Predators): {'conf': 'Western', 'div': 'Central', 'pts': 72, 'gp': 52}}
```

as well as each team's remaining games against every other team:
```python
{(id, 'Team Name'): {(id, 'Team Name'): games_remaining ... } }
```
