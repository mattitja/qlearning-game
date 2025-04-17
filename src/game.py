import random
import os

grid = [
    ['A', ' ', ' ', ' ', ' ', ' '],
    [' ', 'o', 'o', ' ', 'o', ' '],
    [' ', ' ', ' ', ' ', ' ', ' '],
    ['o', ' ', ' ', 'o', 'o', 'o'],
    [' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', 'o', ' ', ' ', 'Z'],
]

Q = {}

GRID_SIZE = len(grid)

ALL_ACTIONS = ['L', 'R', 'U', 'D']

for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        Q[(x, y)] = {action: 0 for action in ALL_ACTIONS}

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
    elif grid[y][x] == 'o':
        return -10
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

def print_policy():
    for y in range(GRID_SIZE):
        row = ''
        for x in range(GRID_SIZE):
            current_position = (x, y)
            if grid[y][x] in ('A', 'Z', 'o'):
                letter = grid[y][x]
            else:
                letter = get_best_action(Q, get_allowed_actions(current_position), current_position)
            row += " " + letter + " "
        print(row)

def print_grid_with_current_pos(current_pos):
    current_x, current_y = current_pos
    for y in range(GRID_SIZE):
        row = ''
        for x in range(GRID_SIZE):
            if x == current_x and y == current_y:
                letter = 'O'
            else:
                letter = grid[y][x]
            row += " " + letter + " "
        print(row)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Q-Learning Algorithmus
def q_learning(episodes=15000, alpha=0.2, gamma=0.9, epsilon=0.2):
    for e in range(episodes):
        current_pos = (0, 0)
        done = False
        step = 0
        while not done:
            action = choose_action(current_pos, Q, epsilon)
            new_pos = move(current_pos, action)
            reward = get_reward(new_pos)

            # Q-Wert updaten
            old_q = Q[current_pos][action]
            future_q = max(Q[new_pos].values())
            new_q = old_q + alpha * (reward + gamma * future_q - old_q)
            Q[current_pos][action] = new_q
            clear_screen()
            print("#" + format(e+1, '05') + " #" + format(step, '03') + " ac: " + str(action)
                  + ", np: " + str(new_pos) + ", r: " + str(reward) + ", oldq: " + str(old_q) + ", newq: " + str(new_q))
            print_grid_with_current_pos(current_pos)

            current_pos = new_pos

            step += 1
            #sleep(0.001)
            if grid[new_pos[1]][new_pos[0]] in ('A', 'Z', 'o'):
                done = True

if __name__ == "__main__":
    q_learning()
    clear_screen()
    print_policy()
