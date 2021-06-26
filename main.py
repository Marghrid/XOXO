# Press the green button in the gutter to run the script.
import argparse
import glob
import os
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional

from board import Board
from encoder2 import Encoder2


def sign(lit): return lit[0] == '-'


def var(lit): return lit[1:] if lit[0] == '-' else lit


config: Optional["Configurations"] = None
solver = "cadical"
solutions = set()

inesc_servers = ["centaurus", "musca", "octans", "scutum", "spica", "serpens", "sextans", "crux",
                 "crater", "corvus", "dorado"]
solutions_dir = "solutions/"
pretty_representations_dir = "/home/macf/public_html/xoxo/configs/"


@dataclass
class Configurations:
    print_constraints: bool
    print_model: bool
    show_solution: bool
    store_solution: bool
    all_models: bool
    debug: bool


def ready_dirs():
    global solutions_dir, pretty_representations_dir
    if solutions_dir[-1] != "/":
        solutions_dir += "/"
    if pretty_representations_dir[-1] != "/":
        pretty_representations_dir += "/"

    if config.store_solution:
        if not os.path.exists(solutions_dir):
            os.makedirs(solutions_dir)
        else:
            input(f"Do you want to remove all files in {solutions_dir} [y|n]? ")
            if 'y':
                files = glob.glob(solutions_dir + '*.txt')
                for file in files:
                    os.remove(file)
    if config.show_solution and  socket.gethostname() in inesc_servers:
        if not os.path.exists(pretty_representations_dir):
            os.makedirs(pretty_representations_dir)
        else:
            input(f"Do you want to remove all files in {pretty_representations_dir} [y|n]? ")
            if 'y':
                files = glob.glob(pretty_representations_dir + '*.txt')
                for file in files:
                    os.remove(file)


def nice_time(total_seconds):
    """ Prints a time in a nice, legible format. """
    if total_seconds < 60:
        return f'{round(total_seconds, 1)}s'
    total_seconds = round(total_seconds)
    mins, secs = divmod(total_seconds, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    ret = ''
    if days > 0:
        ret += f'{days}d'
    if hours > 0:
        ret += f'{hours}h'
    if mins > 0:
        ret += f'{mins}m'
    ret += f'{secs}s'
    return ret


def get_model(lines):
    """ Returns a dict from positive integer DIMACS var ids to bools. """
    vals = dict()
    found = False
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
        if not line.startswith('v ') and not line.startswith('V '):
            continue
        found = True
        vs = line.split()[1:]
        for v in vs:
            if v == '0':
                break
            vals[int(var(v))] = not sign(v)
    return vals if found else None


def send_to_solver(cnf: str):
    """ Pipe a DIMACS string to solver. """
    global config
    print(f"# sending to solver '{solver}'...", end=' ')
    start_time = time.time()
    p = subprocess.Popen(solver, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    po, pe = p.communicate(input=bytes(cnf, encoding='utf-8'))
    print(f"took {nice_time(time.time() - start_time)}.")
    print("# decoding result from solver...", end=' ')
    start_time = time.time()
    rc = p.returncode
    s_out = str(po, encoding='utf-8').splitlines()
    s_err = str(pe, encoding='utf-8').split()
    if config.debug:
        print('\n'.join(s_out), file=sys.stderr)
        print(cnf, file=sys.stderr)
        print(s_out)
    print(f"took {nice_time(time.time() - start_time)}.")

    if rc == 10:
        model = get_model(s_out)
        return 1, model
    elif rc == 20:
        return 0, None
    else:
        return None


def read_cmd_args():
    """ Reads options from command line arguments.
    Stores them in config, a global Configurations  object. """
    global config
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-a', '--all-models', action='store_true', help='Get all models.')
    argparser.add_argument('-m', '--print-model', action='store_true', help='Print model.')
    argparser.add_argument('-s', '--show-solution', action='store_true',
                           help='Show solution using matplotlib.')
    argparser.add_argument('-t', '--store-solution', action='store_true',
                           help='Store solution in a text file.')
    argparser.add_argument('-c', '--print-constraints', action='store_true',
                           help='Print all encoded constraints.')
    argparser.add_argument('-d', '--debug', action='store_true', help='Debug solver')
    args = argparser.parse_args()

    config = Configurations(args.print_constraints, args.print_model, args.show_solution,
                            args.store_solution, args.all_models, args.debug)


def handle_sat(model: dict, encoder, elapsed):
    """ Print everything after a positive reply from the solver. """
    solution = encoder.get_solution(model)
    if config.print_model:
        encoder.print_model(model)
    print("SAT")
    print(f"# Solution #{len(solutions) + 1} after {nice_time(elapsed)}:")
    print(solution)
    print(f"# End of solution #{len(solutions) + 1}. "
          f"Avg. {nice_time(elapsed/(len(solutions) + 1))} per solution.")
    if config.store_solution:
        filename = solutions_dir + f'xoxo_{len(solutions):03}.out'
        print(f"# Saving solution to {filename}...")
        solution.dump(filename)
    if solution not in solutions and config.show_solution:
        if socket.gethostname() in inesc_servers:
            filename = pretty_representations_dir + f'xoxo_{len(solutions):03}.svg'
            solution.show(filename)
        else:
            solution.show()

    solutions.add(solution)


def main():
    global solutions
    board = Board(width=10, height=5)
    encoder = Encoder2(board)
    print(f"# encoding with {encoder.__class__.__name__}...", end=' ')
    start_time = time.time()
    encoder.encode()
    print(f"took {nice_time(time.time() - start_time)}.")

    if config.print_constraints:
        print("# Encoded constraints")
        encoder.print_constraints()
        print("# End encoded constraints")

    start_time = time.time()
    result, model = send_to_solver(encoder.make_dimacs())
    if not config.all_models:
        if result == 1:
            assert model is not None
            handle_sat(model, encoder, time.time() - start_time)
        elif result == 0:
            print("UNSAT")
        else:
            print("ERROR: something went wrong with the solver")

    else:  # get all models
        num_sat_calls = 0
        print("# All solutions.")
        while result == 1:
            assert model is not None
            num_sat_calls += 1
            handle_sat(model, encoder, time.time() - start_time)

            # block this model
            print("# blocking model...", end=' ')
            encoder.block_model(model)
            if config.print_constraints:
                print("# Encoded constraints")
                encoder.print_constraints()
                print("# End of encoded constraints")

            # get new model
            result, model = send_to_solver(encoder.make_dimacs())
        elapsed = time.time() - start_time
        print("# End of all solutions.")
        print(f"# {num_sat_calls} models, {len(solutions)} distinct solutions in "
              f"{nice_time(elapsed)}.")


if __name__ == '__main__':
    read_cmd_args()
    ready_dirs()
    assert config is not None
    main()
