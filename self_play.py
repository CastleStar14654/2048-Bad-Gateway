'''code template of Player
'''

import numpy as np
import random
POSITION_MODE = 'position'
DIRECTION_MODE = 'direction'


class Player:
    def __init__(self, isFirst: bool, array: list) -> None:
        self._isFirst = isFirst
        self._array = array

    def output(self, currentRound: int, board, mode: str):
        if self._isFirst:
            return self._output_first(currentRound, board, mode)
        else:
            return self._output_second(currentRound, board, mode)

    def _output_first(self, currentRound: int, board, mode: str):
        '''if mode=='position', return (row, col)
        else if mode=='direction', return int (0, 1, 2, 3 are U, D, L, R)
        '''
        if mode == POSITION_MODE:
            return self._output_first_pos(currentRound, board)
        elif mode == DIRECTION_MODE:
            return self._output_first_dir(currentRound, board)
        else:
            pass

    def _output_second(self, currentRound: int, board, mode: str):
        '''if mode=='position', return (row, col)
        else if mode=='direction', return int (0, 1, 2, 3 are U, D, L, R)
        '''
        if mode == POSITION_MODE:
            return self._output_second_pos(currentRound, board)
        elif mode == DIRECTION_MODE:
            return self._output_second_dir(currentRound, board)
        else:
            pass

    def _output_first_pos(self, currentRound: int, board) -> tuple:
        '''return (row, col)
        '''
        next_pos = board.getNext(self._isFirst, currentRound)
        if next_pos:
            return next_pos
        else:
            return random.choice(board.getNone(not self._isFirst))

    def _output_first_dir(self, currentRound: int, board) -> int:
        '''return int (0, 1, 2, 3 are U, D, L, R)
        '''
        if currentRound == 0 and (
            board.getValue((0, 3)) or board.getValue((3, 3))
        ):
            return 2
        # 右移是否危险
        for row in range(4):
            current = board.getValue((row, 3))
            if current and current == board.getValue((row, 4)) \
                    and board.getBelong((row, 4)) == self._isFirst:
                circumstances = [(row, 5)]
                if row > 0:
                    circumstances.append((row-1, 4))
                if row < 3:
                    circumstances.append((row+1, 4))
                for pos in circumstances:
                    if board.getValue(pos) == current + 1 \
                            and board.getBelong(pos) != self._isFirst:
                        break
                else:
                    return 3
        # 搜索三个方案
        max_dir = None
        max_value = -1000
        dict_anchor = {0: ('ne',), 1: ('se',), 3: ('ne', 'se')}
        possible_moves = []
        for direction in dict_anchor:
            board_copy = board.copy()
            if board_copy.move(self._isFirst, direction):
                possible_moves.append(direction)
                for anchor in dict_anchor[direction]:
                    new_value = self.board_estimate(
                        board_copy, self._isFirst, anchor)
                    if new_value > max_value:
                        max_value = new_value
                        max_dir = direction
        # 搜索出来发现不能动
        if max_dir != None:
            return max_dir
        else:
            return possible_moves[0] if possible_moves else 2

    def _output_second_pos(self, currentRound: int, board) -> tuple:
        '''return (row, col)
        '''
        next_pos = board.getNext(self._isFirst, currentRound)
        if next_pos:
            return next_pos
        else:
            return random.choice(board.getNone(not self._isFirst))

    def _output_second_dir(self, currentRound: int, board) -> int:
        '''return int (0, 1, 2, 3 are U, D, L, R)
        '''
        # 左移是否危险
        for row in range(4):
            current = board.getValue((row, 4))
            if current and current == board.getValue((row, 3)) \
                    and board.getBelong((row, 3)) == self._isFirst:
                circumstances = [(row, 2)]
                if row > 0:
                    circumstances.append((row-1, 3))
                if row < 3:
                    circumstances.append((row+1, 3))
                for pos in circumstances:
                    if board.getValue(pos) == current + 1 \
                            and board.getBelong(pos) != self._isFirst:
                        break
                else:
                    return 2
        # 搜索三个方案
        max_dir = None
        max_value = -1000
        dict_anchor = {0: ('nw',), 1: ('sw',), 2: ('nw', 'sw')}
        possible_moves = []
        for direction in dict_anchor:
            board_copy = board.copy()
            if board_copy.move(self._isFirst, direction):
                possible_moves.append(direction)
                for anchor in dict_anchor[direction]:
                    new_value = self.board_estimate(
                        board_copy, self._isFirst, anchor)
                    if new_value > max_value:
                        max_value = new_value
                        max_dir = direction
        # 搜索出来发现不能动
        if max_dir != None:
            return max_dir
        else:
            return possible_moves[0] if possible_moves else 3

    templates = {
        'nw': [
            [16, 14, 11, 8],
            [14, 12, 10, 5],
            [11, 10, 8, 3],
            [8, 5, 3, 1]
        ],
        'ne': [
            [8, 11, 14, 16],
            [5, 10, 12, 14],
            [3, 8, 10, 11],
            [1, 3, 5, 8]
        ],
        'sw': [
            [8, 5, 3, 1],
            [11, 10, 8, 3],
            [14, 12, 10, 5],
            [16, 14, 11, 8]
        ],
        'se': [
            [1, 3, 5, 8],
            [3, 8, 10, 11],
            [5, 10, 12, 14],
            [8, 11, 14, 16]
        ]
    }

    def board_estimate(self, board, belong, anchor) -> int:
        '''anchor: 'nw', 'ne', 'sw', 'se'
        '''
        tp = self.templates[anchor]
        res = 0
        for col_b, col_t in zip(range(4) if belong else range(4, 8), range(4)):
            for row in range(4):
                res += (2 * board.getBelong((row, col_b)) - 1) \
                    * board.getValue((row, col_b)) \
                    * tp[row][col_t]
        if not belong:
            res *= -1

        enemy_col = 4 if belong else 3
        for row in range(4):
            if board.getBelong((row, enemy_col)) == belong:
                res += board.getValue((row, enemy_col)) * 10
            else:
                res -= board.getValue((row, enemy_col)) * 3

        return res
