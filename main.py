# Press the green button in the gutter to run the script.
import argparse
import subprocess
import sys
import time

from encoder import Encoder


def sign(lit): return lit[0] == '-'


def var(lit): return lit[1:] if lit[0] == '-' else lit


solver = "cadical"


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
    vals = dict()
    found = False
    for line in lines:
        line = line.rstrip()
        if not line: continue
        if not line.startswith('v ') and not line.startswith('V '): continue
        found = True
        vs = line.split()[1:]
        for v in vs:
            if v == '0': break
            vals[int(var(v))] = not sign(v)
    return vals if found else None


def send_to_solver(cnf: str):
    print(f"# sending to solver '{solver}'. Dimacs: {len(cnf)} chars.")
    start_time = time.time()
    p = subprocess.Popen(solver, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    po, pe = p.communicate(input=bytes(cnf, encoding='utf-8'))
    elapsed = time.time() - start_time
    print(f"# took {nice_time(elapsed)}.")
    print("# decoding result from solver")
    rc = p.returncode
    s_out = str(po, encoding='utf-8').splitlines()
    s_err = str(pe, encoding='utf-8').split()
    if debug_solver:
        print('\n'.join(s_out), file=sys.stderr)
        print(cnf, file=sys.stderr)
        print(s_out)

    if rc == 10:
        return 1, s_out

    elif rc == 20:
        return 0, s_out
    else:
        return None


if __name__ == '__main__':

    debug_solver = False

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-a', '--all-models', action='store_true', help='Get all models')
    argparser.add_argument('-m', '--print-model', action='store_true', help='Print model')
    argparser.add_argument('-s', '--show-solution', action='store_true',
                           help='Show solution using matplotlib')
    argparser.add_argument('-c', '--print-constraints', action='store_true',
                           help='Print all encoded constraints')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Print everything')
    argparser.add_argument('-d', '--debug', action='store_true', help='Debug solver')
    args = argparser.parse_args()

    print_constraints = args.print_constraints
    print_model = args.print_model
    show_solution = args.show_solution
    get_all_models = args.all_models
    if args.verbose:
        print_constraints = True
        print_model = True
    debug_solver = args.debug

    print("# encoding")

    board_height = 5
    board_width = 10
    encoder = Encoder(board_width, board_height)
    encoder.encode()

    if print_constraints:
        print("# encoded constraints")
        encoder.print_constraints()
        print("# END encoded constraints")

    result, solver_output = send_to_solver(encoder.make_dimacs())

    if not get_all_models:
        if result == 1:
            model = get_model(solver_output)
            if print_model:
                encoder.print_model(model)
            print("SAT")
            encoder.print_solution(model)
            if show_solution:
                encoder.show_solution(model)

        elif result == 0:
            print("UNSAT")
        else:
            print("ERROR: something went wrong with the solver")

    else:
        model = None
        old = None
        while result == 1:

            model = get_model(solver_output)

            if print_model:
                encoder.print_model(model)
            encoder.print_solution(model)
            if show_solution:
                encoder.show_solution(model)

            encoder.block_model(model)
            if print_constraints:
                print("# encoded constraints")
                encoder.print_constraints()
                print("# END encoded constraints")
            result, solver_output = send_to_solver(encoder.make_dimacs())
        print("# End of models")
