import curses
import random
import time

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

grid = [
    [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, noth, noth, noth, noth, noth, noth, waly, waly,
     waly, waly, waly, waly, waly, waly, waly, waly],
    [walx, tres, bloc, spac, spac, spac, spac, spac, spac, spac, walx, spac, waly, waly, spac, spac, spac, spac, bloc,
     spac, spac, spac, spac, bloc, bloc, bloc, walx],
    [walx, spac, spac, bloc, bloc, spac, spac, bloc, spac, spac, walx, spac, waly, spac, waly, waly, spac, walx, bloc,
     spac, bloc, spac, spac, bloc, spac, bloc, walx],
    [walx, spac, bloc, spac, spac, spac, spac, bloc, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac,
     spac, bloc, spac, spac, spac, spac, spac, walx],
    [walx, spac, spac, spac, spac, spac, bloc, bloc, spac, spac, walx, spac, waly, spac, waly, spac, waly, walx, bloc,
     bloc, bloc, bloc, spac, spac, bloc, spac, walx],
    [walx, bloc, bloc, spac, bloc, spac, bloc, spac, spac, spac, spac, spac, walx, spac, waly, spac, spac, walx, spac,
     spac, spac, spac, spac, spac, spac, spac, walx],
    [walx, spac, spac, spac, bloc, spac, bloc, spac, bloc, spac, walx, spac, walx, spac, waly, waly, spac, walx, bloc,
     spac, bloc, bloc, spac, goal, spac, spac, walx],
    [walx, spac, spac, spac, bloc, spac, spac, spac, bloc, spac, walx, spac, walx, spac, spac, waly, spac, spac, spac,
     spac, spac, spac, spac, spac, spac, spac, walx],
    [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, noth, waly, waly, waly, waly, noth, waly, waly,
     waly, waly, waly, waly, waly, waly, waly, waly],
]

START_POS = (9, 7)

grid[START_POS[1]][START_POS[0]] = star

GRID_SIZE_Y = len(grid)
GRID_SIZE_X = len(grid[0])

ALL_ACTIONS = [left, right, top, down]

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

# color pairs

WHITE_ON_BLACK = 4
YELLOW_ON_BLACK = 5
GREEN_ON_BLACK = 2
MAGENTA_ON_BLACK = 6
CYAN_ON_BLACK = 3
RED_ON_BLACK = 1
GREY_ON_BLACK = 7
BLUE_ON_BLACK = 8
LIGHT_GREY_ON_BLACK = 15
BLACK_ON_BLACK = 16

# heatmap

heatmap = [[0 for _ in range(GRID_SIZE_X)] for _ in range(GRID_SIZE_Y)]
start_values = [0.00111, 0.00222, 0.00333, 0.00444]


def initialize_q():
    for x in range(GRID_SIZE_X):
        for y in range(GRID_SIZE_Y):
            start_values_copy = start_values.copy()
            random.shuffle(start_values_copy)
            Q[(x, y)] = {action: start_values_copy.pop() for action in ALL_ACTIONS}


def move(current_position, desired_action):
    x, y = current_position
    if (desired_action == left) and x > 0:
        x -= 1
    elif (desired_action == right) and x < GRID_SIZE_X - 1:
        x += 1
    elif (desired_action == top) and y > 0:
        y -= 1
    elif (desired_action == down) and y < GRID_SIZE_Y - 1:
        y += 1
    return (x, y)


def calculate_reward(current_position):
    current_symbol = get_symbol(current_position)
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


def get_allowed_actions(current_position):
    allowed_actions = []
    for action in ALL_ACTIONS:
        next_position = move(current_position, action)
        if next_position != current_position:  # and grid[next_position[1]][next_position[0]] not in walls:
            allowed_actions.append(action)
    return allowed_actions


def get_best_action(q, actions_to_pick_from, position):
    max_value = max(q[position][a] for a in actions_to_pick_from)
    best_actions = [a for a in actions_to_pick_from if q[position][a] == max_value]  # maybe more than one
    return random.choice(best_actions)  # pick one


def pick_best_or_random_action(current_position, q, epsilon):
    allowed_actions = get_allowed_actions(current_position)
    if random.random() < epsilon:
        return random.choice(allowed_actions)
    else:
        return get_best_action(q, allowed_actions, current_position)


def draw_grid(stdscr, current_player_pos, episode, action, reward, old_q, new_q, step, player_dead, speed):
    stdscr.clear()
    current_player_pos_x, current_player_pos_y = current_player_pos
    for draw_y in range(GRID_SIZE_Y):
        for draw_x in range(GRID_SIZE_X):
            # Position des Cursors setzen
            draw_one_grid_slot(current_player_pos_x, current_player_pos_y, draw_x, draw_y, player_dead, stdscr)

    draw_statistics(action, episode, new_q, old_q, player_dead, reward, speed, stdscr, step)
    stdscr.refresh()

    wait_for_draw(speed)


def draw_one_grid_slot(current_player_pos_x, current_player_pos_y, draw_x, draw_y, player_dead, stdscr):
    draw_pos = (draw_x, draw_y)
    stdscr.move(draw_y, draw_x * 3)  # Jedes Symbol ist 3 Zeichen breit (z. B. " X ")

    symbol = determine_symbol(current_player_pos_x, current_player_pos_y, draw_pos)
    color = determine_symbol_color(draw_pos, player_dead, symbol)
    stdscr.addstr(f" {symbol} ", color)


def determine_symbol_color(draw_pos, player_dead, symbol):
    if symbol == play:
        if player_dead:
            color = curses.color_pair(RED_ON_BLACK)
        else:
            color = curses.color_pair(WHITE_ON_BLACK)
    elif symbol == goal or symbol == star:
        color = curses.color_pair(YELLOW_ON_BLACK)
    elif symbol in ALL_ACTIONS:
        if Q[draw_pos][symbol] in start_values:
            color = curses.color_pair(GREY_ON_BLACK)
        else:
            color = get_color_heatmap(draw_pos)
    elif symbol == bloc or symbol == waly or symbol == walx:
        color = curses.color_pair(WHITE_ON_BLACK)
    else:
        color = curses.color_pair(LIGHT_GREY_ON_BLACK)
    return color


def determine_symbol(current_player_pos_x, current_player_pos_y, draw_pos):
    if draw_pos[0] == current_player_pos_x and draw_pos[1] == current_player_pos_y:
        symbol = play
    else:
        symbol = get_symbol(draw_pos)
    if symbol == spac:
        symbol = get_best_action(Q, ALL_ACTIONS, draw_pos)
    return symbol


def draw_statistics(action, episode, new_q, old_q, player_dead, reward, speed, stdscr, step):
    lineNumber = GRID_SIZE_Y
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "")
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Speed: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{speed:.0f}x", curses.color_pair(WHITE_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "")
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Current Step: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"#{step:03} ", curses.color_pair(GREY_ON_BLACK) if player_dead else curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Current Episode: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"#{episode:05} ",
                  curses.color_pair(GREY_ON_BLACK) if player_dead else curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Last Action: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{action}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Last Reward: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{reward:.1f}  ",
                  curses.color_pair(RED_ON_BLACK) if player_dead else curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "")
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Old Q: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{old_q:.5f}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "New Q: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{new_q:.5f}", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "")
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Total steps: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{step_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Total " + f"{bloc}: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{wall_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Total " + f"{tres}: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{tres_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Total " + f"{goal}: ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{goal_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "")
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Epsilon (Explorationsrate): ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{EPSILON:.2f}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Alpha (Lernrate): ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{ALPHA:.2f}  ", curses.color_pair(GREY_ON_BLACK))
    lineNumber += 1
    stdscr.addstr(lineNumber, 0, "Gamma (Langfristigkeit): ", curses.color_pair(WHITE_ON_BLACK))
    stdscr.addstr(f"{GAMMA:.2f}  ", curses.color_pair(GREY_ON_BLACK))


def get_heatmap_max():
    return max(max(row) for row in heatmap)


def get_bg_color_ratio(current_position):
    x, y = current_position
    current_value = heatmap[y][x]
    max_value = get_heatmap_max()
    return current_value / max_value


def get_color_heatmap(current_position):
    ratio = get_bg_color_ratio(current_position)
    if 0 <= ratio <= 0.05:
        return curses.color_pair(10)
    elif 0.05 <= ratio <= 0.1:
        return curses.color_pair(11)
    elif 0.1 <= ratio <= 0.2:
        return curses.color_pair(12)
    elif 0.2 <= ratio <= 0.3:
        return curses.color_pair(13)
    else:
        return curses.color_pair(14)


def clear_screen(stdscr):
    stdscr.clear()


# Q-Learning Algorithmus
def q_learning(stdscr):
    initialize_q()
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

            action = pick_best_or_random_action(player_current_pos, Q, EPSILON)
            new_player_pos = move(player_current_pos, action)
            update_heatmap(e, new_player_pos)
            reward = calculate_reward(new_player_pos)

            new_q, old_q = update_q(action, player_current_pos, new_player_pos, reward)

            player_dead = get_symbol(new_player_pos) in killer_objects
            draw_grid(stdscr, new_player_pos, e, action, reward, old_q, new_q, step, player_dead, speed)

            player_current_pos = new_player_pos
            step += 1

            if player_dead:
                episode_ended = True
                for _ in range(3):
                    wait_for_draw(speed)


def get_symbol(position):
    x, y = position
    return grid[y][x]


def update_q(action, current_player_pos, new_player_pos, reward):
    old_q = Q[current_player_pos][action]
    future_q = max(Q[new_player_pos].values())
    new_q = old_q + ALPHA * (reward + GAMMA * future_q - old_q)
    Q[current_player_pos][action] = new_q
    return new_q, old_q


def update_heatmap(e, new_player_pos):
    new_x, new_y = new_player_pos
    heatmap[new_y][new_x] += 0.00001 * (e ** 3)


def wait_for_draw(speed):
    time.sleep(1 / speed)
    return


def init_colors():
    curses.start_color()

    COLOR_GREY = curses.COLOR_WHITE + 1
    COLOR_LIGHT_GREY = 15
    curses.init_color(COLOR_GREY, 400, 400, 400)
    curses.init_color(COLOR_LIGHT_GREY, 600, 600, 600)

    curses.init_pair(RED_ON_BLACK, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(GREEN_ON_BLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(CYAN_ON_BLACK, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(YELLOW_ON_BLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(MAGENTA_ON_BLACK, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(GREY_ON_BLACK, COLOR_GREY, curses.COLOR_BLACK)
    curses.init_pair(BLUE_ON_BLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(LIGHT_GREY_ON_BLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(BLACK_ON_BLACK, curses.COLOR_BLACK, curses.COLOR_BLACK)

    # Heatmap Colors
    curses.init_color(10, 0, 0, 0)
    curses.init_color(11, 0, 250, 0)
    curses.init_color(12, 0, 500, 0)
    curses.init_color(13, 0, 750, 0)
    curses.init_color(14, 0, 1000, 0)
    curses.init_color(COLOR_LIGHT_GREY, 400, 400, 400)
    curses.init_pair(10, COLOR_GREY, curses.COLOR_BLACK)
    curses.init_pair(11, 11, curses.COLOR_BLACK)
    curses.init_pair(12, 12, curses.COLOR_BLACK)
    curses.init_pair(13, 13, curses.COLOR_BLACK)
    curses.init_pair(14, 14, curses.COLOR_BLACK)

    curses.init_pair(LIGHT_GREY_ON_BLACK, COLOR_LIGHT_GREY, curses.COLOR_BLACK)


def main():
    stdscr = curses.initscr()
    init_colors()

    # curses.curs_set(0)
    stdscr.clear()

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)

    try:
        q_learning(stdscr)
    finally:
        stdscr.addstr(GRID_SIZE_Y + 2, 0, "Drücke eine Taste zum Beenden...")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == "__main__":
    main()
