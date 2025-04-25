# color pairs
import curses
from game import bloc
from game import star
from game import play
from game import spac
from game import goal
from game import tres
from game import walx
from game import waly
from game import start_values
from game import ALL_ACTIONS
from game import get_symbol
from game import get_best_action
from game import tres_counter
from game import wall_counter
from game import goal_counter
from game import step_counter
from game import EPSILON
from game import GAMMA
from game import ALPHA

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

heatmap = {}

def init_heatmap(GRID_SIZE_X, GRID_SIZE_Y):
    global heatmap
    heatmap = [[0 for _ in range(GRID_SIZE_X)] for _ in range(GRID_SIZE_Y)]


def draw_grid(stdscr, current_player_pos, episode, action, reward, old_q, new_q, step, player_dead, speed, GRID_SIZE_X, GRID_SIZE_Y, grid, Q):
    stdscr.clear()
    current_player_pos_x, current_player_pos_y = current_player_pos
    for draw_y in range(GRID_SIZE_Y):
        for draw_x in range(GRID_SIZE_X):
            # Position des Cursors setzen
            draw_one_grid_slot(current_player_pos_x, current_player_pos_y, draw_x, draw_y, player_dead, stdscr, grid, Q)

    draw_statistics(action, episode, new_q, old_q, player_dead, reward, speed, stdscr, step, GRID_SIZE_X, GRID_SIZE_Y)
    stdscr.refresh()


def draw_one_grid_slot(current_player_pos_x, current_player_pos_y, draw_x, draw_y, player_dead, stdscr, grid, Q):
    draw_pos = (draw_x, draw_y)
    stdscr.move(draw_y, draw_x * 3)  # Jedes Symbol ist 3 Zeichen breit (z. B. " X ")

    symbol = determine_symbol(current_player_pos_x, current_player_pos_y, draw_pos, grid, Q)
    color = determine_symbol_color(draw_pos, player_dead, symbol, Q)
    stdscr.addstr(f" {symbol} ", color)


def determine_symbol_color(draw_pos, player_dead, symbol, Q):
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


def determine_symbol(current_player_pos_x, current_player_pos_y, draw_pos, grid, Q):
    if draw_pos[0] == current_player_pos_x and draw_pos[1] == current_player_pos_y:
        symbol = play
    else:
        symbol = get_symbol(draw_pos, grid)
    if symbol == spac:
        symbol = get_best_action(Q, ALL_ACTIONS, draw_pos)
    return symbol


def draw_statistics(action, episode, new_q, old_q, player_dead, reward, speed, stdscr, step, GRID_SIZE_X, GRID_SIZE_Y):
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

def update_heatmap(e, new_player_pos):
    new_x, new_y = new_player_pos
    heatmap[new_y][new_x] += 0.00001 * (e ** 3)

def init_colors(curses):
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

def init_draw(GRID_SIZE_X, GRID_SIZE_Y):
    init_heatmap(GRID_SIZE_X, GRID_SIZE_Y)
    stdscr = curses.initscr()
    init_colors(curses)

    # curses.curs_set(0)
    stdscr.clear()

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    return stdscr

def finish_draw(stdscr, GRID_SIZE_X, GRID_SIZE_Y):
    stdscr.addstr(GRID_SIZE_Y + 2, 0, "Drücke eine Taste zum Beenden...")
    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()