import csv
from pathlib import Path

import agents
from campus import BUILDING_NAMES, CampusMap

TASKS = [
    ("Baseline", "maps/emu_campus.txt", "S", "W"),
    ("Baseline", "maps/emu_campus.txt", "L", "D"),
    ("Baseline", "maps/emu_campus.txt", "H", "P"),
    ("Detour", "maps/emu_detour.txt", "S", "W"),
    ("Detour", "maps/emu_detour.txt", "L", "D"),
    ("Detour", "maps/emu_detour.txt", "H", "P"),
    ("Custom", "maps/my_campus.txt", "S", "W"),
]


def route_length(result):
    return len(result.path) - 1 if result.path is not None else "NA"


def main():
    base = Path(__file__).parent
    rows = []
    for label, map_file, start_letter, goal_letter in TASKS:
        campus = CampusMap(str(base / map_file))
        start, goal = campus.location(start_letter), campus.location(goal_letter)
        bfs_result = agents.bfs(campus, start, goal)
        astar_result = agents.astar(campus, start, goal)
        rows.append({
            "map": label,
            "map_file": map_file,
            "task": start_letter + "->" + goal_letter,
            "start": BUILDING_NAMES[start_letter],
            "goal": BUILDING_NAMES[goal_letter],
            "bfs_route_length": route_length(bfs_result),
            "astar_route_length": route_length(astar_result),
            "bfs_expanded": bfs_result.expanded,
            "astar_expanded": astar_result.expanded,
        })
    output = base / "results" / "search"
    output.mkdir(parents=True, exist_ok=True)
    with open(output / "search_results.csv", "w", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(row["map"], row["task"], row["bfs_route_length"], row["astar_route_length"],
              row["bfs_expanded"], row["astar_expanded"])
    print("Wrote", output / "search_results.csv")


if __name__ == "__main__":
    main()
