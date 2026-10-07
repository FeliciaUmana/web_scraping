"""Small HTML fixtures that mimic FBref's structure (synthetic sample data)."""


HISTORY_HTML = """
<html><body><table id="seasons"><tbody>
<tr><th><a href="/en/comps/9/2024-2025/2024-2025-Premier-League-Stats">2024-2025</a></th></tr>
<tr><th><a href="/en/comps/9/2023-2024/2023-2024-Premier-League-Stats">2023-2024</a></th></tr>
</tbody></table></body></html>
"""

STANDINGS_TABLE = """
<table id="results2024-202591_overall">
<thead><tr><th>Rk</th><th>Squad</th><th>MP</th><th>W</th><th>D</th><th>L</th>
<th>GF</th><th>GA</th><th>GD</th><th>Pts</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>1</td><td> Alpha FC </td><td>38</td><td>25</td><td>9</td><td>4</td><td>86</td><td>41</td><td>+45</td><td>84</td><td>Champions</td></tr>
<tr><td>2</td><td>Beta United</td><td>38</td><td>20</td><td>14</td><td>4</td><td>69</td><td>34</td><td>+35</td><td>74</td><td></td></tr>
<tr><th>Rk</th><th>Squad</th><th>MP</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Pts</th><th>Notes</th></tr>
<tr><td>3</td><td>Gamma Town</td><td>38</td><td>19</td><td>8</td><td>11</td><td>58</td><td>51</td><td>+7</td><td>65</td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</tbody></table>
"""

KEEPER_TABLE = """
<table id="stats_squads_keeper_for">
<thead>
<tr><th></th><th></th><th colspan="2">Playing Time</th><th colspan="3">Performance</th></tr>
<tr><th>Squad</th><th># Pl</th><th>MP</th><th>Min</th><th>GA</th><th>Saves</th><th>CS</th></tr>
</thead>
<tbody>
<tr><th>Alpha FC</th><td>2</td><td>38</td><td>3,420</td><td>41</td><td>105</td><td>13</td></tr>
<tr><th>Beta United</th><td>1</td><td>38</td><td>3,420</td><td>34</td><td>98</td><td>15</td></tr>
</tbody></table>
"""

PLAYER_TABLE = """
<table id="stats_standard">
<thead>
<tr><th colspan="5"></th><th colspan="3">Playing Time</th><th colspan="2">Performance</th></tr>
<tr><th>Rk</th><th>Player</th><th>Nation</th><th>Pos</th><th>Squad</th><th>MP</th><th>Starts</th><th>Min</th><th>Gls</th><th>Ast</th></tr>
</thead>
<tbody>
<tr><th>1</th><td>Ann Striker</td><td>xx XXX</td><td>FW</td><td>Alpha FC</td><td>36</td><td>35</td><td>3,100</td><td>29</td><td>18</td></tr>
<tr><th>2</th><td>Bob Winger</td><td>yy YYY</td><td>MF,FW</td><td>Beta United</td><td>38</td><td>37</td><td>3,300</td><td>29</td><td>5</td></tr>
<tr><th>3</th><td>Cal Mid</td><td>zz ZZZ</td><td>MF</td><td>Gamma Town</td><td>30</td><td>20</td><td>1,800</td><td>10</td><td>9</td></tr>
<tr><th>Rk</th><td>Player</td><td>Nation</td><td>Pos</td><td>Squad</td><td>MP</td><td>Starts</td><td>Min</td><td>Gls</td><td>Ast</td></tr>
<tr><th>4</th><td>Dan Back</td><td>zz ZZZ</td><td>DF</td><td>Gamma Town</td><td>38</td><td>38</td><td>3,420</td><td>2</td><td>1</td></tr>
</tbody></table>
"""

def season_page(hidden: bool = True) -> str:
    """Season overview page; keeper table hidden in a comment like on the real site."""
    keeper = f"<!--{KEEPER_TABLE}-->" if hidden else KEEPER_TABLE
    return f"<html><body>{STANDINGS_TABLE}<div>{keeper}</div></body></html>"


def players_page() -> str:
    return f"<html><body><!--{PLAYER_TABLE}--></body></html>"


