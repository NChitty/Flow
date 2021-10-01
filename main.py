import time

from objects.bdd import BDD
from objects.crossbar import Crossbar


def performance_comparison(n_vars):
    bdd = BDD.read_bdd(f"bdds/var{n_vars}.bdd")
    xbar = Crossbar.read_crossbar(f"xbars/var{n_vars}.xbar")
    start = time.process_time_ns()
    print(f"{n_vars} Variables: {bdd.enumeration_verification(xbar)}")
    end = time.process_time_ns()
    print(f"\t\t{(end - start) / 1000.0}ms")


def test_equivalence(no_of_tests):
    bdd = BDD.read_bdd("bdds/var5.bdd")
    print(f"{'Test':4}|Equivalent")
    for x in range(1, no_of_tests):
        xbar = Crossbar.read_crossbar(f"xbars/test{x}.xbar")
        print(f"{x:4}|{'True' if bdd.enumeration_verification(xbar) else 'False':10}")
