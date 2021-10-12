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
    for x in range(1, no_of_tests+1):
        xbar = Crossbar.read_crossbar(f"xbars/test{x}.xbar")
        print(f"{x:4}|{'True' if bdd.enumeration_verification(xbar) else 'False':10}")

def lone_equivalence_test(bdd_file, xbar_file):
    bdd = BDD.read_bdd(bdd_file)
    xbar = Crossbar.read_crossbar(xbar_file)
    if not bdd.enumeration_verification(xbar):
        print("-----------------------------BDD Truth Table-----------------------------")
        bdd.truth_table()
        print("-----------------------------XBar Truth Table-----------------------------")
        xbar.truth_table()
        return
    print(True)

#test_equivalence(5)
performance_comparison(2)
#performance_comparison(5)
#performance_comparison(10)
#performance_comparison(15)
bdd = BDD.read_bdd("bdd.test")
xbar = bdd.synthesize_xbar()
print(bdd.enumeration_verification(xbar))