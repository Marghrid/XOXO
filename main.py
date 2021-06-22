from itertools import combinations


class Piece:
    def __init__(self, id: int):
        assert 0 <= id <= 9, f"id is {id}"
        self.num_parts = 5
        self.os = []
        self.coords = []

        init_method = self.__getattribute__(f"init_{id}")
        init_method()

        for x1, x2 in combinations(range(len(self.coords)), 2):
            pos1, pos2 = self.coords[x1], self.coords[x2]
            distance = (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2
            if distance == 1:
                assert self.os[x1] != self.os[x2], str(self)

    def __str__(self):
        ret = ''
        for i in range(max(map(lambda c: c[0], self.coords))):
            for j in range(max(map(lambda c: c[1], self.coords))):
                if (i, j) in self.coords:
                    s = 'O' if self.os[self.coords.index((i, j))] else 'X'
                else:
                    s = ' '
                ret += s
            ret += '\n'
        return ret[:-1]

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
        self.coords = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2)]
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


class Encoder:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pieces = []

        self._vars = {}

        self.init_pieces()
        self.num_pieces = len(self.pieces)
        self.init_vars()

    def o(self, i: int, j: int):
        assert 0 <= i <= self.width
        assert 0 <= j <= self.height

        return f"o_{str(i).rjust(len(str(self.width - 1)), '0')}_" \
               f"{str(j).rjust(len(str(self.height - 1)), '0')}"

    def p(self, i: int, j: int, k: int, l: int):
        assert 0 <= i <= self.width
        assert 0 <= j <= self.height
        assert 0 <= k <= self.num_pieces
        assert 0 <= l <= self.pieces[k].num_parts

        return f"p_{str(i).rjust(len(str(self.width - 1)), '0')}_" \
               f"{str(j).rjust(len(str(self.height - 1)), '0')}_" \
               f"{str(k).rjust(len(str(self.num_pieces - 1)), '0')}_" \
               f"{str(l).rjust(len(str(self.pieces[k].num_parts - 1)), '0')}"

    def init_pieces(self):
        for k in range(10):
            p = Piece(k)
            self.pieces.append(p)

    def init_vars(self):
        # o vars
        for i in range(self.width):
            for j in range(self.height):
                self.add_var(self.o(i, j))

        # p vars
        for i in range(self.width):
            for j in range(self.height):
                for k in range(self.num_pieces):
                    for l in range(self.pieces[k].num_parts):
                        self.add_var(self.p(i, j, k, l))

    def encode(self):
        print(self._vars)

    def solve(self):
        return None

    def add_var(self, var: str):
        self._vars[var] = len(self._vars)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    board_height = 5
    board_width = 10
    encoder = Encoder(board_width, board_height)
    encoder.encode()
    solution = encoder.solve()
