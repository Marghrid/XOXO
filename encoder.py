import re
from itertools import combinations

import matplotlib.pyplot as plt
from termcolor import colored

from piece import Piece, colors


def neg(lit: str): return lit[1:] if lit[0] == '-' else '-' + lit


class Encoder:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.max_i = height - 1
        self.max_j = width - 1
        self.pieces = []

        self._vars = {}
        self.constraints = []
        self.s_fresh = -1  # counter for sequential counter's aux s variables.

        self.init_pieces()
        self.num_pieces = len(self.pieces)
        self.init_vars()

    def o(self, i: int, j: int):
        assert self.valid_i(i), f"i: {i}"
        assert self.valid_j(j), f"j: {j}"

        return f"o_{str(i).rjust(len(str(self.width - 1)), '0')}_" \
               f"{str(j).rjust(len(str(self.height - 1)), '0')}"

    def de_o(self, p_name: str):
        rgx = r"o_(\d+)_(\d+)"
        return map(int, re.match(rgx, p_name).groups())

    def p(self, i: int, j: int, k: int, l: int):
        assert self.valid_i(i), f"i: {i}"
        assert self.valid_j(j), f"j: {j}"
        assert 0 <= k <= self.num_pieces, f"k: {k}"
        assert 0 <= l <= self.pieces[k].num_parts, f"l: {l}"

        return f"p_{str(i).rjust(len(str(self.width - 1)), '0')}_" \
               f"{str(j).rjust(len(str(self.height - 1)), '0')}_" \
               f"{str(k).rjust(len(str(self.num_pieces - 1)), '0')}_" \
               f"{str(l).rjust(len(str(self.pieces[k].num_parts - 1)), '0')}"

    def de_p(self, p_name: str):
        rgx = r"p_(\d+)_(\d+)_(\d+)_(\d+)"
        return map(int, re.match(rgx, p_name).groups())

    # aux var for sequential counter encoding for <= 1 constraints
    def s(self, i):
        """ variable used for sequential counter encoding """
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

    def valid_i(self, i: int):
        return 0 <= i <= self.max_i

    def valid_j(self, j: int):
        return 0 <= j <= self.max_j

    def valid_k(self, k: int):
        return 0 <= k < self.num_pieces

    def add_constraint(self, constraint):
        """add constraints, which is a list of literals"""
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
        # 'X' or 'O' for the whole board:
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

        # pieces' shape
        for piece in self.pieces:
            self.encode_piece(piece)

    def solve(self):
        return None

    def add_var(self, var: str):
        self._vars[var] = len(self._vars) + 1

    def make_dimacs(self, param):
        """encode constraints as CNF in DIMACS"""
        s = ''
        s += "c Pedro's XOXO\n"
        s += f"p cnf {len(self._vars)} {len(self.constraints)}\n"
        for ctr in self.constraints:
            assert all([var in self._vars or neg(var) in self._vars for var in ctr])
            s += " ".join(map(str, [self._vars[var] if var in self._vars else -self._vars[neg(var)]
                                    for var in ctr]))
            s += ' 0\n'
        # assert len(s.split('\n')) == len(self.constraints) + 1
        with open("ex.cnf", 'w') as f:
            f.write(s)
        return s

    def print_constraints(self):
        for ctr in self.constraints:
            print(f"{{{', '.join(ctr)}}}")

    def print_model(self, model: dict):
        reversed_vars = {value: key for (key, value) in self._vars.items()}
        for var_id in model:
            assert var_id in reversed_vars.keys(), f"{var_id}"
            if reversed_vars[var_id].startswith("p") and model[var_id]:
                i, j, k, l = self.de_p(reversed_vars[var_id])
                print(i, j, k, l)

    def print_solution(self, model: dict):
        solution_os, solution_ps = self.get_solution(model)
        ret = ''
        for i in range(self.height):
            for j in range(self.width):
                k, l = solution_ps[(i, j)]
                is_o = solution_os[(i, j)]
                s = colored(str(k) + ("O" if is_o else "X"), colors[k % len(colors)])  # + str(l)
                ret += s + " "
            ret += '\n'
        print(ret)

    def show_solution(self, model: dict):
        solution_os, solution_ps = self.get_solution(model)
        data = []
        for i in range(self.height):
            data_r = []
            for j in range(self.width):
                data_r.append(solution_ps[(i, j)][0])
            data.append(data_r)
        plt.imshow(data, cmap="Set3")
        plt.axis('off')

        for i in range(self.height):
            for j in range(self.width):
                is_o = solution_os[(i, j)]
                plt.text(j, i, 'O' if is_o else 'X',
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontweight='bold', size='xx-large', color='0.2'
                         )
        plt.show(bbox_inches='tight', pad_inches=0.15)

    def get_solution(self, model):
        reversed_vars = {value: key for (key, value) in self._vars.items()}
        solution_ps = {}
        solution_os = {}
        for var_id in model:
            assert var_id in reversed_vars.keys()
            if reversed_vars[var_id].startswith("p") and model[var_id]:
                i, j, k, l = self.de_p(reversed_vars[var_id])
                assert (i, j) not in solution_ps
                solution_ps[(i, j)] = (k, l)
            elif reversed_vars[var_id].startswith("o"):
                i, j = self.de_o(reversed_vars[var_id])
                assert (i, j) not in solution_os
                solution_os[(i, j)] = model[var_id]
        return solution_os, solution_ps

    def encode_piece(self, piece: Piece):
        rotations = piece.get_rotations()
        for i in range(self.height):
            for j in range(self.width):
                # which rotations are valid in this position?
                valid_rotations = []
                for rotation in rotations:
                    min_i = min(map(lambda coord: i + coord[0], rotation))
                    max_i = max(map(lambda coord: i + coord[0], rotation))
                    min_j = min(map(lambda coord: j + coord[1], rotation))
                    max_j = max(map(lambda coord: j + coord[1], rotation))
                    if self.valid_i(max_i) and self.valid_i(min_i) and \
                            self.valid_j(min_j) and self.valid_j(max_j):
                        valid_rotations.append(rotation)

                # if no rotations are valid, the piece cannot be here
                if len(valid_rotations) == 0:
                    self.add_constraint([neg(self.p(i, j, piece.idx, 0))])
                    return

                # each part is in a valid position relative to part #0
                for l in range(1, piece.num_parts):
                    p_position_0 = self.p(i, j, piece.idx, 0)
                    positions_l = [r[l] for r in valid_rotations]
                    p_positions_l = [self.p(i + pos[0], j + pos[1], piece.idx, l) for pos in
                                     positions_l]
                    ctr = [neg(p_position_0)]
                    ctr.extend(p_positions_l)
                    self.add_constraint(ctr)

                # all parts are in the same rotation
                for rotation in valid_rotations:
                    parts_positions = [(i + p[0], j + p[1]) for p in rotation]
                    # first 2 parts define the rotation:
                    first = parts_positions[0]
                    second = parts_positions[1]
                    remaining = parts_positions[2:]
                    # remaining pieces must comply
                    for p_idx, part in enumerate(remaining):
                        l = p_idx + 2
                        ctr = [neg(self.p(first[0], first[1], piece.idx, 0)),
                               neg(self.p(second[0], second[1], piece.idx, 1)),
                               self.p(part[0], part[1], piece.idx, l)]
                        self.add_constraint(ctr)

                # each part is in the correct 'X' or 'O'
                for l in range(piece.num_parts):
                    pos_l = self.p(i, j, piece.idx, l)
                    if piece.os[l]:  # this part is an 'O'
                        ctr = [neg(pos_l), self.o(i, j)]
                    else:
                        ctr = [neg(pos_l), neg(self.o(i, j))]
                    self.add_constraint(ctr)
