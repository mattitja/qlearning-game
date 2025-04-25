import random
import time

from draw import *

BLOCK = '■'
START = 'O'
PLAYR = '@'
SPACE = 's'
GOALL = '👸🏻'
TRESR = '💰'
WALLX = '■'
WALLY = '■'
NTHNG = '■'
ACTION_LEFT = '←'
ACTION_RIGHT = '→'
ACTION_TOP = '↑'
ACTION_BOTTOM = '↓'

WALLS = [BLOCK, WALLX, WALLY, NTHNG]
KILLER_OBJECTS = [*WALLS, GOALL, TRESR, START]

START_POS = (9, 7)

ALL_ACTIONS = [ACTION_LEFT, ACTION_RIGHT, ACTION_TOP, ACTION_BOTTOM]
START_VALUES = [0.00111, 0.00222, 0.00333, 0.00444]

EPSILON = 0.05
GAMMA = 0.95
ALPHA = 0.2
START_SPEED = 16
EPISODES = 200000

tres_counter = 0
goal_counter = 0
start_counter = 0
wall_counter = 0
step_counter = 0

def init_grid():
    grid = [
        [WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, NTHNG, NTHNG, NTHNG, NTHNG, NTHNG, NTHNG, WALLY,
         WALLY,
         WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY],
        [WALLX, TRESR, BLOCK, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, WALLX, SPACE, WALLY, WALLY, SPACE, SPACE, SPACE, SPACE,
         BLOCK,
         SPACE, SPACE, SPACE, SPACE, BLOCK, BLOCK, BLOCK, WALLX],
        [WALLX, SPACE, SPACE, BLOCK, BLOCK, SPACE, SPACE, BLOCK, SPACE, SPACE, WALLX, SPACE, WALLY, SPACE, WALLY, WALLY, SPACE, WALLX,
         BLOCK,
         SPACE, BLOCK, SPACE, SPACE, BLOCK, SPACE, BLOCK, WALLX],
        [WALLX, SPACE, BLOCK, SPACE, SPACE, SPACE, SPACE, BLOCK, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE,
         SPACE,
         SPACE, BLOCK, SPACE, SPACE, SPACE, SPACE, SPACE, WALLX],
        [WALLX, SPACE, SPACE, SPACE, SPACE, SPACE, BLOCK, BLOCK, SPACE, SPACE, WALLX, SPACE, WALLY, SPACE, WALLY, SPACE, WALLY, WALLX,
         BLOCK,
         BLOCK, BLOCK, BLOCK, SPACE, SPACE, BLOCK, SPACE, WALLX],
        [WALLX, BLOCK, BLOCK, SPACE, BLOCK, SPACE, BLOCK, SPACE, SPACE, SPACE, SPACE, SPACE, WALLX, SPACE, WALLY, SPACE, SPACE, WALLX,
         SPACE,
         SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, WALLX],
        [WALLX, SPACE, SPACE, SPACE, BLOCK, SPACE, BLOCK, SPACE, BLOCK, SPACE, WALLX, SPACE, WALLX, SPACE, WALLY, WALLY, SPACE, WALLX,
         BLOCK,
         SPACE, BLOCK, BLOCK, SPACE, GOALL, SPACE, SPACE, WALLX],
        [WALLX, SPACE, SPACE, SPACE, BLOCK, SPACE, SPACE, SPACE, BLOCK, SPACE, WALLX, SPACE, WALLX, SPACE, SPACE, WALLY, SPACE, SPACE,
         SPACE,
         SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, SPACE, WALLX],
        [WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, NTHNG, WALLY, WALLY, WALLY, WALLY, NTHNG, WALLY,
         WALLY,
         WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY, WALLY],
    ]
    grid[START_POS[1]][START_POS[0]] = START
    grid_size_y = len(grid)
    grid_size_x = len(grid[0])

    return grid, grid_size_x, grid_size_y

def initialize_q(grid_size_x, grid_size_y):
    q = {}
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            start_values_copy = START_VALUES.copy()
            random.shuffle(start_values_copy)
            q[(x, y)] = {action: start_values_copy.pop() for action in ALL_ACTIONS}
    return q


def move_player(current_position, desired_action, grid_size_x, grid_size_y):
    x, y = current_position
    if (desired_action == ACTION_LEFT) and x > 0:
        x -= 1
    elif (desired_action == ACTION_RIGHT) and x < grid_size_x - 1:
        x += 1
    elif (desired_action == ACTION_TOP) and y > 0:
        y -= 1
    elif (desired_action == ACTION_BOTTOM) and y < grid_size_y - 1:
        y += 1
    return x, y


def calculate_reward(current_position, grid):
    current_symbol = get_symbol(current_position, grid)
    if current_symbol == START:
        global start_counter
        start_counter += 1
        return -100
    elif current_symbol == GOALL:
        global goal_counter
        goal_counter += 1
        return 10000
    elif current_symbol == TRESR:
        global tres_counter
        tres_counter += 1
        return 0.1
    elif current_symbol in WALLS:
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
        next_position = move_player(current_position, action, grid_size_x, grid_size_y)
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


def q_learning(screen, grid, grid_size_x, grid_size_y, heatmap):
    q = initialize_q(grid_size_x, grid_size_y)
    speed = initialize_speed()
    for e in range(EPISODES):
        episode_ended, player_current_pos, step = start_episode()
        while not episode_ended:
            speed = adjust_speed(speed, screen)

            action = pick_best_or_random_action(player_current_pos, q, EPSILON, grid_size_x, grid_size_y)
            player_new_pos = move_player(player_current_pos, action, grid_size_x, grid_size_y)
            reward = calculate_reward(player_new_pos, grid)

            heatmap = update_heatmap(e, player_new_pos, heatmap)

            new_q, old_q = update_q(action, player_current_pos, player_new_pos, reward, q)

            player_dead = get_symbol(player_new_pos, grid) in KILLER_OBJECTS

            draw_grid(screen, player_new_pos, e, action, reward, old_q, new_q, step, player_dead, speed, grid_size_x, grid_size_y, grid, q, heatmap)
            wait_for_draw(speed)

            player_current_pos = player_new_pos
            step += 1

            if player_dead:
                episode_ended = True
                for _ in range(3):
                    wait_for_draw(speed)


def start_episode():
    player_current_pos = START_POS
    episode_ended = False
    step = 0
    return episode_ended, player_current_pos, step


def initialize_speed():
    return START_SPEED

def reset_step_counter():
    return 0

def reset_player():
    return START_POS

def adjust_speed(speed, screen):
    key = screen.getch()
    if key == ord('+'):
        speed = speed * 2
    elif key == ord('-'):
        speed = speed / 2
    return speed


def get_symbol(position, grid):
    x, y = position
    return grid[y][x]


def update_q(action, current_player_pos, new_player_pos, reward, q):
    old_q = q[current_player_pos][action]
    future_q = max(q[new_player_pos].values())
    new_q = old_q + ALPHA * (reward + GAMMA * future_q - old_q)
    q[current_player_pos][action] = new_q
    return new_q, old_q


def wait_for_draw(speed):
    time.sleep(1 / speed)


def main():
    grid, grid_size_x, grid_size_y = init_grid()
    screen = init_draw()
    heatmap = init_heatmap(grid_size_x, grid_size_y)

    try:
        q_learning(screen, grid, grid_size_x, grid_size_y, heatmap)
    finally:
        finish_draw(screen, grid_size_y)


if __name__ == "__main__":
    main()
