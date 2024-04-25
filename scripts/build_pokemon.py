def _build_stats_table(stats: dict):
    for key in ["hp", "attack", "defense", "special attack", "special defense", "speed"]:
        print(f"<tr>")
        print(f'<th scope="row">{key}</th>')
        print(f'<td>{stats[key]}</td>')
        print(f'<td style="width:255px">')
        print(f'<div style="background-color:black;height:20px;width:calc(100%*{stats[key]}/255)"></div>')
        print(f'</td>')
        print(f"</tr>")

def builder(data: dict):
    print("<!DOCTYPE html>")
    print(f"<html>")
    print(f"<head></head>")
    print(f"<body>")
    print(f"<h1>{data['name']}</h1>")
    print(f"<p>{data['form']}</p>")
    print(f"<p>{' '.join(data['types'])}</p>")
    print(f"<h2>Stats</h2>")
    print(f"<table>")
    _build_stats_table(data['stats'])
    print(f"</table>")
    print(f"</body>")
    print(f"</html>")
