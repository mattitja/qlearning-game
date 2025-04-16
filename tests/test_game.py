from src.game import move, GRID_SIZE, ALL_ACTIONS
from src.game import get_reward
from src.game import get_allowed_actions
from src.game import get_best_action
from src.game import choose_action
from src.game import GRID_SIZE

M = 0 #min
G = GRID_SIZE-1 #grid_six max

def test_move():
    assert move((M, M), 'D') == (M, M+1)
    assert move((M, M), 'U') == (M, M)
    assert move((M, M), 'L') == (M, M)
    assert move((M, M), 'R') == (M+1, M)
    assert move((G, G), 'D') == (G, G)
    assert move((G, G), 'U') == (G, G-1)
    assert move((G, G), 'L') == (G-1, G)
    assert move((G, G), 'R') == (G, G)
    assert move((M, G), 'D') == (M, G)
    assert move((M, G), 'U') == (M, G-1)
    assert move((M, G), 'L') == (M, G)
    assert move((M, G), 'R') == (M+1, G)
    assert move((G, M), 'D') == (G, M+1)
    assert move((G, M), 'U') == (G, M)
    assert move((G, M), 'L') == (G-1, M)
    assert move((G, M), 'R') == (G, M)

def test_get_reward():
    assert get_reward((M,M)) == -1.0
    assert get_reward((G,G)) == 100
    assert get_reward((1,1)) == -0.1

def test_get_allowed_actions():
    assert get_allowed_actions((M, M)) == ['R', 'D']
    assert get_allowed_actions((M + 1, M + 1)) == ALL_ACTIONS

def test_get_best_action():
    current_position = (0, 0)
    q = {current_position: {'L': 1, 'R': 2, 'U': 3, 'D': 4}}
    assert get_best_action(q, ['L'], current_position) == 'L'
    assert get_best_action(q, ['L', 'D'], current_position) == 'D'

def test_get_best_action_but_there_are_more(monkeypatch):
    current_position = (0, 0)
    q = {current_position: {'L': 1, 'R': 1, 'U': 1, 'D': 1}}
    assert get_best_action(q, ['L'], current_position) == 'L'
    monkeypatch.setattr('random.choice', lambda p: p[0])
    assert get_best_action(q, ['L', 'D'], current_position) == 'L'

def test_choose_action_random(monkeypatch):
    current_position = (0, 0)
    q = {current_position: {'L': 1, 'R': 2, 'U': 3, 'D': 4}}
    monkeypatch.setattr('src.game.get_allowed_actions', lambda p: ['L'])
    monkeypatch.setattr('random.random', lambda: 0.00)
    assert choose_action(current_position, q) == 'L'

def test_choose_action_best(monkeypatch):
    current_position = (0, 0)
    q = {current_position: {'L': 1, 'R': 2, 'U': 3, 'D': 4}}
    monkeypatch.setattr('src.game.get_allowed_actions', lambda p: ['L', 'R'])
    monkeypatch.setattr('src.game.get_best_action', lambda x, y, z: 'R')
    monkeypatch.setattr('random.random', lambda: 1)
    assert choose_action(current_position, q) == 'R'
