from piece import Piece


class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.max_i = height - 1
        self.max_j = width - 1
        self.pieces = []

        self.init_pieces()
        self.num_pieces = len(self.pieces)

    def init_pieces(self):
        for k in range(10):
            p = Piece(k)
            self.pieces.append(p)

    def is_o(self, i: int, j: int) -> bool:
        """ Returns true if board position should have a piece with 'O' facing up."""
        return (i + j) % 2 == 1

    def valid_i(self, i: int):
        """ Returns true if i is a valid row index. """
        return 0 <= i <= self.max_i

    def valid_j(self, j: int):
        """ Returns true if j is a valid column index. """
        return 0 <= j <= self.max_j

    def valid_k(self, k: int):
        """ Returns true if k is a valid piece index. """
        return 0 <= k < self.num_pieces

    def compute_valid_rotations(self, i: int, j: int, piece: Piece, all_rotations: list):
        """ Given a list of all possible piece rotations, returns the rotations
        that are allowed for coordinate (i, j), i.e., that don't fall off the board. """
        valid_rotations = []
        # we want rotations with rotation[0] = (piece.os[0] != is_o(i, j))
        for flipped, positions in filter(lambda r: r[0] == (piece.os[0] != self.is_o(i, j)),
                                         all_rotations):
            min_i = min(map(lambda coord: i + coord[0], positions))
            max_i = max(map(lambda coord: i + coord[0], positions))
            min_j = min(map(lambda coord: j + coord[1], positions))
            max_j = max(map(lambda coord: j + coord[1], positions))
            if self.valid_i(max_i) and self.valid_i(min_i) and \
                    self.valid_j(min_j) and self.valid_j(max_j):
                valid_rotations.append((flipped, positions))
        return valid_rotations
