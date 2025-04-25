import random
import time
from draw import *

# used symbols

bloc = '■'
star = 'O'
play = '@'
spac = 's'
goal = '👸🏻'
tres = '💰'
walx = '■'
waly = '■'
noth = '■'
left = '←'
right = '→'
top = '↑'
down = '↓'

# categories

walls = [bloc, walx, waly, noth]
killer_objects = [*walls, goal, tres, star]

# world

START_POS = (9, 7)


def init_grid():
    grid = [
        [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, noth, noth, noth, noth, noth, noth, waly,
         waly,
         waly, waly, waly, waly, waly, waly, waly, waly],
        [walx, tres, bloc, spac, spac, spac, spac, spac, spac, spac, walx, spac, waly, waly, spac, spac, spac, spac,
         bloc,
         spac, spac, spac, spac, bloc, bloc, bloc, walx],
        [walx, spac, spac, bloc, bloc, spac, spac, bloc, spac, spac, walx, spac, waly, spac, waly, waly, spac, walx,
         bloc,
         spac, bloc, spac, spac, bloc, spac, bloc, walx],
        [walx, spac, bloc, spac, spac, spac, spac, bloc, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac,
         spac,
         spac, bloc, spac, spac, spac, spac, spac, walx],
        [walx, spac, spac, spac, spac, spac, bloc, bloc, spac, spac, walx, spac, waly, spac, waly, spac, waly, walx,
         bloc,
         bloc, bloc, bloc, spac, spac, bloc, spac, walx],
        [walx, bloc, bloc, spac, bloc, spac, bloc, spac, spac, spac, spac, spac, walx, spac, waly, spac, spac, walx,
         spac,
         spac, spac, spac, spac, spac, spac, spac, walx],
        [walx, spac, spac, spac, bloc, spac, bloc, spac, bloc, spac, walx, spac, walx, spac, waly, waly, spac, walx,
         bloc,
         spac, bloc, bloc, spac, goal, spac, spac, walx],
        [walx, spac, spac, spac, bloc, spac, spac, spac, bloc, spac, walx, spac, walx, spac, spac, waly, spac, spac,
         spac,
         spac, spac, spac, spac, spac, spac, spac, walx],
        [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, noth, waly, waly, waly, waly, noth, waly,
         waly,
         waly, waly, waly, waly, waly, waly, waly, waly],
    ]
    grid[START_POS[1]][START_POS[0]] = star
    grid_size_y = len(grid)
    grid_size_x = len(grid[0])

    return grid, grid_size_x, grid_size_y


ALL_ACTIONS = [left, right, top, down]
start_values = [0.00111, 0.00222, 0.00333, 0.00444]

# qlearning specific

EPSILON = 0.05
GAMMA = 0.95
ALPHA = 0.2
EPISODES = 200000
Q = {}

# counter

tres_counter = 0
goal_counter = 0
start_counter = 0
wall_counter = 0
step_counter = 0



def initialize_q(grid_size_x, grid_size_y):
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            start_values_copy = start_values.copy()
            random.shuffle(start_values_copy)
            Q[(x, y)] = {action: start_values_copy.pop() for action in ALL_ACTIONS}


def move(current_position, desired_action, grid_size_x, grid_size_y):
    x, y = current_position
    if (desired_action == left) and x > 0:
        x -= 1
    elif (desired_action == right) and x < grid_size_x - 1:
        x += 1
    elif (desired_action == top) and y > 0:
        y -= 1
    elif (desired_action == down) and y < grid_size_y - 1:
        y += 1
    return (x, y)


def calculate_reward(current_position, grid):
    current_symbol = get_symbol(current_position, grid)
    if current_symbol == star:
        global start_counter
        start_counter += 1
        return -100
    elif current_symbol == goal:
        global goal_counter
        goal_counter += 1
        return 10000
    elif current_symbol == tres:
        global tres_counter
        tres_counter += 1
        return 0.1
    elif current_symbol in walls:
        global wall_counter
        wall_counter += 1
        return -10
    else:
        global step_counter
        step_counter += 1
        return -0.1


def get_allowed_actions(current_position, grid_size_x, grid_size_y):
    allowed_actions = []
    for action in ALL_ACTIONS:
        next_position = move(current_position, action, grid_size_x, grid_size_y)
        if next_position != current_position:  # and grid[next_position[1]][next_position[0]] not in walls:
            allowed_actions.append(action)
    return allowed_actions


def get_best_action(q, actions_to_pick_from, position):
    max_value = max(q[position][a] for a in actions_to_pick_from)
    best_actions = [a for a in actions_to_pick_from if q[position][a] == max_value]  # maybe more than one
    return random.choice(best_actions)  # pick one


def pick_best_or_random_action(current_position, q, epsilon, grid_size_x, grid_size_y):
    allowed_actions = get_allowed_actions(current_position, grid_size_x, grid_size_y)
    if random.random() < epsilon:
        return random.choice(allowed_actions)
    else:
        return get_best_action(q, allowed_actions, current_position)


# Q-Learning Algorithmus
def q_learning(stdscr, grid, grid_size_x, grid_size_y):
    initialize_q(grid_size_x, grid_size_y)
    speed = 16
    curses.curs_set(0)
    for e in range(EPISODES):
        player_current_pos = START_POS
        episode_ended = False
        step = 0
        while not episode_ended:
            key = stdscr.getch()
            if key == ord('+'):
                speed = speed * 2
            elif key == ord('-'):
                speed = speed / 2

            action = pick_best_or_random_action(player_current_pos, Q, EPSILON, grid_size_x, grid_size_y)
            new_player_pos = move(player_current_pos, action, grid_size_x, grid_size_y)
            update_heatmap(e, new_player_pos)
            reward = calculate_reward(new_player_pos, grid)

            new_q, old_q = update_q(action, player_current_pos, new_player_pos, reward)

            player_dead = get_symbol(new_player_pos, grid) in killer_objects
            draw_grid(stdscr, new_player_pos, e, action, reward, old_q, new_q, step, player_dead, speed, grid_size_x, grid_size_y, grid, Q)
            wait_for_draw(speed)

            player_current_pos = new_player_pos
            step += 1

            if player_dead:
                episode_ended = True
                for _ in range(3):
                    wait_for_draw(speed)


def get_symbol(position, grid):
    x, y = position
    return grid[y][x]


def update_q(action, current_player_pos, new_player_pos, reward):
    old_q = Q[current_player_pos][action]
    future_q = max(Q[new_player_pos].values())
    new_q = old_q + ALPHA * (reward + GAMMA * future_q - old_q)
    Q[current_player_pos][action] = new_q
    return new_q, old_q


def wait_for_draw(speed):
    time.sleep(1 / speed)


def main():
    grid, grid_size_x, grid_size_y = init_grid()
    stdscr = init_draw(grid_size_x, grid_size_y)

    try:
        q_learning(stdscr, grid, grid_size_x, grid_size_y)
    finally:
        finish_draw(stdscr, grid_size_x, grid_size_y)


if __name__ == "__main__":
    main()
