import random
import time
import os

grid = [
    ['A', ' ', ' ', ' '],
    [' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' '],
    [' ', ' ', ' ', 'Z'],
]

Q = {}

GRID_SIZE = len(grid)

ALL_ACTIONS = ['L', 'R', 'U', 'D']
EPSILON = 0.1

for s in range(len(ALL_ACTIONS)):
    for a in range(len(ALL_ACTIONS)):
        Q[(s, a)] = {action: 0 for action in ALL_ACTIONS}

def move (current_position, desired_action):
    x, y = current_position
    if (desired_action == 'L') and x > 0:
        x -= 1
    elif (desired_action == 'R') and x < GRID_SIZE - 1:
        x += 1
    elif (desired_action == 'U') and y > 0:
        y -= 1
    elif (desired_action == 'D') and y < GRID_SIZE - 1:
        y += 1
    return (x, y)

def get_reward(current_position):
    x, y = current_position
    if grid[y][x] == 'A':
        return -1
    elif grid[y][x] == 'Z':
        return 100
    else:
        return -0.1

def get_allowed_actions(current_position):
    x, y = current_position
    allowed_actions = []
    for action in ALL_ACTIONS:
        next_position = move(current_position, action)
        if next_position != current_position:
            allowed_actions.append(action)
    return allowed_actions

# def get_best_action(q, actions, position):
#     return max(actions, key=lambda a: q[position][a])


def get_best_action(q, actions_to_pick_from, position):
    max_value = max(q[position][a] for a in actions_to_pick_from)
    best_actions = [a for a in actions_to_pick_from if q[position][a] == max_value] #maybe more than one
    return random.choice(best_actions) # pick one

def choose_action(current_position, q):
    allowed_actions = get_allowed_actions(current_position)
    if random.random() < EPSILON:
        return random.choice(allowed_actions)
    else:
        return get_best_action(q, allowed_actions, current_position)

def print_policy():
    for x in range(GRID_SIZE):
        row = ''
        for y in range(GRID_SIZE):
            letter = None
            if grid[x][y] in ('A', 'Z'):
                letter = grid[x][y]
            else:
                letter = get_best_action(Q, ALL_ACTIONS, (x, y))
            row += " " + letter + " "
        print(row)


if __name__ == "__main__":
    print(Q)
