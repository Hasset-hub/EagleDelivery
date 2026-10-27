from collections import deque
import heapq
from itertools import count


class SearchResult:
    def __init__(self, path, expanded):
        self.path = path
        self.expanded = expanded


def reconstruct_path(parents, goal):
    path = []
    state = goal
    while state is not None:
        path.append(state)
        state = parents[state]
    path.reverse()
    return path


def bfs(campus, start, goal):
    frontier = deque([start])
    parents = {start: None}
    expanded = 0
    while frontier:
        state = frontier.popleft()
        if state == goal:
            return SearchResult(reconstruct_path(parents, goal), expanded)
        expanded += 1
        for action, successor in campus.neighbors(state):
            if successor not in parents:
                parents[successor] = state
                frontier.append(successor)
    return SearchResult(None, expanded)


def manhattan(state, goal):
    return abs(state[0] - goal[0]) + abs(state[1] - goal[1])


def astar(campus, start, goal):
    if start == goal:
        return SearchResult([start], 0)

    g_costs = {start: 0}
    parents = {start: None}

    insertion_counter = count()
    h_start = manhattan(start, goal)
    frontier = [(h_start + 0, next(insertion_counter), 0, start)]

    expanded = 0

    while frontier:
        f, _, g, state = heapq.heappop(frontier)

        if g > g_costs.get(state, float('inf')):
            continue

        if state == goal:
            return SearchResult(reconstruct_path(parents, goal), expanded)

        expanded += 1
        for action, successor in campus.neighbors(state):
            new_g = g + 1
            if new_g < g_costs.get(successor, float('inf')):
                g_costs[successor] = new_g
                parents[successor] = state
                h = manhattan(successor, goal)
                new_f = new_g + h
                heapq.heappush(frontier, (new_f, next(insertion_counter), new_g, successor))

    return SearchResult(None, expanded)


def epsilon_greedy(q_values, state, actions, epsilon, rng):
    if rng.random() < epsilon:
        return rng.choice(actions)
    else:
        best_value = max(q_values.get((state, a), 0.0) for a in actions)
        best_actions = [a for a in actions if q_values.get((state, a), 0.0) == best_value]
        return rng.choice(best_actions)


def q_learning_update(q_values, state, action, reward, next_state,
                      actions, alpha, gamma, terminal):
    current_q = q_values.get((state, action), 0.0)

    if terminal:
        target = reward
    else:
        max_next_q = max(q_values.get((next_state, a), 0.0) for a in actions)
        target = reward + gamma * max_next_q

    q_values[(state, action)] = current_q + alpha * (target - current_q)
