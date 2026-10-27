# Eagle Delivery

COSC 461/561 Project 1 by Hasset Admasu.

A simulated delivery robot carries a package between building entrances on a grid
model of the Eastern Michigan University campus. The project has three parts:

- **Part A**: plan routes on the known map with A* (Manhattan heuristic) and compare it with the supplied BFS baseline.
- **Part B**: learn a delivery policy from experience with tabular Q-learning and epsilon-greedy exploration.
- **Part C**: design a custom campus map and run a controlled experiment on the exploration rate epsilon.

The full write-up is in [EagleDelivery_Report.pdf](EagleDelivery_Report.pdf). Its HTML source and figures are in `report/`.

## Requirements

- Python 3.9 or newer. The simulator, search, learning and tests use only the standard library.
- `matplotlib` is needed only for `analyze_results.py`, which draws the report figures: `pip install -r requirements.txt`.

## Files

| Path | Contents |
|---|---|
| `agents.py` | BFS (supplied), `manhattan`, `astar`, `epsilon_greedy`, `q_learning_update` |
| `campus.py` | Map loading, movement, rewards, resets (supplied) |
| `run_project.py` | CLI: `show`, `search`, `random`, `train` (supplied) |
| `summarize_results.py` | Evaluation summary and `learning_curve.csv` per results folder (supplied) |
| `search_results.py` | Runs BFS and A* on all required tasks and writes `results/search/search_results.csv` |
| `analyze_results.py` | Computes extra training metrics (`results/training_metrics.csv`) and draws `report/figures/*.png` |
| `maps/emu_campus.txt`, `maps/emu_detour.txt` | Supplied 11 x 17 maps (the detour map blocks cell (3, 6)) |
| `maps/my_campus.txt` | Custom 15 x 15 map for Part C |
| `results/` | Raw training and evaluation CSVs, `summary.csv`, `summary.txt`, `learning_curve.csv` for every run |
| `tests/` | Public unit tests |
| `examples/interaction_demo.py` | API demonstration (supplied) |

## Run commands

Run everything from the repository root.

### Tests

```bash
python3 -m unittest discover -v
python3 -m unittest tests.test_student.SearchTests -v
python3 -m unittest tests.test_student.LearningTests -v
```

All 14 tests pass (6 environment tests and 8 student tests).

### Part A: search

```bash
python3 run_project.py show
python3 run_project.py search --algorithm bfs   --start S --goal W
python3 run_project.py search --algorithm astar --start S --goal W
python3 run_project.py search --algorithm astar --map maps/emu_detour.txt --start L --goal D
python3 search_results.py
```

`search_results.py` runs both algorithms on the six required map/task pairs and on the custom S-W task:

| Map | Task | BFS length | A* length | BFS expanded | A* expanded |
|---|---|---|---|---|---|
| Baseline | S -> W | 18 | 18 | 67 | 22 |
| Baseline | L -> D | 22 | 22 | 79 | 62 |
| Baseline | H -> P | 16 | 16 | 41 | 16 |
| Detour | S -> W | 26 | 26 | 70 | 51 |
| Detour | L -> D | 22 | 22 | 65 | 60 |
| Detour | H -> P | 16 | 16 | 41 | 16 |
| Custom | S -> W | 12 | 12 | 38 | 12 |

### Part B: Q-learning baseline

```bash
python3 run_project.py train --map maps/emu_campus.txt --start S --goal W --output results/baseline_SW
python3 run_project.py train --map maps/emu_campus.txt --start L --goal D --output results/baseline_LD
python3 run_project.py train --map maps/emu_campus.txt --start H --goal P --output results/baseline_HP
python3 summarize_results.py results/baseline_SW
python3 summarize_results.py results/baseline_LD
python3 summarize_results.py results/baseline_HP
```

### Part C: custom map experiment

```bash
python3 run_project.py search --map maps/my_campus.txt --algorithm bfs
python3 run_project.py search --map maps/my_campus.txt --algorithm astar
python3 run_project.py train --map maps/my_campus.txt --start S --goal W --epsilon 0.05 --output results/custom_e005
python3 run_project.py train --map maps/my_campus.txt --start S --goal W --epsilon 0.2  --output results/custom_e020
python3 run_project.py train --map maps/my_campus.txt --start S --goal W --epsilon 0.5  --output results/custom_e050
python3 summarize_results.py results/custom_e005
python3 summarize_results.py results/custom_e020
python3 summarize_results.py results/custom_e050
```

### Metrics and figures

```bash
python3 analyze_results.py
```

`run_project.py train` refuses to write into a folder that already contains CSVs, so use a new output directory (or delete the old one) for each rerun. All runs are deterministic for a given seed, so rerunning reproduces the committed CSVs exactly.

## Experiment settings

| Setting | Part B baseline | Part C experiment |
|---|---|---|
| Map | `maps/emu_campus.txt` | `maps/my_campus.txt` |
| Tasks | S->W, L->D, H->P | S->W |
| Training episodes | 2,000 per seed | 2,000 per seed |
| Evaluation episodes | 100 per seed (epsilon = 0, learning frozen) | 100 per seed (epsilon = 0, learning frozen) |
| Seeds | 0, 1, 2 | 0, 1, 2 for each setting |
| Max actions per episode | 200 | 200 |
| Learning rate alpha | 0.3 | 0.3 |
| Discount gamma | 0.95 | 0.95 |
| Exploration epsilon | 0.2, constant | **0.05, 0.2, 0.5** (the only factor varied) |
| Slip probability | 0.0 | 0.0 |

Each seed and condition starts from a fresh, empty Q-table.

## Custom map

```
###############
#S...........W#
#.#####.#####.#
#.#####.#####.#
#.#.###.#####.#
#.#.###.#####.#
#.#.###.#####.#
#L...........D#
#.#####.#####.#
#.#####.#####.#
#.#####.#####.#
#.#####.#####.#
#.#####.#####.#
#H.....P......#
###############
```

- **Loops**: the three vertical corridors (columns 1, 7, 13) and three horizontal corridors (rows 1, 7, 13) form rectangular cycles, for example S -> (1,7) -> (7,7) -> L -> S.
- **Dead end**: the stub in column 3, rows 4-6, open only from (7,3).
- **S->W route choices**: direct along row 1 (12 moves), via column 7 or column 1 and row 7 (24 moves), or via row 13 (36 moves).

## Key results

- **Part A**: BFS and A* always found routes of the same length. A* expanded fewer nodes in every required case, but its saving ranged from 8% (detour L->D) to 67% (baseline S->W), depending on how closely the Manhattan distance matches the true distance around walls.
- **Part B**: all 9 runs reach 100% evaluation success with BFS-optimal routes (18, 22, 16 steps; returns 22, 18, 24). Training stays a few steps above optimal because epsilon = 0.2 is never decayed.
- **Part C**: epsilon had no effect on the final greedy policy (100% success, optimal 12 steps for every seed), but it strongly affected training cost: mean steps over the last 500 training episodes were 12.7, 15.1 and 24.7 for epsilon = 0.05, 0.2 and 0.5.
