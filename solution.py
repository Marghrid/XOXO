from matplotlib import pyplot as plt
from termcolor import colored

from piece import term_colors


class Solution:
    """ Represents a solution to a XOXO board. """
    _sol_num: int = 0

    def __init__(self):
        """ Instantiate an empty solution. """
        # A solution is represented by a dict of tuples (i, j) (coordinates) to ints (colors).
        self.colors = {}
        self.id = Solution._sol_num
        self.height = None
        self.width = None
        Solution._sol_num += 1

    def add_color(self, i: int, j: int, color: int):
        """ Main function to build a solution. Set position (i, j) to color color."""
        self.colors[(i, j)] = color

    def check_solution(self):
        max_i = max(map(lambda c: c[0], self.colors.keys()))
        max_j = max(map(lambda c: c[1], self.colors.keys()))

        for i in range(max_i + 1):
            for j in range(max_j + 1):
                assert (i, j) in self.colors.keys()
        self.height = max_i + 1
        self.width = max_j + 1

    def is_o(self, i: int, j: int) -> bool:
        """ Returns true if board position should have a piece with 'O' facing up."""
        return (i + j) % 2 == 1

    def show(self, filename=None):
        """ Show a solution using a matplotlib heatmap. """
        self.check_solution()
        data = []
        plt.figure()
        for i in range(self.height):
            data_r = []
            for j in range(self.width):
                data_r.append(self.colors[(i, j)])
            data.append(data_r)
        plt.imshow(data, cmap="Set3")
        plt.axis('off')

        for i in range(self.height):
            for j in range(self.width):
                is_o = self.is_o(i, j)
                plt.text(j, i, 'O' if is_o else 'X',
                         horizontalalignment='center',
                         verticalalignment='center',
                         fontweight='bold', size='xx-large', color='0.2'
                         )
        if filename is not None and len(filename) > 0:
            plt.savefig(filename,
                        format="svg", bbox_inches='tight', pad_inches=0)
        else:
            plt.show(bbox_inches='tight', pad_inches=0.15)

    def __str__(self):
        self.check_solution()
        ret = ''
        for i in range(self.height):
            for j in range(self.width):
                k = self.colors[(i, j)]
                s = colored(str(k) + ("O" if self.is_o(i, j) else "X"),
                            term_colors[k % len(term_colors)])  # +
                # str(l)
                ret += s + " "
            ret += '\n'
        return ret[:-1]

    def __repr__(self):
        self.check_solution()
        return '\n'.join(map(lambda i: ''.join(
            map(lambda j: str(self.colors[(i, j)]),
                range(self.width))),
                          range(self.height)))

    def __hash__(self):
        self.check_solution()
        return hash(repr(self))

    def dump(self, filename=None):
        self.check_solution()
        if filename is not None and len(filename) > 0:
            with open(filename, 'w+') as f:
                f.write(repr(self) + '\n')
        else:
            print(repr(self))

    def read(self, filename: str):
        with open(filename, 'r') as f:
            for i, line in enumerate(f.readlines()):
                for j, col in enumerate(line.rstrip()):
                    self.add_color(i, j, int(col))
        self.check_solution()

    def distance_to(self, other: "Solution") -> int:
        count = 0
        self.check_solution()
        other.check_solution()
        if self.width != other.width or self.height != other.height:
            raise ValueError("Solutions cannot be compared.")
        for i in range(self.height):
            for j in range(self.width):
                if self.colors[(i, j)] != other.colors[(i, j)]:
                    count += 1
        return count

    def __eq__(self, other: "Solution"):
        self.check_solution()
        other.check_solution()
        if self.width != other.width or self.height != other.height:
            raise ValueError("Solutions cannot be compared.")
        for i in range(self.height):
            for j in range(self.width):
                if self.colors[(i, j)] != other.colors[(i, j)]:
                    return False
        return True
