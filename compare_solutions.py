import glob

import numpy as np
from matplotlib import pyplot as plt

from solution import Solution

solutions_dir = "solutions/"

if __name__ == '__main__':
    files = glob.glob(solutions_dir + '*.out')
    solutions = []
    for file in files:
        sol = Solution()
        sol.read(file)
        solutions.append(sol)

    data = []
    plt.figure()
    for i in solutions:
        data_r = []
        for j in solutions:
            data_r.append(i.distance_to(j))
        data.append(data_r)
    plt.imshow(data, cmap="Blues")
    plt.show()

    last = solutions.pop(0)
    while len(solutions) > 0:
        # print(list(map(lambda sol: last.distance_to(sol), solutions)))
        closest_idx = np.argmin(list(map(lambda sol: last.distance_to(sol), solutions)))
        last.show()
        last = solutions.pop(int(closest_idx))
    last.show()
