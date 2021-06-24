import re
from itertools import combinations

from board import Board
from piece import Piece
from solution import Solution


def neg(lit: str): return lit[1:] if lit[0] == '-' else '-' + lit


class Encoder:
    def __init__(self, board: Board):
        self._vars = {}
        self.constraints = []
        self.s_fresh = -1  # counter for sequential counter's aux s variables.
        self.board = board

        self.init_vars()

    def o(self, i: int, j: int):
        assert self.board.valid_i(i), f"i: {i}"
        assert self.board.valid_j(j), f"j: {j}"

        return f"o_{str(i).rjust(len(str(self.board.max_i)), '0')}_" \
               f"{str(j).rjust(len(str(self.board.max_j)), '0')}"

    @staticmethod
    def de_o(p_name: str):
        rgx = r"o_(\d+)_(\d+)"
        return map(int, re.match(rgx, p_name).groups())

    def p(self, i: int, j: int, k: int, l: int):
        assert self.board.valid_i(i), f"i: {i}"
        assert self.board.valid_j(j), f"j: {j}"
        assert self.board.valid_k(k), f"k: {k}"
        assert 0 <= l <= self.board.pieces[k].num_parts, f"l: {l}"

        return f"p_{str(i).rjust(len(str(self.board.max_i)), '0')}_" \
               f"{str(j).rjust(len(str(self.board.max_j)), '0')}_" \
               f"{str(k).rjust(len(str(self.board.num_pieces - 1)), '0')}_" \
               f"{str(l).rjust(len(str(self.board.pieces[k].num_parts - 1)), '0')}"

    @staticmethod
    def de_p(p_name: str):
        rgx = r"p_(\d+)_(\d+)_(\d+)_(\d+)"
        return map(int, re.match(rgx, p_name).groups())

    # aux var for sequential counter encoding for <= 1 constraints
    def s(self, i):
        """ variable used for sequential counter encoding """
        return f's_{i}_{self.s_fresh}'

    def init_vars(self):
        # o vars
        for i in range(self.board.height):
            for j in range(self.board.width):
                self.add_var(self.o(i, j))

        # p vars
        for i in range(self.board.height):
            for j in range(self.board.width):
                for k in range(self.board.num_pieces):
                    for l in range(self.board.pieces[k].num_parts):
                        self.add_var(self.p(i, j, k, l))

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

    def encode(self):
        self.encode_board_constraints()

        # pieces' shape
        for piece in self.board.pieces:
            self.encode_piece_constraints(piece)

    def add_var(self, var: str):
        self._vars[var] = len(self._vars) + 1

    def make_dimacs(self):
        """ Encode constraints as CNF in DIMACS. """
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
                print("p", i, j, k, l)
            if reversed_vars[var_id].startswith("o"):
                i, j = self.de_o(reversed_vars[var_id])
                print(("o" if model[var_id] else "-o"), i, j)

    def block_model(self, model: dict):
        reversed_vars = {value: key for (key, value) in self._vars.items()}
        ctr = []
        for var_idx in model:
            if reversed_vars[var_idx].startswith("p"):
                if model[var_idx]:
                    lit = neg(reversed_vars[var_idx])
                    # else:
                    #     lit = reversed_vars[var_idx]
                    ctr.append(lit)
        assert len(ctr) == self.board.height * self.board.width
        self.add_constraint(ctr)

    def get_solution(self, model):
        reversed_vars = {value: key for (key, value) in self._vars.items()}
        solution = Solution(self.board)
        for var_id in model:
            assert var_id in reversed_vars.keys()
            if reversed_vars[var_id].startswith("p") and model[var_id]:
                i, j, k, l = self.de_p(reversed_vars[var_id])
                assert (i, j) not in solution.colors
                solution.add_color(i, j, k)
            elif reversed_vars[var_id].startswith("o"):
                i, j = self.de_o(reversed_vars[var_id])
                assert self.board.is_o(i, j) == model[var_id]
        return solution

    def encode_board_constraints(self):
        # 'X' or 'O' for the whole board:
        for i in range(self.board.height):
            for j in range(self.board.width):
                if self.board.is_o(i, j):
                    self.add_constraint([self.o(i, j)])
                else:
                    self.add_constraint([neg(self.o(i, j))])

        # Once piece per cell
        for i in range(self.board.height):
            for j in range(self.board.width):
                to_sum = []
                for k in range(self.board.num_pieces):
                    for l in range(self.board.pieces[k].num_parts):
                        to_sum.append(self.p(i, j, k, l))
                self.add_sum_eq1(to_sum)
        # One cell per piece:
        for k in range(self.board.num_pieces):
            for l in range(self.board.pieces[k].num_parts):
                to_sum = []
                for i in range(self.board.height):
                    for j in range(self.board.width):
                        to_sum.append(self.p(i, j, k, l))
                self.add_sum_eq1(to_sum)

    def encode_piece_constraints(self, piece: Piece):
        rotations = piece.get_rotations()
        for i in range(self.board.height):
            for j in range(self.board.width):
                # which rotations are valid in this position?
                valid_rotations = self.board.compute_valid_rotations(i, j, piece, rotations)

                # if no rotations are valid, the piece cannot be here
                if len(valid_rotations) == 0:
                    self.add_constraint([neg(self.p(i, j, piece.idx, 0))])
                    return

                # each part is in a valid position relative to part #0 (flipped or not)
                # pos0 -> (pos1 \/ pos1 \/ pos1 \/ ...)
                for l in range(1, piece.num_parts):
                    abs_pos_0 = self.p(i, j, piece.idx, 0)
                    rel_pos_l = [r[1][l] for r in valid_rotations]
                    # abs_pos_l contains all possible position variables for part l, considering
                    # the valid rotations.
                    abs_pos_l = [self.p(i + pos[0], j + pos[1], piece.idx, l)
                                 for pos in rel_pos_l]
                    # if part 0 is in (i, j), then part l must be in a position compatible with one
                    # of the valid rotations
                    ctr = [neg(abs_pos_0)]
                    ctr.extend(abs_pos_l)
                    self.add_constraint(ctr)

                # all parts are in the same rotation
                for rotation in valid_rotations:
                    # piece is not flipped
                    parts_positions = [(i + p[0], j + p[1]) for p in rotation[1]]
                    # first 2 parts + symbol of 1st part define the rotation:
                    pos0 = parts_positions[0]
                    pos1 = parts_positions[1]
                    o0 = not piece.os[0] if rotation[0] else piece.os[0]
                    o0_var = self.o(pos0[0], pos0[1])
                    pos_remaining = parts_positions[2:]
                    # remaining pieces must comply:
                    # if pos0 and pos1 are these, and o0 is the non-flipped value, then the
                    # remaining vars must be in one of the valid non-flipped rotations:
                    for p_idx, part in enumerate(pos_remaining):
                        l = p_idx + 2
                        ctr = [neg(self.p(pos0[0], pos0[1], piece.idx, 0)),
                               neg(self.p(pos1[0], pos1[1], piece.idx, 1)),
                               neg(o0_var) if o0 else o0_var,
                               self.p(part[0], part[1], piece.idx, l)]
                        self.add_constraint(ctr)
