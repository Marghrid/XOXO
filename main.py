# Press the green button in the gutter to run the script.
import argparse
import subprocess
import sys
import time


def sign(l): return l[0] == '-'


def var(l): return l[1:] if l[0] == '-' else l


from encoder import Encoder

solver = "cadical"


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


if __name__ == '__main__':

    debug_solver = False

    argparser = argparse.ArgumentParser()
    # argparser.add_argument('-t', '--print_tree', action='store_true', help='print decision tree')
    argparser.add_argument('-m', '--print_model', action='store_true', help='print model')
    argparser.add_argument('-c', '--print_constraints', action='store_true',
                           help='print all encoded constraints')
    argparser.add_argument('-v', '--verbose', action='store_true', help='print everything')
    argparser.add_argument('-d', '--debug', action='store_true', help='debug solver')
    args = argparser.parse_args()

    print_constraints = args.print_constraints
    print_model = args.print_model
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
        # print("# " + "\n# ".join(map(str, encoder.constraints)))
        encoder.print_constraints()
        print("# END encoded constraints")

    print("# sending to solver '" + str(solver) + "'")
    cnf = encoder.make_dimacs(False)
    start_time = time.time()
    p = subprocess.Popen(solver, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    (po, pe) = p.communicate(input=bytes(cnf, encoding='utf-8'))
    elapsed = time.time() - start_time

    print("# decoding result from solver")
    rc = p.returncode
    lns = str(po, encoding='utf-8').splitlines()
    lnse = str(pe, encoding='utf-8').split()

    if debug_solver:
        print('\n'.join(lns), file=sys.stderr)
        print(cnf, file=sys.stderr)
        print(lns)

    if rc == 10:
        if print_model:
            encoder.print_model(get_model(lns))
        print("SAT")
        encoder.print_solution(get_model(lns))
        encoder.show_solution(get_model(lns))

    elif rc == 20:
        print("UNSAT")
    else:
        print("ERROR: something went wrong with the solver")

    print('Time:', elapsed)
