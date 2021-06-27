from itertools import combinations

import numpy as np
from matplotlib import pyplot as plt
from termcolor import colored

term_colors = ["red", "green", "yellow", "blue", "magenta", "cyan"]


class Piece:
    def __init__(self, idx: int):
        assert 0 <= idx <= 9, f"id is {idx}"
        self.num_parts = 5
        self.os = []
        self.coords = []
        self.idx = idx

        # DIRTY, UGLY HACK!! Pieces are hardcoded.
        init_method = self.__getattribute__(f"init_{idx}")
        init_method()

        for x1, x2 in combinations(range(len(self.coords)), 2):
            pos1, pos2 = self.coords[x1], self.coords[x2]
            distance = (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2
            if distance == 1:
                assert self.os[x1] != self.os[x2], str(self)

        # debug:
        # self.show()

    def init_0(self):
        self.coords = [[0, 0], [0, 1], [1, 1], [2, 1], [2, 2]]
        self.os = [False, True, False, True, False]

    def init_1(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [1, 1], [2, 1]]
        self.os = [True, False, True, True, False]

    def init_2(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 2]]
        self.os = [False, True, False, True, True]

    def init_3(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4]]
        self.os = [True, False, True, False, True]

    def init_4(self):
        self.coords = [[0, 0], [0, 1], [1, 1], [1, 2], [2, 2]]
        self.os = [False, True, False, True, False]

    def init_5(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [0, 3], [1, 0]]
        self.os = [True, False, True, False, False]

    def init_6(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [1, 2], [1, 3]]
        self.os = [True, False, True, False, True]

    def init_7(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [1, 0], [1, 1]]
        self.os = [True, False, True, False, True]

    def init_8(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2]]
        self.os = [True, False, True, False, True]

    def init_9(self):
        self.coords = [[0, 0], [0, 1], [0, 2], [0, 3], [1, 2]]
        self.os = [True, False, True, False, False]

    def __str__(self):
        ret = ''
        for i in range(max(map(lambda c: c[0], self.coords)) + 1):
            for j in range(max(map(lambda c: c[1], self.coords)) + 1):
                if [i, j] in self.coords:
                    s = str(self.idx) + ('O' if self.os[self.coords.index([i, j])] else 'X')
                    s = colored(s, term_colors[self.idx % len(term_colors)])
                else:
                    s = f'  '
                ret += s
            ret += '\n'
        return ret[:-1]

    def show(self):
        data = []
        max_i = max(1, max(map(lambda coord: coord[0], self.coords)))
        max_j = max(1, max(map(lambda coord: coord[1], self.coords)))
        # plt.figure(figsize=(2.4, 2))
        plt.figure(figsize=(max_j, max_i))
        for i in range(max_i + 1):
            data_r = []
            for j in range(max_j + 1):
                if [i, j] in self.coords:
                    data_r.append(self.idx)
                else:
                    data_r.append(-1)
            data.append(data_r)
        plt.imshow(data, cmap="Blues")
        plt.axis('off')
        # plt.gca().yaxis.get_major_locator().set_params(integer=True)
        # plt.gca().xaxis.get_major_locator().set_params(integer=True)
        # plt.gca().xaxis.tick_top()

        for i in range(max_i + 1):
            for j in range(max_j + 1):
                if [i, j] in self.coords:
                    is_o = self.os[self.coords.index([i, j])]
                    t = 'O' if is_o else 'X'
                    # t = str(self.coords.index([i, j]))
                    plt.text(j, i, t,
                             horizontalalignment='center',
                             verticalalignment='center',
                             fontweight='bold', size='x-large', color='0.9'
                             )
        plt.title(f"Piece #{self.idx}")
        plt.show(bbox_inches='tight', pad_inches=0)
        # plt.savefig(fname=f"p{self.idx}.pdf", format="pdf", bbox_inches='tight', pad_inches=0)

    def get_rotations(self):
        """ Returns alternate sets of coordinates for pieces, considering all possible rotations.
        Solution is a tuple (flipped, coordinates), where flipped is a bool and coordinates a
        list. """
        rotation_mat_90 = np.array([[0, 1], [-1, 0]])
        rotation_mat_180 = np.array([[-1, 0], [0, -1]])
        rotation_mat_270 = np.array([[0, -1], [1, 0]])

        # Initial coordinates are a non-flipped rotation.
        rotations = [(False, self.coords)]
        coords_mat = np.array(self.coords)

        # rotate rotate rotate
        rotated_90 = np.dot(coords_mat, rotation_mat_90).tolist()
        rotated_180 = np.dot(coords_mat, rotation_mat_180).tolist()
        rotated_270 = np.dot(coords_mat, rotation_mat_270).tolist()
        rotations.append((False, rotated_90))
        rotations.append((False, rotated_180))
        rotations.append((False, rotated_270))

        # flip
        flipped_coords_mat = np.dot(np.array(self.coords), np.array([[-1, 0], [0, 1]]))
        rotations.append((True, flipped_coords_mat.tolist()))

        # rotate rotate rotate
        rotated_90 = np.dot(flipped_coords_mat, rotation_mat_90).tolist()
        rotated_180 = np.dot(flipped_coords_mat, rotation_mat_180).tolist()
        rotated_270 = np.dot(flipped_coords_mat, rotation_mat_270).tolist()
        rotations.append((True, rotated_90))
        rotations.append((True, rotated_180))
        rotations.append((True, rotated_270))

        return rotations
