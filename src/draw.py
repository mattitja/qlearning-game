# color pairs
import curses
from game import BLOCK
from game import START
from game import PLAYR
from game import SPACE
from game import GOALL
from game import TRESR
from game import WALLX
from game import WALLY
from game import START_VALUES
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

def init_heatmap(grid_size_x, grid_size_y):
    heatmap = [[0 for _ in range(grid_size_x)] for _ in range(grid_size_y)]
    return heatmap


def draw_grid(screen, current_player_pos, episode, action, reward, old_q, new_q, step, player_dead, speed, grid_size_x, grid_size_y, grid, q, heatmap):
    screen.clear()
    current_player_pos_x, current_player_pos_y = current_player_pos
    for draw_y in range(grid_size_y):
        for draw_x in range(grid_size_x):
            # Position des Cursors setzen
            draw_one_grid_slot(current_player_pos_x, current_player_pos_y, draw_x, draw_y, player_dead, screen, grid, q, heatmap)

    draw_statistics(action, episode, new_q, old_q, player_dead, reward, speed, screen, step, grid_size_y)
    screen.refresh()


def draw_one_grid_slot(current_player_pos_x, current_player_pos_y, draw_x, draw_y, player_dead, screen, grid, q, heatmap):
    draw_pos = (draw_x, draw_y)
    screen.move(draw_y, draw_x * 3)  # Jedes Symbol ist 3 Zeichen breit (z. B. " X ")

    symbol = determine_symbol(current_player_pos_x, current_player_pos_y, draw_pos, grid, q)
    color = determine_symbol_color(draw_pos, player_dead, symbol, q, heatmap)
    screen.addstr(f" {symbol} ", color)


def determine_symbol_color(draw_pos, player_dead, symbol, q, heatmap):
    if symbol == PLAYR:
        if player_dead:
            color = curses.color_pair(RED_ON_BLACK)
        else:
            color = curses.color_pair(WHITE_ON_BLACK)
    elif symbol == GOALL or symbol == START:
        color = curses.color_pair(YELLOW_ON_BLACK)
    elif symbol in ALL_ACTIONS:
        if q[draw_pos][symbol] in START_VALUES:
            color = curses.color_pair(GREY_ON_BLACK)
        else:
            color = get_color_heatmap(draw_pos, heatmap)
    elif symbol == BLOCK or symbol == WALLY or symbol == WALLX:
        color = curses.color_pair(WHITE_ON_BLACK)
    else:
        color = curses.color_pair(LIGHT_GREY_ON_BLACK)
    return color


def determine_symbol(current_player_pos_x, current_player_pos_y, draw_pos, grid, q):
    if draw_pos[0] == current_player_pos_x and draw_pos[1] == current_player_pos_y:
        symbol = PLAYR
    else:
        symbol = get_symbol(draw_pos, grid)
    if symbol == SPACE:
        symbol = get_best_action(q, ALL_ACTIONS, draw_pos)
    return symbol


def draw_statistics(action, episode, new_q, old_q, player_dead, reward, speed, screen, step, grid_size_y):
    line_number = grid_size_y
    line_number += 1
    screen.addstr(line_number, 0, "")
    line_number += 1
    screen.addstr(line_number, 0, "Speed: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{speed:.0f}x", curses.color_pair(WHITE_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "")
    line_number += 1
    screen.addstr(line_number, 0, "Current Step: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"#{step:03} ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "Current Episode: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"#{episode:05} ",
                  curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "Last Action: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{action}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "Last Reward: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{reward:.1f}  ",
                  curses.color_pair(RED_ON_BLACK) if player_dead else curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "")
    line_number += 1
    screen.addstr(line_number, 0, "Old Q: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{old_q:.5f}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "New Q: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{new_q:.5f}", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "")
    line_number += 1
    screen.addstr(line_number, 0, "Total steps: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{step_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, f"Total {BLOCK}: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{wall_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, f"Total {TRESR}: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{tres_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, f"Total {GOALL}: ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{goal_counter:.0f}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "")
    line_number += 1
    screen.addstr(line_number, 0, "Epsilon (Explorationsrate): ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{EPSILON:.2f}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "Alpha (Lernrate): ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{ALPHA:.2f}  ", curses.color_pair(GREY_ON_BLACK))
    line_number += 1
    screen.addstr(line_number, 0, "Gamma (Langfristigkeit): ", curses.color_pair(WHITE_ON_BLACK))
    screen.addstr(f"{GAMMA:.2f}  ", curses.color_pair(GREY_ON_BLACK))


def get_heatmap_max(heatmap):
    return max(max(row) for row in heatmap)


def get_bg_color_ratio(current_position, heatmap):
    x, y = current_position
    current_value = heatmap[y][x]
    max_value = get_heatmap_max(heatmap)
    return current_value / max_value


def get_color_heatmap(current_position, heatmap):
    ratio = get_bg_color_ratio(current_position, heatmap)
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


def clear_screen(screen):
    screen.clear()

def update_heatmap(e, new_player_pos, heatmap):
    new_x, new_y = new_player_pos
    heatmap[new_y][new_x] += 0.00001 * (e ** 3)
    return heatmap

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

def init_draw():
    screen = curses.initscr()
    init_colors(curses)
    curses.curs_set(0)

    # curses.curs_set(0)
    screen.clear()

    curses.noecho()
    curses.cbreak()
    screen.keypad(True)
    screen.nodelay(True)
    return screen

def finish_draw(screen, grid_size_y):
    screen.addstr(grid_size_y + 2, 0, "Drücke eine Taste zum Beenden...")
    screen.refresh()
    screen.nodelay(False)
    screen.getch()
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()