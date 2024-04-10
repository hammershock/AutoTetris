import glob
import sys
import warnings
import random
from enum import Enum, auto

import numpy as np


def rotate(shape, orient: int):
    for x, y in shape:
        result = {0: (x, y), 1: (y, -x), 2: (-x, -y), 3: (-y, x)}
        yield result[orient]


# 实例化方块
shapes_ = {1: [(0, -1), (0, 0), (0, 1), (0, 2)],
           2: [(0, -1), (0, 0), (0, 1), (-1, 1)],
           3: [(0, -1), (0, 0), (0, 1), (1, 1)],
           4: [(0, 0), (0, 1), (1, 0), (1, 1)],
           5: [(1, 0), (0, 0), (0, 1), (-1, 1)],
           6: [(-1, 0), (0, 0), (1, 0), (0, 1)],
           7: [(-1, 0), (0, 0), (0, 1), (1, 1)]}

shapes = {(val, orient): tuple(rotate(shapes_[val], orient)) for val in shapes_.keys() for orient in range(4)}

cache = {}


class Mode(Enum):
    very_easy = auto()
    easy = auto()
    medium = auto()
    hard = auto()
    extreme = auto()
    
    
class State:
    def __init__(self, board, landing_height=0):
        self.board: np.ndarray = board.copy()
        self.h, self.w = self.board.shape
        
        self.landing_height = landing_height
        self.rows_eliminated = 0
    
    def is_over(self):
        return np.any(self.board[0] > 0)
    
    def next_states(self, val: int):
        orient_end = 1 if val == 4 else (2 if val in [1, 5, 7] else 4)
        
        for orient in range(orient_end):
            shape = np.array(shapes[(val, orient)])
            x_min, y_min = np.min(shape, axis=0)
            x_max, y_max = np.max(shape, axis=0)
            
            for x0 in range(-x_min, self.w - x_max):
                land_y = -1
                for y0 in range(-y_min, self.h - 1):
                    for dx, dy in shape:
                        x, y = x0 + dx, y0 + dy
                        next_y = y + 1
                        if next_y >= self.h or self.board[next_y, x] > 0:
                            land_y = y0
                            break
                    if land_y > 0:
                        break
                if land_y < 0:
                    continue
                
                layers = []
                next_state = self.board.copy()
                for dx, dy in shape:
                    x, y = x0 + dx, land_y + dy
                    if y in range(self.h):
                        next_state[y, x] = val
                    layers.append(y)
                state = State(next_state, self.h - land_y)
                state.check_line_clear(layers)
                yield orient, x0, state
    
    def score(self) -> float:
        return (- 4.500158825082766 * self.landing_height
                + 3.4181268101392694 * self.rows_eliminated
                - 3.2178882868487753 * self.row_transitions()
                - 9.348695305445199 * self.column_transitions()
                - 7.899265427351652 * self.holes()
                - 3.3855972247263626 * self.well_sum())
    
    def best2_c(self, val1, val2):
        sys.path.append('./cpp/build')
        import Tetris
        state = Tetris.State(self.board.astype(int).tolist())
        orient, x0 = state.best2(val1, val2)
        return orient, x0
    
    def best1_c(self, val):
        sys.path.append('./cpp/build')
        import Tetris
        state = Tetris.State(self.board.astype(int).tolist())
        orient, x0 = state.best1(val)
        return orient, x0
        
    def best1(self, val, accelerate=False):
        if accelerate:
            try:
                if len(glob.glob(f'cpp/build/*.so')):
                    orient, x0 = self.best1_c(val)
                    
                    return orient, x0
                else:
                    warnings.warn('cpp extension not found, please run build.sh to build it first!')
            except ImportError as e:
                warnings.warn(f'failed to load c extensions, {e}')
                pass
            
        orient, x0, _ = max((x for x in self.next_states(val)), key=lambda x: x[-1].score())
        return orient, x0
    
    def best2(self, val1, val2, accelerate=False):
        if accelerate:
            try:
                if len(glob.glob(f'cpp/build/*.so')):
                    orient, x0 = self.best2_c(val1, val2)
                    
                    return orient, x0
                else:
                    warnings.warn('cpp extension not found, please run build.sh to build it first!')
            except ImportError as e:
                warnings.warn(f'failed to load c extensions, {e}')
                pass
        
        best_score = - float('inf')
        best_orient = None
        best_x0 = None
        for orient, x0, state in self.next_states(val1):
            for _, _, state2 in state.next_states(val2):
                score = state2.score() + state.score()
                if score > best_score:
                    best_score = score
                    best_orient = orient
                    best_x0 = x0
        return best_orient, best_x0
    
    def worst_block1_c(self):
        sys.path.append('./cpp/build')
        import Tetris
        state = Tetris.State(self.board.astype(int).tolist())
        val = state.worst_block1()
        return val
    
    def worst_block2_c(self, val):
        sys.path.append('./cpp/build')
        import Tetris
        state = Tetris.State(self.board.astype(int).tolist())
        val2 = state.worst_block2(val)
        return val2
    
    def easiest_block1_c(self):
        sys.path.append('./cpp/build')
        import Tetris
        state = Tetris.State(self.board.astype(int).tolist())
        val = state.easiest_block1()
        return val
    
    def easiest_block2_c(self, val):
        sys.path.append('./cpp/build')
        import Tetris
        state = Tetris.State(self.board.astype(int).tolist())
        val2 = state.easiest_block2(val)
        return val2
        
    def worst_block2(self, val, accelerate=False):
        if accelerate:
            try:
                if len(glob.glob(f'cpp/build/*.so')):
                    val2 = self.worst_block2_c(val)
                    return val2
                else:
                    warnings.warn('cpp extension not found, please run build.sh to build it first!')
            except ImportError as e:
                warnings.warn(f'failed to load c extensions, {e}')
                pass
        
        raise NotImplementedError('Only supports C++ version')
    
    def check_line_clear(self, layers):
        new_grid = []
        lines_cleared = 0
        cleard_rows = []
        for i, row in enumerate(self.board):
            if np.all(row > 0):
                lines_cleared += 1
                cleard_rows.append(i)
            else:
                new_grid.append(row)
        
        for _ in range(lines_cleared):
            new_grid.insert(0, np.zeros(self.w))
        
        cnt = 0
        for layer in layers:
            if layer in cleard_rows:
                cnt += 1
        
        self.board = np.array(new_grid)  # 更新网格为新网格
        self.rows_eliminated = lines_cleared * cnt
    
    def row_transitions(self):
        transitions_cnt = 0
        for row in self.board:
            transitions_cnt += np.sum(np.abs(np.diff(np.array([1, *row, 1]) > 0)))
        return transitions_cnt
    
    def column_transitions(self):
        transitions_cnt = 0
        for row in self.board.T:
            transitions_cnt += np.sum(np.abs(np.diff(np.array([1, *row, 1]) > 0)))
        return transitions_cnt
    
    def holes(self):
        holes = 0
        
        for x in range(self.w):
            column = self.board[:, x]
            flag = False
            
            for v in column:
                if v > 0:
                    flag = True
                if flag and v == 0:
                    holes += 1
                    flag = False
        
        return holes
    
    def well_sum(self):
        sum = 0
        for j in range(self.w):
            cnt = 0
            for i in range(self.h):
                left = self.board[i, j - 1] if j - 1 >= 0 else 1
                right = self.board[i, j + 1] if j + 1 < self.w else 1
                mid = self.board[i, j]
                if left > 0 and right > 0 and mid == 0:
                    cnt += 1
                else:
                    sum += cnt * (cnt + 1) / 2
                    cnt = 0
        return sum


class PyTris:
    def __init__(self, w=10, h=20, autoplay=False, turbo=False, mode=Mode.medium, p=0.5):
        """
        
        :param w:
        :param h:
        :param autoplay:
        :param turbo:
        :param mode: 难度模式：
        :param p: 难度(0-1)
        难度说明：
        Mode.very_easy: 前方块以概率1-p出现最有利于玩家的那一个
        Mode.easy: 下一个方块以概率1-p出现最有利于玩家的那一个
        Mode.medium: 下一个方块完全随机出现
        Mode.hard: 下一个方块以概率p出现最不利于玩家的那一个
        Mode.extreme: 禁用下一个方块提示，且当前方块以概率p出现最不利于玩家的那一个
        """
        self.val = random.choice(list(shapes_.keys()))
        self.next = random.choice(list(shapes.keys()))
        
        self.w = w
        self.h = h
        self.autoplay = autoplay
        self.turbo = turbo
        self.mode = mode
        self.p = p
        
        self.state = State(np.zeros((h, w)))
        self.view = np.zeros_like(self.state.board)  # 实际显示时绘制的视图
        
        self.orient = 0
        
        self.pos_x, self.pos_y = 0, 0
        
        self.score = 0
        self.game_over = False

    def start_game(self):
        self.game_over = False
        self.score = 0
        self.state = State(np.zeros((self.h, self.w)))
        self.view = np.zeros_like(self.state.board)
        
        # 游戏开始时生成第一个方块
        self.spawn_piece()
    
    def spawn_piece(self):
        next_orient = random.randint(0, 3)
        
        if self.mode == Mode.extreme:
            self.next = None
            self.val = self.state.worst_block1_c() if random.random() < self.p else random.randint(1, 7)
            self.orient = np.random.randint(0, 3)
        elif self.mode == Mode.hard:
            next = (self.state.worst_block2_c(self.val), next_orient) if random.random() < self.p else random.choice(list(shapes.keys()))
            (self.val, self.orient), self.next = self.next, next
        elif self.mode == Mode.easy:
            next = (self.state.easiest_block2_c(self.val), next_orient) if random.random() > self.p else random.choice(list(shapes.keys()))
            (self.val, self.orient), self.next = self.next, next
        elif self.mode == Mode.very_easy:
            self.next = None
            self.val = self.state.easiest_block1_c()
            self.orient = np.random.randint(0, 3)
        else:  # medium
            next = random.choice(list(shapes.keys()))
            (self.val, self.orient), self.next = self.next, next
        
        shape = np.array(shapes[(self.val, self.orient)])
        
        x_max, y_max = np.max(shape, axis=0)  # x横向, y纵向
        x_min, y_min = np.min(shape, axis=0)
        
        self.pos_y = - y_min
        self.pos_x = random.randint(-x_min, self.w - 1 - x_max)
        
        if self.autoplay:
            if self.next is None:
                self.orient, self.pos_x = self.state.best1(self.val, accelerate=self.turbo)
            else:
                self.orient, self.pos_x = self.state.best2(self.val, self.next[0], accelerate=self.turbo)

        self.view = self.state.board.copy()  # 更新视图
        
        for dx, dy in shapes[(self.val, self.orient)]:
            if self.pos_y + dy in range(self.h):
                self.view[self.pos_y + dy, self.pos_x + dx] = self.val
            
    def rotate_piece(self):
        new_orient = 0
        if self.val != 4:
            if self.val in [2, 3, 6]:
                new_orient = (self.orient + 1) % 4
            else:
                new_orient = (self.orient + 1) % 2

        new_view = self.state.board.copy()

        for dx, dy in shapes[(self.val, new_orient)]:
            x, y = self.pos_x + dx, self.pos_y + dy
            if x < 0 or x >= self.w or y < 0 or y >= self.h or self.state.board[y, x] > 0:
                return  # 无法转动
            else:
                new_view[y, x] = self.val
                
        self.view = new_view
        self.orient = new_orient
        
    def move_piece(self, dir_x, dir_y):
        if self.game_over:
            return
        
        new_view = self.state.board.copy()
        new_x, new_y = self.pos_x + dir_x, self.pos_y + dir_y
        
        for dx, dy in shapes[(self.val, self.orient)]:
            x, y = new_x + dx, new_y + dy
            
            if x < 0 or x >= self.w or y < 0 or y >= self.h or self.state.board[y, x] > 0:
                if (dir_x, dir_y) == (0, 1):  # 成功触底
                    self.state.board = self.view.copy()
                    self.score += self.check_line_clear()  # 更新得分
                    self.game_over = self.state.is_over()  # 判断胜负
                    if not self.game_over:
                        self.spawn_piece()  # 生成新块
                return False
            
            new_view[y, x] = self.val
            
        self.pos_x += dir_x
        self.pos_y += dir_y
        self.view = new_view
        return True
    
    def drop(self):
        while self.move_piece(0, 1):
            pass

    def check_line_clear(self):
        new_grid = []
        lines_cleared = 0
        
        for row in self.state.board:
            if np.all(row > 0):
                lines_cleared += 1
            else:
                new_grid.append(row)
        
        for _ in range(lines_cleared):
            new_grid.insert(0, np.zeros(self.w))
        
        self.state.board = np.array(new_grid)  # 更新网格为新网格
        return lines_cleared  # 返回消除的行数，可用于计分或其他逻辑
