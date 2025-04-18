import random
import curses

bloc = '#'
star = 'O'
play = '@'
spac = ' '
goal = 'X'
walx = '|'
waly = '='

walls = [bloc, walx, waly]

grid = [
    [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly],
    [walx, star, bloc, spac, bloc, bloc, bloc, bloc, bloc, spac, spac, spac, bloc, walx],
    [walx, spac, bloc, spac, spac, spac, spac, spac, spac, spac, bloc, spac, spac, walx],
    [walx, spac, bloc, spac, bloc, bloc, bloc, bloc, bloc, bloc, bloc, bloc, spac, walx],
    [walx, spac, bloc, spac, bloc, bloc, bloc, bloc, bloc, bloc, bloc, bloc, spac, walx],
    [walx, spac, bloc, spac, spac, spac, spac, spac, spac, spac, spac, bloc, spac, walx],
    [walx, spac, bloc, bloc, bloc, bloc, bloc, bloc, bloc, bloc, spac, bloc, spac, walx],
    [walx, spac, spac, spac, spac, spac, spac, spac, spac, spac, spac, bloc, goal, walx],
    [waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly, waly],
]

Q = {}

GRID_SIZE_Y = len(grid)
GRID_SIZE_X = len(grid[0])

left = '←'
right = '→'
top = '↑'
down = '↓'

ALL_ACTIONS = [left, right, top, down]

for x in range(GRID_SIZE_X):
    for y in range(GRID_SIZE_Y):
        Q[(x, y)] = {action: 0 for action in ALL_ACTIONS}

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

def draw_grid(stdscr, current_pos, episode, step, action, reward, old_q, new_q):
    stdscr.clear()
    current_x, current_y = current_pos
    for y in range(GRID_SIZE_Y):
        row = ''
        for x in range(GRID_SIZE_X):
            if x == current_x and y == current_y:
                letter = play
            else:
                letter = grid[y][x]
            row += " " + letter + " "
        stdscr.addstr(y, 0, row)
    stdscr.addstr(GRID_SIZE_Y, 0,
                  f"# {episode+1:05}  Step: {step:03}  Action: {action}  Reward: {reward:.1f}  OldQ: {old_q:.2f}  NewQ: {new_q:.2f}")
    stdscr.refresh()

def clear_screen(stdscr):
    stdscr.clear()

# Q-Learning Algorithmus
def q_learning(stdscr, episodes=10000, alpha=0.2, gamma=0.9, epsilon=0.1):
    curses.curs_set(0)
    for e in range(episodes):
        current_pos = (1, 1)
        done = False
        step = 0
        while not done:
            action = choose_action(current_pos, Q, epsilon)
            new_pos = move(current_pos, action)
            reward = get_reward(new_pos)

            old_q = Q[current_pos][action]
            future_q = max(Q[new_pos].values())
            new_q = old_q + alpha * (reward + gamma * future_q - old_q)
            Q[current_pos][action] = new_q

            draw_grid(stdscr, current_pos, e, step, action, reward, old_q, new_q)

            current_pos = new_pos
            step += 1

            if grid[new_pos[1]][new_pos[0]] in (star, goal, *walls):
                done = True
    print_policy(stdscr)

def main():
    stdscr = curses.initscr()
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
