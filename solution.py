from matplotlib import pyplot as plt
from termcolor import colored

from board import Board
from piece import term_colors


class Solution:
    """ Represents a solution to a XOXO board. """
    _sol_num: int = 0

    def __init__(self, board: Board):
        """ Instantiate an empty solution. """
        self.board = board
        # A solution is represented by a dict of tuples (i, j) (coordinates) to ints (colors).
        self.colors = {}
        self.id = Solution._sol_num
        Solution._sol_num += 1

    def add_color(self, i: int, j: int, color: int):
        """ Main function to build a solution. Set position (i, j) to color color."""
        self.colors[(i, j)] = color

    def show(self, filename=None):
        """ Show a solution using a matplotlib heatmap. """
        data = []
        for i in range(self.board.height):
            data_r = []
            for j in range(self.board.width):
                data_r.append(self.colors[(i, j)])
            data.append(data_r)
        plt.imshow(data, cmap="Set3")
        plt.axis('off')

        for i in range(self.board.height):
            for j in range(self.board.width):
                is_o = self.board.is_o(i, j)
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
        ret = ''
        for i in range(self.board.height):
            for j in range(self.board.width):
                k = self.colors[(i, j)]
                s = colored(str(k) + ("O" if self.board.is_o(i, j) else "X"),
                            term_colors[k % len(term_colors)])  # +
                # str(l)
                ret += s + " "
            ret += '\n'
        return ret[:-1]

    def dump(self, filename=None):
        s = '\n'.join(map(lambda i: ''.join(
            map(lambda j: str(self.colors[(i, j)]),
                range(self.board.width))),
                        range(self.board.height)))
        if filename is not None and len(filename) > 0:
            with open(filename, 'w+') as f:
                f.write(s + '\n')
        else:
            print(s)
