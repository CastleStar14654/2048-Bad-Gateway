
class Board:
    def __init__(self, lst):
        self.lst = lst
    def getValue(self, tuple):
        return abs(self.lst[tuple[0]][tuple[1]])
    def getBelong(self, tuple):
        return self.lst[tuple[0]][tuple[1]] > 0

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
    def __init__(self, board=None):
        self.board = board
        self.tree = {}

    def __len__(self):
        return len(self.tree)

    def __getitem__(self, key):
        return self.tree[key]

    def __contains__(self, item):
        return item in self.tree

    def __bool__(self, item):
        return bool(self.tree)

    def search(self, mode: str, isFirst: bool, one_layer: bool) -> None:
        '''search and deepen the tree
        starting from `self.board`, player `isFirst`, playing the `mode` ('position' or 'direction')
        `one_layer`:
            if `True`, search for 1 layer
            if `False`, search for at least 2 layers, and then search till the end of the round
        '''
        pass

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

        # vertival
        for col in range(4):
            sub_res = self.evaluate_row(col, True)
            res[True] += sub_res[True]
            res[False] += sub_res[False]
        for col in range(4, 8):
            sub_res = self.evaluate_row(col, False)
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

        belong = True
        prev = None
        for col in range(4):
            current = self.Chess(self.board.getBelong((row, col)),
                                    self.board.getValue((row, col)))
            if current.value:
                summation[current.belong] += current.value ** SCORE_SUM_POWER
                if prev:
                    if current.eq_val(prev):
                        merge[current.belong] += .5
                        merge[prev.belong] += .5
                    else:
                        mono = current.value ** SCORE_MONOTONICITY_POWER \
                            - prev.value ** SCORE_MONOTONICITY_POWER
                        if not current.eq_belong(prev) or current.belong != belong:
                            monotonicity_lR[belong] -= abs(mono)
                            monotonicity_Lr[belong] -= abs(mono)
                        elif mono > 0:
                            monotonicity_lR[belong] += mono
                        else:
                            monotonicity_Lr[belong] -= mono
                prev = current
            else:
                empty[belong] += 1

        belong = False
        for col in range(4, 8):
            current = self.Chess(self.board.getBelong((row, col)),
                                    self.board.getValue((row, col)))
            if current.value:
                summation[current.belong] += current.value ** SCORE_SUM_POWER
                if current.eq_val(prev):
                    merge[current.belong] += .5
                    merge[prev.belong] += .5
                elif col != 4:
                    mono = current.value ** SCORE_MONOTONICITY_POWER \
                        - prev.value ** SCORE_MONOTONICITY_POWER
                    if not current.eq_belong(prev) or current.belong != belong:
                        monotonicity_lR[belong] -= abs(mono)
                        monotonicity_Lr[belong] -= abs(mono)
                    elif mono > 0:
                        monotonicity_lR[belong] += mono
                    else:
                        monotonicity_Lr[belong] -= mono
                prev = current
            else:
                empty[belong] += 1

        for key in res:
            res[key] = SCORE_EMPTY_WEIGHT * empty[key]
                - SCORE_SUM_WEIGHT * summation[key]
                + SCORE_MERGES_WEIGHT * merge[key]
                - SCORE_MONOTONICITY_WEIGHT * min(monotonicity_Lr[key], monotonicity_lR[key])

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
            current = self.Chess(self.board.getBelong((row, col)),
                                    self.board.getValue((row, col)))
            if current.value:
                summation[current.belong] += current.value ** SCORE_SUM_POWER
                if prev:
                    if current.eq_val(prev):
                        merge[current.belong] += .5
                        merge[prev.belong] += .5
                    else:
                        mono = current.value ** SCORE_MONOTONICITY_POWER \
                            - prev.value ** SCORE_MONOTONICITY_POWER
                        if not current.eq_belong(prev) or current.belong != belong:
                            monotonicity_lR[belong] -= abs(mono)
                            monotonicity_Lr[belong] -= abs(mono)
                        elif mono > 0:
                            monotonicity_lR[belong] += mono
                        else:
                            monotonicity_Lr[belong] -= mono
                prev = current
            else:
                empty[belong] += 1

        for key in res:
            res[key] = SCORE_EMPTY_WEIGHT * empty[key]
                - SCORE_SUM_WEIGHT * summation[key]
                + SCORE_MERGES_WEIGHT * merge[key]
                - SCORE_MONOTONICITY_WEIGHT * min(monotonicity_Lr[key], monotonicity_lR[key])

        return res
