'''对估值函数 evaluate() 的期望：
evaluate(board, isFirst) 返回 isFirst 方与 not isFirst 方的局面之差
'''
import random
import operator

# 常量定义
POSITION_MODE = 'position'
DIRECTION_MODE = 'direction'
_POSITION_MODE = '_position'
_DIRECTION_MODE = '_direction'

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

INF = float('inf')

MERGE_INTERFERENCE_THRESHOLD = 4  # 仅处理 2^5 及以上的合并
BASE_POWER = 2  # 基础分值为 2**(BASE_POWER * 级别)
ENEMY_WEIGHT = 0.75  # 估值为己方分值减去 ENEMY_WEIGHT*对方分值
BONUS_POWER = BASE_POWER  # 己方棋子在对方领域接近己方的两列时，有额外加分 2**(BONUS_POWER * 级别)
FAR_BONUS_POWER = BASE_POWER - 1 # 己方棋子在对方领域远离己方的两列时，有额外加分 2**(FAR_BONUS_POWER * 级别)


class Node:
    '''搜索树的节点.
    使用 self.node: dict 作为数据结构，每个节点存储
        self.isFirst: 此树是否在先手的视角下生成
        self.mode: 此节点决策模式. 可为 `POSITION` 或 `DIRECTION`
        self.board: 待决策棋盘
        self.currentRound: 本节点轮数
        self.evaluate: 估值函数
        self.minimax: bool, 是否为 min 节点
        self.alpha, self.beta: ab剪枝用参数
        self.nodes: 节点
    '''
    # 对对方合并方向的计数
    direction_count = {True: {RIGHT: 3, UP: 1, DOWN: 1, LEFT: 0},
                       False: {LEFT: 3, UP: 1, DOWN: 1, RIGHT: 0}}

    def __init__(self, isFirst: bool, mode: str, board, currentRound: int,
                 evaluate, minimax: bool, alpha=-INF, beta: float = INF):
        '''生成节点。
        player: 玩家
        isFirst: 这棵 ***树*** 是 !!!以谁的视角!!! 生成的
        mode: 'position' or 'direction'
        board: 棋盘. 期待传入一个副本
        currentRound: 此层轮数

        evaluate: 估值函数, evaluate(board, isFirst) 返回 isFirst 方与 not isFirst 方的局面之差
        minimax: min `True`, max `False`
        alpha, beta: alpha, beta值
        '''
        self.isFirst = isFirst
        self.mode = mode
        self.board = board
        self.currentRound = currentRound

        self.evaluate = evaluate
        self.minimax = minimax
        self.alpha = alpha
        self.beta = beta
        self.nodes = {}  # {operation: Node}

        # `ab_attr` 归本层管的参数
        # `comp` 用于本层的比较函数
        self.ab_attr = 'beta' if self.minimax else 'alpha'
        self.comp = operator.lt if self.minimax else operator.gt

    def count_direction(self, operation):
        '''记录对面对方向的操作频数
        '''
        if len(operation) == 1:  # 我也不知道为啥方向会被套进元组里
            operation = operation[0]
            self.direction_count[not self.isFirst][operation] += 1

    def deepen(self, modes: list):
        '''加深并搜索树. modes 为由新的层的 (mode, round) 元组构成的 list
        返回本层新的 alpha 或 beta
        '''
        if modes:
            # 本层没被搜过, 而且还要往更深层搜
            opers = self.operations()
            if opers:
                # 本层有路可走
                for op_func in opers:
                    # 这个 op_func 会更新棋盘, 返回棋盘有没有变
                    board_copy = self.board.copy()
                    if getattr(board_copy, op_func[0])(op_func[1], op_func[2]) == False:
                        # 棋盘在此操作下不动, 非法
                        continue
                    # 创建新节点, 给下一层
                    self.nodes[op_func[2]] = Node(self.isFirst, modes[0][0], board_copy, modes[0][1],
                                                  self.evaluate, not self.minimax, -INF, INF)
                    # 下面与之前类似
                    setattr(self.nodes[op_func[2]],
                            self.ab_attr, getattr(self, self.ab_attr))
                    new_value = self.nodes[op_func[2]].deepen(
                        modes[1:])  # 继续往深层搜
                    if self.comp(new_value, getattr(self, self.ab_attr)):
                        setattr(self, self.ab_attr, new_value)
                    if self.alpha >= self.beta:  # 剪枝条件
                        break
            if not self.nodes:
                # 如果前面没搜出什么东西, 那么把空操作弄进去
                self.nodes[()] = Node(self.isFirst, modes[0][0], self.board.copy(), modes[0][1],
                                      self.evaluate, not self.minimax, -INF, INF)
                setattr(self.nodes[()], self.ab_attr,
                        getattr(self, self.ab_attr))
                new_value = self.nodes[()].deepen(modes[1:])
                setattr(self, self.ab_attr, new_value)
        else:
            opers = self.operations()
            # 需保证层数为0的时候一定在搜索direction
            for op_func in opers:
                # 这个 op_func 会更新棋盘, 返回棋盘有没有变
                board_copy = self.board.copy()
                if getattr(board_copy, op_func[0])(op_func[1], op_func[2]) == False:
                    continue
                new_value = self.evaluate(board_copy, self.isFirst)
                if self.comp(new_value, getattr(self, self.ab_attr)):
                    setattr(self, self.ab_attr, new_value)
                if self.alpha >= self.beta:
                    break

        return getattr(self, self.ab_attr)

    def decision(self):
        '''决策. 需要先调用 deepen()
        返回 (决策, 新根节点)
        '''
        for op, node in self.nodes.items():
            if node.beta >= self.alpha:
                return op, node
        raise RuntimeError('no decision')

    def operations(self) -> list:
        '''返回可用操作的 [(名字, *调用传参), ...]
        '''
        res = []
        if self.mode == POSITION_MODE:
            try:
                # 优先在自己这边放子
                pos = self.board.getNext(
                    self.isFirst ^ self.minimax, self.currentRound)
            except IndexError:
                # 回合数到头
                pos = ()
            if pos:
                # 如果可以在自己这边放
                res.append(('add', self.isFirst ^ self.minimax, pos))

            if not res:
                # 如果局势比较晚, 或者不可以在自己这里放, 那么随机搞一个
                nones = self.board.getNone(self.isFirst == self.minimax)
                if nones:
                    random.shuffle(nones)
                    res.append(('add', self.isFirst == self.minimax, nones[0]))
        else:
            if self.minimax:
                # 对方，根据对方已有决策进行猜测
                d = self.direction_count[not self.isFirst]
                d = sorted(d, key=lambda x: d[x], reverse=True)
            else:
                # 己方，优先进攻
                d = (RIGHT, UP, DOWN, LEFT) \
                    if self.isFirst \
                    else (LEFT, UP, DOWN, RIGHT)
            for direction in d:
                res.append(('move', self.isFirst ^ self.minimax, direction))
        return res


def find_pos(board_raw: list, to_belong: bool, direction: int) -> tuple:
    '''寻找在 `to_belong` 方落子的位置。若无法阻止合并，返回 None
    board_raw: 棋盘原始数据，为嵌套列表
    direction: 为已知对方占优的合并方向
    仅处理对方至少是两个2^x间的合并, 其中 x 为 `MERGE_INTERFERENCE_THRESHOLD + 1`
    '''
    prev_value = -1
    prev_pos = None
    if direction < 2:
        # 上下方向
        cols = range(4) if to_belong else range(4, 8)
        for col in cols:
            for row in range(4):
                value = board_raw[row][col][0]
                if value:
                    # 非空
                    if value > MERGE_INTERFERENCE_THRESHOLD and value == prev_value and row - prev_pos[0] > 1:
                        return row - 1, col
                    prev_value = value
                    prev_pos = row, col
            # 重置
            prev_value = -1
            prev_pos = None
    else:
        # 左右方向
        cols = range(5) if to_belong else range(3, 8)
        for row in range(4):
            for col in cols:
                value = board_raw[row][col][0]
                if value:
                    # 非空
                    if value > MERGE_INTERFERENCE_THRESHOLD and value == prev_value and col - prev_pos[1] > 1:
                        return row, col - 1
                    prev_value = value
                    prev_pos = row, col
            # 重置
            prev_value = -1
            prev_pos = None
    return None


class Player:
    '''任务要求的 `Player` 接口
    self.tree: 搜索树的根节点
    '''
    def __init__(self, isFirst: bool, array: list) -> None:
        self._isFirst = isFirst
        self._array = array
        self.tree = Node(isFirst, POSITION_MODE, None, 0,
                         self.evaluate, False)

    def output(self, currentRound: int, board, mode: str):
        # 获得上步操作, 记进小本本
        prev_decision = board.getDecision(not self._isFirst)
        self.tree.count_direction(prev_decision)

        # 直接返回, 不浪费算力
        if mode[0] == '_':
            return

        # 建设搜索树
        decision = None
        self.tree = Node(self._isFirst, mode, board.copy(), currentRound,
                         self.evaluate, False)
        if mode == POSITION_MODE:
            # 尝试看有没有高收益的阻碍对方合并的地方
            # 寻找对面的大子合并方向
            old_score = sum(board.getScore(self._isFirst)) + \
                sum(board.getScore(not self._isFirst))
            dir_merge = {}  # {方向: 合并后的sum(getScore)减少了多少}
            direction = 0
            while direction < 4:
                board_copy = board.copy()
                if board_copy.move(not self._isFirst, direction) == False:
                    direction += 1
                    continue
                new_score = sum(board_copy.getScore(self._isFirst)) + \
                    sum(board_copy.getScore(not self._isFirst))
                delta = old_score - new_score
                if delta >= MERGE_INTERFERENCE_THRESHOLD:
                    dir_merge[direction] = delta
                direction += 1

            if dir_merge:
                max_dir = max(dir_merge, key=lambda k: dir_merge[k])
                decision = find_pos(board.getRaw(), not self._isFirst, max_dir)

            if decision == None:
                # 搜六层
                if self._isFirst:
                    self.tree.deepen(
                        [(POSITION_MODE, currentRound), (DIRECTION_MODE, currentRound),
                         (DIRECTION_MODE, currentRound), (POSITION_MODE, currentRound + 1),
                         (POSITION_MODE, currentRound + 1), (DIRECTION_MODE, currentRound + 1)])
                else:
                    self.tree.deepen(
                        [(DIRECTION_MODE, currentRound), (DIRECTION_MODE, currentRound),
                         (POSITION_MODE, currentRound + 1), (POSITION_MODE, currentRound + 1),
                         (DIRECTION_MODE, currentRound + 1), (DIRECTION_MODE, currentRound + 1)])
        elif board.getTime(self._isFirst) < .5:
            # @Mr.Luo Zhixiang
            # 搜四层
            if self._isFirst:
                self.tree.deepen(
                    [(DIRECTION_MODE, currentRound), (POSITION_MODE, currentRound + 1),
                     (POSITION_MODE, currentRound + 1), (DIRECTION_MODE, currentRound + 1)])
            else:
                self.tree.deepen(
                    [(POSITION_MODE, currentRound + 1), (POSITION_MODE, currentRound + 1),
                     (DIRECTION_MODE, currentRound + 1), (DIRECTION_MODE, currentRound + 1)])
        else:
            # 搜八层
            if self._isFirst:
                self.tree.deepen(
                    [(DIRECTION_MODE, currentRound), (POSITION_MODE, currentRound + 1),
                     (POSITION_MODE, currentRound + 1), (DIRECTION_MODE, currentRound + 1),
                     (DIRECTION_MODE, currentRound + 1), (POSITION_MODE, currentRound + 2),
                     (POSITION_MODE, currentRound + 2), (DIRECTION_MODE, currentRound + 2)])
            else:
                self.tree.deepen(
                    [(POSITION_MODE, currentRound + 1), (POSITION_MODE, currentRound + 1),
                     (DIRECTION_MODE, currentRound + 1), (DIRECTION_MODE, currentRound + 1),
                     (POSITION_MODE, currentRound + 2), (POSITION_MODE, currentRound + 2),
                     (DIRECTION_MODE, currentRound + 2), (DIRECTION_MODE, currentRound + 2)])

        # 决策
        if decision == None:
            decision, self.tree = self.tree.decision()
        return decision

    def evaluate(self, board, isFirst: bool):
        '''估值函数返回 isFirst 方与 not isFirst 方的局面之差
        '''
        # 基本分
        def func(x): return 2 ** (BASE_POWER * x)
        res = sum(map(func, board.getScore(isFirst))) - \
            ENEMY_WEIGHT * sum(map(func, board.getScore(not isFirst)))
        # 在对面的棋子的附加分
        boardList = board.getRaw()
        for col in range(4, 6) if isFirst else range(2, 4):
            for row in range(4):
                if boardList[row][col][1] == isFirst:
                    res += 2 ** (BONUS_POWER * boardList[row][col][0])
        for col in range(6, 8) if isFirst else range(2):
            for row in range(4):
                if boardList[row][col][1] == isFirst:
                    res += 2 ** (FAR_BONUS_POWER * boardList[row][col][0])
        return res
