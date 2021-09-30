from objects.bdd import Node, BDD
from objects.crossbar import Crossbar

##################### Task 1 (The Crossbar Format) #####################
print("(Crossbar) Enter file name: ", end='')
filename = input()
crossbar = Crossbar.read_crossbar(filename)
crossbar.print_matrix()
crossbar.create_graph()
print(crossbar.evaluate([False, False, True, False]))
