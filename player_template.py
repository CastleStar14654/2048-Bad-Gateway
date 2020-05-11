'''code template of Player
'''

POSITION_MODE ='position'
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
        pass

    def _output_first_dir(self, currentRound: int, board) -> int:
        '''return int (0, 1, 2, 3 are U, D, L, R)
        '''
        pass

    def _output_second_pos(self, currentRound: int, board) -> tuple:
        '''return (row, col)
        '''
        pass

    def _output_second_dir(self, currentRound: int, board) -> int:
        '''return int (0, 1, 2, 3 are U, D, L, R)
        '''
        pass
