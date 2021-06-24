# Press the green button in the gutter to run the script.
import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional

from board import Board
from encoder import Encoder


def sign(lit): return lit[0] == '-'


def var(lit): return lit[1:] if lit[0] == '-' else lit


config: Optional["Configurations"] = None
solver = "cadical"
solutions = set()


@dataclass
class Configurations:
    print_constraints: bool
    print_model: bool
    show_solution: bool
    all_models: bool
    debug: bool


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
    print("# decoding result from solver.")
    rc = p.returncode
    s_out = str(po, encoding='utf-8').splitlines()
    s_err = str(pe, encoding='utf-8').split()
    if config.debug:
        print('\n'.join(s_out), file=sys.stderr)
        print(cnf, file=sys.stderr)
        print(s_out)

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
    argparser.add_argument('-a', '--all-models', action='store_true', help='Get all models')
    argparser.add_argument('-m', '--print-model', action='store_true', help='Print model')
    argparser.add_argument('-s', '--show-solution', action='store_true',
                           help='Show solution using matplotlib')
    argparser.add_argument('-c', '--print-constraints', action='store_true',
                           help='Print all encoded constraints')
    argparser.add_argument('-d', '--debug', action='store_true', help='Debug solver')
    args = argparser.parse_args()

    config = Configurations(args.print_constraints, args.print_model, args.show_solution,
                            args.all_models, args.debug)


def handle_sat(model: dict, encoder: Encoder):
    """ Print everything after a positive reply from the solver. """
    solution = encoder.get_solution(model)
    if config.print_model:
        encoder.print_model(model)
    print("SAT")
    print(solution)
    if solution not in solutions and config.show_solution:
        solution.show()
    solutions.add(solution)


def main():
    global solutions
    print("# encoding...", end=' ')
    start_time = time.time()
    board = Board(width=10, height=5)
    encoder = Encoder(board)
    encoder.encode()
    print(f"took {nice_time(time.time() - start_time)}.")

    if config.print_constraints:
        print("# encoded constraints")
        encoder.print_constraints()
        print("# END encoded constraints")

    result, model = send_to_solver(encoder.make_dimacs())
    if not config.all_models:
        if result == 1:
            assert model is not None
            handle_sat(model, encoder)
        elif result == 0:
            print("UNSAT")
        else:
            print("ERROR: something went wrong with the solver")

    else:  # get all models
        num_sat_calls = 0
        while result == 1:
            assert model is not None
            num_sat_calls += 1
            handle_sat(model, encoder)

            # block this model
            encoder.block_model(model)
            if config.print_constraints:
                print("# encoded constraints")
                encoder.print_constraints()
                print("# END encoded constraints")

            # get new model
            result, model = send_to_solver(encoder.make_dimacs())
        print("# End of models.")
        print(f"{num_sat_calls} models, {len(solutions)} distinct solutions")


if __name__ == '__main__':
    read_cmd_args()
    assert config is not None
    main()
