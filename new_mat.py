'''ref: https://github.com/nneonneo/2048-ai/
'''

import numpy as np
import random
import collections

POSITION_MODE = 'position'
DIRECTION_MODE = 'direction'

SCORE_MONOTONICITY_POWER = 4.0
SCORE_MONOTONICITY_WEIGHT = 300
SCORE_SUM_POWER = 3.5
SCORE_SUM_WEIGHT = 300
SCORE_MERGES_WEIGHT = 300.0
SCORE_EMPTY_WEIGHT = 300.0


class Player:
    class Chess:
        def __init__(self, belong, value):
            self.belong = belong
            self.value = value

        def __eq__(self, other):
            return self.eq_belong(other) and self.eq_val(other)

        def eq_val(self, other):
            return self.value == other.value

        def eq_belong(self, other):
            return self.belong == self.belong

    class Tree_Node:
        def __init__(self, currentRound, board=None):
            self.round = currentRound
            self.board = board
            self.tree = {}
            self.depth = 0

        def __len__(self):
            return len(self.tree)

        def __getitem__(self, key):
            return self.tree[key]

        def __contains__(self, item):
            return item in self.tree

        def __bool__(self):
            return bool(self.tree)

        def search(self, mode: str, isFirst: bool, one_layer: bool) -> None:
            '''search and deepen the tree
            starting from `self.board`, player `isFirst`, playing the `mode` ('position' or 'direction')
            `one_layer`:
                if `True`, search for 1 layer
                if `False`, search for at least 2 layers, and then search till the end of the round
            '''
            if mode == POSITION_MODE:
                board_copy = self.board.copy()
                random_next = board_copy.getNext(isFirst, )


        def evaluate(self) -> dict:
            '''evaluate current situation
            return: dict[bool: int]
                dict[isFirst] == evaluation of isFirst
            calculating:
                monotonicity
                mergeable next time
                sum of chess
            '''
            res = {True: 0, False: 0}
            # horizontal
            for row in range(4):
                sub_res = self.evaluate_row(row)
                res[True] += sub_res[True]
                res[False] += sub_res[False]

            # vertical
            for col in range(4):
                sub_res = self.evaluate_col(col, True)
                res[True] += sub_res[True]
                res[False] += sub_res[False]
            for col in range(4, 8):
                sub_res = self.evaluate_col(col, False)
                res[True] += sub_res[True]
                res[False] += sub_res[False]

            return res

        def evaluate_row(self, row: int) -> dict:
            res = {True: 0, False: 0}
            monotonicity_Lr = {True: 0, False: 0}
            monotonicity_lR = {True: 0, False: 0}
            merge = {True: 0, False: 0}
            summation = {True: 0, False: 0}
            empty = {True: 0, False: 0}

            prev = None
            for belong, ra in zip((False, True), (range(4), range(4, 8))):
                for col in ra:
                    current = Player.Chess(self.board.getBelong((row, col)),
                                           self.board.getValue((row, col)))
                    if current.value:
                        summation[current.belong] += current.value ** SCORE_SUM_POWER
                        if prev:
                            if current.eq_val(prev):
                                merge[current.belong] += .5 * current.value
                                merge[prev.belong] += .5 * current.value
                                if col == 4 and current.belong == belong and prev.belong != belong:
                                    merge[current.belong] -= 1.5 * \
                                        current.value
                            elif col != 4 and current.belong != belong:
                                mono = current.value ** SCORE_MONOTONICITY_POWER
                                monotonicity_lR[not belong] += mono
                                monotonicity_Lr[not belong] += mono
                                monotonicity_lR[belong] -= mono
                                monotonicity_Lr[belong] -= mono
                        prev = current
                    else:
                        empty[belong] += 1

            for key in res:
                res[key] = SCORE_EMPTY_WEIGHT * empty[key] \
                    + SCORE_SUM_WEIGHT * summation[key] \
                    + SCORE_MERGES_WEIGHT * merge[key] \
                    - SCORE_MONOTONICITY_WEIGHT * \
                    min(monotonicity_Lr[key], monotonicity_lR[key])

            return res

        def evaluate_col(self, col: int, belong: bool) -> dict:
            res = {True: 0, False: 0}
            monotonicity_Lr = {True: 0, False: 0}
            monotonicity_lR = {True: 0, False: 0}
            merge = {True: 0, False: 0}
            summation = {True: 0, False: 0}
            empty = {True: 0, False: 0}

            prev = None
            for row in range(4):
                current = Player.Chess(self.board.getBelong((row, col)),
                                       self.board.getValue((row, col)))
                if current.value:
                    summation[current.belong] += current.value ** SCORE_SUM_POWER
                    if prev:
                        if current.eq_val(prev):
                            merge[current.belong] += .5 * current.value \
                                if current.belong == belong \
                                else -current.value
                            merge[prev.belong] += .5 * current.value \
                                if prev.belong == belong \
                                else -current.value
                        elif current.belong != belong:
                            mono = current.value ** SCORE_MONOTONICITY_POWER
                            monotonicity_lR[not belong] += mono
                            monotonicity_Lr[not belong] += mono
                            monotonicity_lR[belong] -= mono
                            monotonicity_Lr[belong] -= mono
                    prev = current
                else:
                    empty[belong] += 1

            for key in res:
                res[key] = SCORE_EMPTY_WEIGHT * empty[key] \
                    + SCORE_SUM_WEIGHT * summation[key] \
                    + SCORE_MERGES_WEIGHT * merge[key] \
                    - SCORE_MONOTONICITY_WEIGHT * \
                    min(monotonicity_Lr[key], monotonicity_lR[key])

            return res

    def __init__(self, isFirst: bool, array: list) -> None:
        self._isFirst = isFirst
        self._array = array
        self.tree = self.Tree_Node()

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
            raise ValueError('wrong mode: ' + str(mode))

    def _output_second(self, currentRound: int, board, mode: str):
        '''if mode=='position', return (row, col)
        else if mode=='direction', return int (0, 1, 2, 3 are U, D, L, R)
        '''
        if mode == POSITION_MODE:
            return self._output_second_pos(currentRound, board)
        elif mode == DIRECTION_MODE:
            return self._output_second_dir(currentRound, board)
        else:
            raise ValueError('wrong mode: ' + str(mode))

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

    def search_pos(self, )

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
                if board.getBelong((row, col_b)) == belong:
                    res += board.getValue((row, col_b)) \
                        << tp[row][col_t]

        for enemy_col in (range(4, 8) if belong else range(4)):
            for row in range(4):
                if board.getBelong((row, enemy_col)) == belong:
                    res += board.getValue((row, enemy_col)) << 5

        return res
