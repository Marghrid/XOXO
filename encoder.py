from itertools import combinations

from piece import Piece


def neg(lit: str): return lit[1:] if lit[0] == '-' else '-' + lit


class Encoder:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.pieces = []

        self._vars = {}
        self.constraints = []
        self.s_fresh = -1  # counter for sequential counter's aux s variables.

        self.init_pieces()
        self.num_pieces = len(self.pieces)
        self.init_vars()

    def o(self, i: int, j: int):
        assert 0 <= i <= self.height
        assert 0 <= j <= self.width

        return f"o_{str(i).rjust(len(str(self.width - 1)), '0')}_" \
               f"{str(j).rjust(len(str(self.height - 1)), '0')}"

    def p(self, i: int, j: int, k: int, l: int):
        assert 0 <= i <= self.height
        assert 0 <= j <= self.width
        assert 0 <= k <= self.num_pieces
        assert 0 <= l <= self.pieces[k].num_parts

        return f"p_{str(i).rjust(len(str(self.width - 1)), '0')}_" \
               f"{str(j).rjust(len(str(self.height - 1)), '0')}_" \
               f"{str(k).rjust(len(str(self.num_pieces - 1)), '0')}_" \
               f"{str(l).rjust(len(str(self.pieces[k].num_parts - 1)), '0')}"

    # aux var for sequential counter encoding for <= 1 constraints
    def s(self, i):
        ''' variable used for sequential counter encoding '''
        return f's_{i}_{self.s_fresh}'

    def init_vars(self):
        # o vars
        for i in range(self.height):
            for j in range(self.width):
                self.add_var(self.o(i, j))

        # p vars
        for i in range(self.height):
            for j in range(self.width):
                for k in range(self.num_pieces):
                    for l in range(self.pieces[k].num_parts):
                        self.add_var(self.p(i, j, k, l))

    def add_constraint(self, constraint):
        '''add constraints, which is a list of literals'''
        assert (constraint is not None)
        assert (isinstance(constraint, list))
        self.constraints.append(constraint)

    def add_sum_eq1(self, sum_lits):
        """
        encodes clauses SUM(sum_lits) = 1.
        """
        self.add_sum_le1(sum_lits)
        # self.add_sum_le1_sc(sum_lits)
        self.add_sum_ge1(sum_lits)

    def add_sum_le1(self, sum_lits):
        """
        encodes clauses SUM(sum_lits) <= 1 using pairwise encoding.
        """
        if len(sum_lits) == 0 or len(sum_lits) == 1:
            return

        lit_pairs = list(combinations(sum_lits, 2))
        for lit_pair in lit_pairs:
            self.add_constraint([neg(lit_pair[0]), neg(lit_pair[1])])

    def add_sum_le1_sc(self, sum_lits):
        """
        encodes clauses SUM(sum_lits) <= 1 using sequential counter.
        """
        # Using Sinz 2005 as reference:
        # idx 0 of list sum_lits corresponds to s_0 (starts in 0)

        if len(sum_lits) == 0 or len(sum_lits) == 1:
            return

        self.s_fresh += 1
        n = len(sum_lits) - 1

        self.add_constraint([neg(sum_lits[0]), self.s(0)])
        self.add_constraint([neg(sum_lits[n]), neg(self.s(n - 1))])

        for i in range(1, n):
            # s(i) is true if x_1 is true
            self.add_constraint([neg(sum_lits[i]), self.s(i)])
            # s(i) is true if s(i-1) is true
            self.add_constraint([neg(self.s(i - 1)), self.s(i)])
            # x_i can only be set to true is s(i-1) is false
            self.add_constraint([neg(sum_lits[i]), neg(self.s(i - 1))])

    def add_sum_ge1(self, sum_lits):
        """
        encodes clauses SUM(sum_lits) <= 1.
        """
        self.add_constraint(sum_lits)

    def init_pieces(self):
        for k in range(10):
            p = Piece(k)
            self.pieces.append(p)

    def encode(self):
        # 'XO' for all board:
        for i in range(self.height):
            for j in range(self.width):
                if (i + j) % 2 == 0:
                    self.add_constraint([neg(self.o(i, j))])
                else:
                    self.add_constraint([self.o(i, j)])

        # Once piece per cell
        for i in range(self.height):
            for j in range(self.width):
                to_sum = []
                for k in range(self.num_pieces):
                    for l in range(self.pieces[k].num_parts):
                        to_sum.append(self.p(i, j, k, l))
                self.add_sum_eq1(to_sum)

        # One cell per piece:
        for k in range(self.num_pieces):
            for l in range(self.pieces[k].num_parts):
                to_sum = []
                for i in range(self.height):
                    for j in range(self.width):
                        to_sum.append(self.p(i, j, k, l))
                self.add_sum_eq1(to_sum)

        # Encode pieces:

        # print(self._vars)
        # print(self.constraints)
        self.pieces[1].get_rotations()

    def solve(self):
        return None

    def add_var(self, var: str):
        self._vars[var] = len(self._vars)

    def mk_cnf(self, param):
        # TODO
        '''encode constraints as CNF in DIMACS'''
        # maxid = 0
        # self.var_map = dict()
        # cs = 0
        # rv = ''
        # for c in self.constraints:
        #     if not isinstance(c, list): continue
        #     cs = cs + 1
        #     for l in c:
        #         if var(l) not in self.var_map:
        #             maxid = maxid + 1
        #             self.var_map[var(l)] = maxid
        #
        # rv += 'p cnf {} {}'.format(len(self.var_map), cs) + '\n'
        # for c in self.constraints:
        #     if isinstance(c, list):
        #         if print_comments:
        #             rv += 'c ' + str(c) + '\n'
        #         rv += ' '.join(map(str,
        #                            [-(self.var_map[var(l)]) if sign(l) else self.var_map[l] for l in
        #                             c])) + ' 0\n'
        #     else:
        #         if print_comments:
        #             rv += 'c ' + str(c) + '\n'
        #
        # return rv

    def print_model(self, param):
        # TODO
        pass

    def print_solution(self, param):
        # TODO
        pass
