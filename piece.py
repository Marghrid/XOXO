from itertools import combinations

import numpy as np


class Piece:
    def __init__(self, idx: int):
        assert 0 <= idx <= 9, f"id is {idx}"
        self.num_parts = 5
        self.os = []
        self.coords = []

        init_method = self.__getattribute__(f"init_{idx}")
        init_method()

        for x1, x2 in combinations(range(len(self.coords)), 2):
            pos1, pos2 = self.coords[x1], self.coords[x2]
            distance = (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2
            if distance == 1:
                assert self.os[x1] != self.os[x2], str(self)

        print(f"Piece #{idx}")
        print(self)

    def init_0(self):
        self.coords = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
        self.os = [True, False, True, False, True]

    def init_1(self):
        self.coords = [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1)]
        self.os = [False, True, False, True, False]

    def init_2(self):
        self.coords = [(0, 0), (1, 0), (0, 1), (0, 2), (1, 2)]
        self.os = [False, True, True, False, True]

    def init_3(self):
        self.coords = [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
        self.os = [True, False, True, False, True]

    def init_4(self):
        self.coords = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)]
        self.os = [False, True, False, True, False]

    def init_5(self):
        self.coords = [(0, 0), (1, 0), (0, 1), (0, 2), (0, 3)]
        self.os = [True, False, False, True, False]

    def init_6(self):
        self.coords = [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)]
        self.os = [True, False, True, True, False]

    def init_7(self):
        self.coords = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]
        self.os = [True, False, True, False, True]

    def init_8(self):
        self.coords = [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]
        self.os = [False, True, False, True, False]

    def init_9(self):
        self.coords = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 2)]
        self.os = [True, False, True, False, False]

    def __str__(self):
        ret = ''
        for i in range(max(map(lambda c: c[0], self.coords)) + 1):
            for j in range(max(map(lambda c: c[1], self.coords)) + 1):
                if (i, j) in self.coords:
                    s = 'O' if self.os[self.coords.index((i, j))] else 'X'
                    s += ' '
                else:
                    s = ' '
                    s += ' '
                ret += s
            ret += '\n'
        return ret[:-1]

    def get_rotations(self):
        rotations = [self.coords]
        coords_matrix = np.array(self.coords)
        rotation_matrix_90 = np.array([[0, 1], [-1, 0]])
        rotation_matrix_180 = np.array([[-1, 0], [0, -1]])
        rotation_matrix_270 = np.array([[0, -1], [1, 0]])
        rotated_90 = np.dot(coords_matrix, rotation_matrix_90)
        rotated_180 = np.dot(coords_matrix, rotation_matrix_180)
        rotated_270 = np.dot(coords_matrix, rotation_matrix_270)

        print(rotated_90)
        print(rotated_180)
        print(rotated_270)
