'''对估值函数 evaluate() 的期望：
evaluate(board, isFirst) 返回 isFirst 方与 not isFirst 方的局面之差
'''
import random
import operator

POSITION_MODE = 'position'
DIRECTION_MODE = 'direction'
_POSITION_MODE = '_position'
_DIRECTION_MODE = '_direction'

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

INF = float('inf')


class Node:
    direction_count = {True: {RIGHT: 5, UP: 3, DOWN: 3, LEFT: 0},
                       False: {LEFT: 5, UP: 3, DOWN: 3, RIGHT: 0}}

    def __init__(self, isFirst: bool, mode: str, board, currentRound: int,
                 evaluate, minimax: bool, alpha=-INF,
                 beta: float = INF, depth: int = None):
        '''生成节点。
        player: 玩家
        isFirst: 这棵 ***树*** 是 !!!以谁的视角!!! 生成的
        mode: 'position' or 'direction'
        board: 棋盘. 期待传入一个副本
        currentRound: 此层轮数

        evaluate: 估值函数, evaluate(board, isFirst) 返回 isFirst 方与 not isFirst 方的局面之差
        minimax: min `True`, max `False`
        alpha, beta: alpha, beta值
        depth: 如果是根节点, 传入期待这棵树有多深. 根节点深度记为 0
        '''
        self.isFirst = isFirst
        self.mode = mode
        self.board = board
        self.currentRound = currentRound

        self.evaluate = evaluate
        self.minimax = minimax
        self.alpha = alpha
        self.beta = beta
        self.depth = depth
        self.nodes = {}  # {operation: Node}

        # `ab_attr` 归本层管的参数
        # `comp` 用于本层的比较函数
        self.ab_attr = 'beta' if self.minimax else 'alpha'
        self.comp = operator.lt if self.minimax else operator.gt

    def release(self, operation):
        '''选取操作 operation 对应的分支
        返回新的树根; 如果该操作未被我们考虑, 返回 None
        '''
        if len(operation) == 1:  # 我也不知道为啥方向会被套进元组里
            operation = operation[0]
            self.direction_count[not self.isFirst][operation] += 1
        res = self.nodes.get(operation, None)
        if res:
            res.depth = self.depth - 1
        return res

    def deepen(self, modes: list, new_round):
        '''加深并搜索树. modes 为新的层的 mode
        返回 新的 alpha 或 beta
        '''
        # `best_so_far` 万一本轮搜出来比之前的都糟糕, 使用这个变量跟踪这种事情
        best_so_far = INF if self.minimax else -INF

        if self.nodes:
            # 本层已被搜过. 只需更新 alpha 或 beta
            new_nodes = {}  # 本字典用于剪枝. 保存要保留的节点
            for op, node in self.nodes.items():
                # min 节点更想要最小的 beta, max 节点更想要最大的 alpha
                setattr(node, self.ab_attr, getattr(
                    self, self.ab_attr))  # 更新子节点的参量
                new_value = node.deepen(modes, new_round)  # 保存子节点搜索后的新参量
                if self.comp(new_value, getattr(self, self.ab_attr)):  # 如果比现在的好, 那么更新
                    setattr(self, self.ab_attr, new_value)
                if self.comp(new_value, best_so_far):  # 同上, 更新 `best_so_far`
                    best_so_far = new_value
                new_nodes[op] = node  # 保留要留存的枝
                if self.alpha >= self.beta:  # 剪枝条件
                    break
            if self.comp(getattr(self, self.ab_attr), best_so_far):
                # 出现新境况糟于原有境况, 更新
                setattr(self, self.ab_attr, best_so_far)
            self.nodes = new_nodes  # 保留部分节点
        elif modes:
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
                    self.nodes[op_func[2]] = Node(self.isFirst, modes[0], board_copy, new_round,
                                                  self.evaluate, not self.minimax, -INF, INF, None)
                    # 下面与之前类似
                    setattr(self.nodes[op_func[2]],
                            self.ab_attr, getattr(self, self.ab_attr))
                    new_value = self.nodes[op_func[2]].deepen(
                        modes[1:], new_round)  # 继续往深层搜
                    if self.comp(new_value, getattr(self, self.ab_attr)):
                        setattr(self, self.ab_attr, new_value)
                    if self.comp(new_value, best_so_far):
                        best_so_far = new_value
                    if self.alpha >= self.beta and self.mode == POSITION_MODE:  # 剪枝条件
                        break
                if self.comp(getattr(self, self.ab_attr), best_so_far):
                    setattr(self, self.ab_attr, best_so_far)
            if not self.nodes:
                # 如果前面没搜出什么东西, 那么把空操作弄进去
                self.nodes[()] = Node(self.isFirst, modes[0], self.board.copy(), new_round,
                                      self.evaluate, not self.minimax, -INF, INF, None)
                setattr(self.nodes[()], self.ab_attr,
                        getattr(self, self.ab_attr))
                new_value = self.nodes[()].deepen(modes[1:], new_round)
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
                if self.comp(new_value, best_so_far):
                    best_so_far = new_value
                if self.alpha >= self.beta:
                    break
            if self.comp(getattr(self, self.ab_attr), best_so_far):
                setattr(self, self.ab_attr, best_so_far)

        # 根节点的 depth 要更新
        if self.depth != None:
            self.depth += len(modes)

        return getattr(self, self.ab_attr)

    def decision(self):
        '''决策. 需要先调用 deepen()
        返回 (决策, 新根节点)
        '''
        for op, node in self.nodes.items():
            if node.beta >= self.alpha:
                node.depth = self.depth - 1
                return op, node
        raise RuntimeError('no decision')

    def find_opp_pos(self):
        '''获得在对手领地下棋的可选位置列表
        按估值从大到小排列. 若不可下, 返回 `[]`
        '''
        nones = self.board.getNone(not self.isFirst)

        if not nones:  # 不存在可下的位置
            return []

        position_dic = {}

        for pos in nones:

            y, x = pos
            #横竖方向遇到的第一个对方棋子
            x_left, x_right, y_up, y_down = 0, 0, 0, 0
            #横向遇到的第一个我方棋子
            x_ours=0
            '''TODO 有没有可能合并 for 循环. 仿佛改成 while 也不错
            '''

            for i in range(x - 1, -1, -1):  # 获取四个邻域值
                if x_left:
                    break
                if self.board.getBelong((y, i)) == self.isFirst:
                    x_ours = self.board.getValue((y, i))
                    break
                x_left = self.board.getValue((y, i))

            for i in range(x + 1, 8):
                if x_right:
                    break
                if self.board.getBelong((y, i)) == self.isFirst:
                    x_ours = self.board.getValue((y, i))
                    break
                x_right = self.board.getValue((y, i))

            for j in range(y - 1, -1, -1):
                if self.board.getBelong((x, j)) == self.isFirst or y_down:
                    break
                y_down = self.board.getValue((j, x))

            for j in range(y + 1, 4):
                if self.board.getBelong((x, j)) == self.isFirst or y_up:
                    break
                y_up = self.board.getValue((j, x))

            score = x_left + x_right + y_up + y_down  # 先算四个邻域总和
            if x_right == x_left:  # 如果同一方向上有相等（可合并）的，再加一遍
                score += 2 * x_right
            if y_down == y_up:
                score += 2 * y_down
            position_dic[pos] = score

            # 对方可吞并，才考虑在内吗？
            if x_ours == x_left or x_ours == x_right:
                if x_ours > score:
                    # 权重比对方自己合并要高
                    position_dic[pos] = x_ours * 5

        return sorted(position_dic, key=lambda k: position_dic[k], reverse=True)

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
                pos = ()
            if pos:
                # 如果可以在自己这边放
                res.append(('add', self.isFirst ^ self.minimax, pos))

            '''TODO: 更好的获得位置的方法
            '''
            temp = self.find_opp_pos()

            if temp:
                res.append(('add', self.isFirst == self.minimax, temp[0]))

        else:
            '''TODO 对方进攻/防守策略判断及优化'''
            if self.minimax:
                # 对方
                d = self.direction_count[not self.isFirst]
                d = sorted(d, key=lambda x: d[x], reverse=True)
            else:
                # 自己, 优先进攻
                d = (RIGHT, UP, DOWN, LEFT) \
                    if self.isFirst \
                    else (LEFT, UP, DOWN, RIGHT)
            for direction in d:
                res.append(('move', self.isFirst ^ self.minimax, direction))
        return res

    def __repr__(self):
        return repr(self.mode) + repr(self.nodes)


class Player:
    def __init__(self, isFirst: bool, array: list) -> None:
        self._isFirst = isFirst
        self._array = array
        self.tree = Node(isFirst, POSITION_MODE, None, 0,
                         self.evaluate, False, depth=0)

    def output(self, currentRound: int, board, mode: str):
        if currentRound == 0 and mode == POSITION_MODE:
            # 初始化搜索树
            self.tree.board = board.copy()
            if self._isFirst:
                self.tree.deepen([POSITION_MODE, DIRECTION_MODE], 0)
            else:
                self.tree.deepen([DIRECTION_MODE, DIRECTION_MODE], 0)
        else:
            # 获得上部操作, 进入搜索树相应分支
            prev_decision = board.getDecision(not self._isFirst)
            self.tree = self.tree.release(prev_decision)
            if self.tree == None:
                # 不幸没有猜中, 重新建设搜索树
                mode_without_bar = mode.lstrip('_')  # 搞掉烦人的 '_'
                self.tree = Node(self._isFirst, mode_without_bar, board.copy(), currentRound,
                                 self.evaluate, False, depth=0)
                if mode_without_bar == POSITION_MODE:
                    self.tree.deepen(
                        [POSITION_MODE, DIRECTION_MODE]
                        if self._isFirst
                        else [DIRECTION_MODE, DIRECTION_MODE], currentRound)

            if mode.endswith(DIRECTION_MODE):
                # 加深搜索树
                if self._isFirst:
                    self.tree.deepen(
                        [DIRECTION_MODE, POSITION_MODE, POSITION_MODE, DIRECTION_MODE], currentRound + 1)
                else:
                    self.tree.deepen(
                        [POSITION_MODE, POSITION_MODE, DIRECTION_MODE, DIRECTION_MODE], currentRound + 1)

        if mode.startswith('_'):
            # 空操作, 我相信这棵树已经知道自己此时无路可走
            self.tree = self.tree.release(())
            assert self.tree != None
        else:
            # 决策
            decision, self.tree = self.tree.decision()
            return decision

    def evaluate(self, board, isFirst: bool):
        '''估值函数 TODO 返回 isFirst 方与 not isFirst 方的局面之差
        TODO 先后手是否可以两个版本?
        '''
        def func(x): return 1 << (3 * x)
        res = sum(map(func, board.getScore(isFirst))) - .125 * sum(map(func, board.getScore(not isFirst)))
        return res
