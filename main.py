import time

from objects.bdd import BDD, read_bdd
from objects.crossbar import Crossbar, read_crossbar


def performance_comparison_enumeration(n_vars):
    bdd = read_bdd(f"bdds/var{n_vars}.bdd")
    xbar = read_crossbar(f"xbars/var{n_vars}.xbar")
    start = time.process_time_ns()
    print(f"{n_vars} Variables: {bdd.enumeration_verification(xbar)}")
    end = time.process_time_ns()
    print(f"\t\t{(end - start) / 1000.0}ms")


def performance_comparison_synthesis(n_vars):
    bdd = read_bdd(f"bdds/var{n_vars}.bdd")
    start = time.process_time_ns()
    xbar = bdd.synthesize_xbar()
    end = time.process_time_ns()
    print(f"Nodes {len(bdd.nodes)}: {(end-start)/1000.0}ms")


def test_equivalence(no_of_tests):
    bdd = read_bdd("bdds/var5.bdd")
    print(f"{'Test':4}|Equivalent")
    for x in range(1, no_of_tests + 1):
        xbar = read_crossbar(f"xbars/test{x}.xbar")
        print(f"{x:4}|{'True' if bdd.enumeration_verification(xbar) == 0 else 'False':10}")


def lone_equivalence_test(bdd_in, xbar_in):
    if type(bdd_in) is BDD:
        bdd = bdd_in
    else:
        bdd = read_bdd(bdd_in)
    if type(xbar_in) is Crossbar:
        xbar = xbar_in
    else:
        xbar = read_crossbar(xbar_in)
    value_list = bdd.enumeration_verification(xbar)
    if value_list:
        for x in range(len(bdd.variables)):
            print(f'{("x_" + str(x+1)):4}|', end='')
        print(f'{"bdd":4}|{"xbar":4}|')
        for x in value_list:
            for y in x:
                print(f'{1 if y else 0:4}|', end='')
            print()
        return
    print(True)


def synthesis_test(bdd_file):
    bdd = read_bdd(bdd_file)
    xbar = bdd.synthesize_xbar()
    if not len(bdd.enumeration_verification(xbar)) == 0:
        string = bdd_file
        print(f"Creating synthesized xbar file @ xbars/{string.split('/')[1].split('.')[0]}_synthesis.xbar")
        xbar.fprint_matrix(f"xbars/{string.split('/')[1].split('.')[0]}_synthesis.xbar")
    else:
        print("Synthesis: Success.")


def synthesize_xbar(bdd_file):
    bdd = read_bdd(bdd_file)
    xbar = bdd.synthesize_xbar()
    string = bdd_file
    print(f"Creating synthesized xbar file @ xbars/{string.split('/')[1].split('.')[0]}_synthesis.xbar")
    xbar.fprint_matrix(f"xbars/{string.split('/')[1].split('.')[0]}_synthesis.xbar")


if __name__ == "__main__":
    xbar = read_crossbar("xbars/var2.xbar")
    xbar.truth_table()
    bdd = read_bdd(("bdds/var2.bdd"))
    bdd.truth_table()
