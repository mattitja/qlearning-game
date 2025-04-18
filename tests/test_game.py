from src.game import move, GRID_SIZE, ALL_ACTIONS
from src.game import get_reward
from src.game import get_allowed_actions
from src.game import get_best_action
from src.game import choose_action
from src.game import GRID_SIZE

M = 0 #min
G = GRID_SIZE-1 #grid_six max

def test_move():
    assert move((M, M), '↓') == (M, M+1)
    assert move((M, M), '↑') == (M, M)
    assert move((M, M), '←') == (M, M)
    assert move((M, M), '→') == (M+1, M)
    assert move((G, G), '↓') == (G, G)
    assert move((G, G), '↑') == (G, G-1)
    assert move((G, G), '←') == (G-1, G)
    assert move((G, G), '→') == (G, G)
    assert move((M, G), '↓') == (M, G)
    assert move((M, G), '↑') == (M, G-1)
    assert move((M, G), '←') == (M, G)
    assert move((M, G), '→') == (M+1, G)
    assert move((G, M), '↓') == (G, M+1)
    assert move((G, M), '↑') == (G, M)
    assert move((G, M), '←') == (G-1, M)
    assert move((G, M), '→') == (G, M)

def test_get_reward():
    assert get_reward((M,M)) == -1.0
    assert get_reward((G,G)) == 100
    assert get_reward((1,1)) == -0.1

def test_get_allowed_actions():
    assert get_allowed_actions((M, M)) == ['→', '↓']
    assert get_allowed_actions((M + 1, M + 1)) == ALL_ACTIONS

def test_get_best_action():
    current_position = (0, 0)
    q = {current_position: {'←': 1, '→': 2, '↑': 3, '↓': 4}}
    assert get_best_action(q, ['←'], current_position) == '←'
    assert get_best_action(q, ['←', '↓'], current_position) == '↓'

def test_get_best_action_but_there_are_more(monkeypatch):
    current_position = (0, 0)
    q = {current_position: {'←': 1, '→': 1, '↑': 1, '↓': 1}}
    assert get_best_action(q, ['←'], current_position) == '←'
    monkeypatch.setattr('random.choice', lambda p: p[0])
    assert get_best_action(q, ['←', '↓'], current_position) == '←'

def test_choose_action_random(monkeypatch):
    current_position = (0, 0)
    q = {current_position: {'←': 1, '→': 2, '↑': 3, '↓': 4}}
    monkeypatch.setattr('src.game.get_allowed_actions', lambda p: ['←'])
    monkeypatch.setattr('random.random', lambda: 0.00)
    assert choose_action(current_position, q) == '←'

def test_choose_action_best(monkeypatch):
    current_position = (0, 0)
    q = {current_position: {'←': 1, '→': 2, '↑': 3, '↓': 4}}
    monkeypatch.setattr('src.game.get_allowed_actions', lambda p: ['←', '→'])
    monkeypatch.setattr('src.game.get_best_action', lambda x, y, z: '→')
    monkeypatch.setattr('random.random', lambda: 1)
    assert choose_action(current_position, q, 0.1) == '→'
