import copy
import random
import curses
import time

bloc = '#'
star = 'O'
play = '@'
spac = 's'
goal = 'X'
tres = 'T'
walx = '|'
waly = '='
noth = ' '

walls = [bloc, walx, waly]
finish = [*walls, goal, tres, star]

grid = [
    [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, noth, noth, noth, noth, noth, noth, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly],
    [walx, spac, bloc, spac, spac, spac, spac, spac, spac, spac, walx, noth, waly, waly, waly, noth, noth, walx, spac, spac, bloc, spac, spac, spac, spac, spac, bloc, spac, walx],
    [walx, spac, star, bloc, bloc, spac, spac, bloc, spac, spac, walx, waly, waly, spac, waly, waly, waly, walx, spac, bloc, bloc, spac, bloc, spac, spac, bloc, goal, bloc, walx],
    [walx, spac, bloc, spac, spac, spac, spac, bloc, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac, bloc, spac, spac, bloc, spac, spac, walx],
    [walx, spac, spac, spac, spac, spac, bloc, bloc, spac, bloc, walx, waly, waly, spac, waly, waly, waly, walx, bloc, spac, bloc, bloc, bloc, bloc, spac, bloc, bloc, spac, walx],
    [walx, bloc, bloc, spac, bloc, spac, bloc, spac, spac, spac, walx, noth, walx, spac, waly, noth, noth, walx, spac, spac, spac, spac, spac, bloc, spac, spac, spac, spac, walx],
    [walx, spac, spac, spac, bloc, spac, bloc, spac, bloc, spac, walx, noth, walx, spac, waly, waly, noth, walx, spac, spac, bloc, bloc, bloc, bloc, spac, spac, bloc, bloc, walx],
    [walx, spac, spac, spac, bloc, spac, spac, spac, bloc, spac, walx, noth, walx, spac, spac, waly, noth, walx, bloc, spac, spac, spac, spac, bloc, spac, spac, spac, spac, walx],
    [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, noth, waly, waly, waly, waly, noth, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly],
]

Q = {}

GRID_SIZE_Y = len(grid)
GRID_SIZE_X = len(grid[0])

left = '←'
right = '→'
top = '↑'
down = '↓'

start_values = [0.00111, 0.00222, 0.00333, 0.00444]

ALL_ACTIONS = [left, right, top, down]

for x in range(GRID_SIZE_X):
    for y in range(GRID_SIZE_Y):
        start_values_copy = start_values.copy()
        random.shuffle(start_values_copy)
        print(start_values_copy)
        Q[(x, y)] = {action: start_values_copy.pop() for action in ALL_ACTIONS}
        print(Q[(x, y)])
        #time.sleep(10)

def move (current_position, desired_action):
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

def get_reward(current_position):
    x, y = current_position
    if grid[y][x] == star:
        return -100
    elif grid[y][x] == goal:
        return 100
    elif grid[y][x] == tres:
        return 1
    elif grid[y][x] in walls:
        return -10
    else:
        return -0.1

def get_allowed_actions(current_position):
    allowed_actions = []
    for action in ALL_ACTIONS:
        next_position = move(current_position, action)
        if next_position != current_position:
            allowed_actions.append(action)
    return allowed_actions

def get_best_action(q, actions_to_pick_from, position):
    max_value = max(q[position][a] for a in actions_to_pick_from)
    best_actions = [a for a in actions_to_pick_from if q[position][a] == max_value] #maybe more than one
    return random.choice(best_actions) # pick one

def choose_action(current_position, q, epsilon):
    allowed_actions = get_allowed_actions(current_position)
    if random.random() < epsilon:
        return random.choice(allowed_actions)
    else:
        return get_best_action(q, allowed_actions, current_position)

def print_policy(stdscr):
    stdscr.clear()
    for y in range(GRID_SIZE_Y):
        row = ''
        for x in range(GRID_SIZE_X):
            current_position = (x, y)
            if grid[y][x] in (star, goal, *walls):
                letter = grid[y][x]
            else:
                letter = get_best_action(Q, get_allowed_actions(current_position), current_position)
            row += " " + letter + " "
        stdscr.addstr(y, 0, row)

def draw_grid(stdscr, current_player_pos, episode, action, reward, old_q, new_q):
    stdscr.clear()
    current_player_pos_x, current_player_pos_y = current_player_pos
    for draw_y in range(GRID_SIZE_Y):
        for draw_x in range(GRID_SIZE_X):
            # Position des Cursors setzen
            draw_pos = (draw_x,draw_y)
            stdscr.move(draw_y, draw_x * 3)  # Jedes Symbol ist 3 Zeichen breit (z. B. " X ")

            # Symbol bestimmen, was geprintet werden soll
            if draw_x == current_player_pos_x and draw_y == current_player_pos_y:
                symbol = play
            else:
                symbol = grid[draw_y][draw_x]

            if symbol == spac:
                symbol = get_best_action(Q, ALL_ACTIONS, draw_pos)

            # Farbe basierend auf dem Symbol wählen
            if symbol == play:
                color = curses.color_pair(1)
            elif symbol == goal or symbol == star:
                color = curses.color_pair(2)
            elif symbol in ALL_ACTIONS:
                if Q[draw_pos][symbol] in start_values:
                    color = curses.color_pair(7)
                else:
                    color = curses.color_pair(5)
            elif symbol == bloc:
                color = curses.color_pair(3)
            elif symbol == waly or symbol == walx:
                color = curses.color_pair(4)
            else:
                color = curses.color_pair(4)
            stdscr.addstr(f" {symbol} ", color)

    stdscr.addstr(GRID_SIZE_Y, 0,
                  f"Episode: #{episode:05}  Action: {action}  Reward: {reward:.1f}  OldQ: {old_q:.5f}  NewQ: {new_q:.5f}")
    stdscr.refresh()

def clear_screen(stdscr):
    stdscr.clear()

# Q-Learning Algorithmus
def q_learning(stdscr, episodes=20000, alpha=0.2, gamma=0.9, epsilon=0.2):
    curses.curs_set(0)
    for e in range(episodes):
        current_player_pos = (2, 2)
        done = False
        step = 0
        while not done:
            action = choose_action(current_player_pos, Q, epsilon)
            new_player_pos = move(current_player_pos, action)
            reward = get_reward(new_player_pos)

            old_q = Q[current_player_pos][action]
            future_q = max(Q[new_player_pos].values())
            new_q = old_q + alpha * (reward + gamma * future_q - old_q)
            Q[current_player_pos][action] = new_q

            draw_grid(stdscr, current_player_pos, e, action, reward, old_q, new_q)

            current_player_pos = new_player_pos
            step += 1
            #time.sleep(1)

            if grid[new_player_pos[1]][new_player_pos[0]] in finish:
                done = True
    print_policy(stdscr)

def init_colors():
    curses.start_color()
    COLOR_GREY = curses.COLOR_WHITE + 1
    curses.init_color(COLOR_GREY, 200, 200, 200)
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)    # Rot auf Schwarz
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Grün auf Schwarz
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Weiß auf Schwarz
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Blau auf Schwarz
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Blau auf Schwarz
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Blau auf Schwarz
    curses.init_pair(7, COLOR_GREY, curses.COLOR_BLACK)   # Blau auf Schwarz

def main():
    stdscr = curses.initscr()
    init_colors()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        q_learning(stdscr)
    finally:
        stdscr.addstr(GRID_SIZE_Y + 2, 0, "Drücke eine Taste zum Beenden...")
        stdscr.refresh()
        stdscr.getch()
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

if __name__ == "__main__":
    main()
