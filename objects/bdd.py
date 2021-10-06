from objects.crossbar import Crossbar
from objects.variables import Variable


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.left_child_node = None
        self.right_child_node = None
        self.decision_variable = None
        self.terminal_node = False


class BDD:
    def __init__(self, nodes):
        self.nodes = nodes
        self.variables = {}

    def print(self):
        print(f'vars {len(self.variables)}')
        print(f'nodes {len(self.nodes)}')
        for node_key in self.nodes.keys:
            node = self.nodes[node_key]
            if type(node.decision_variable) is Variable:
                print(
                    f'{node.node_id} {node.left_child_node.id} {node.right_child_node.id} {node.decision_variable.id}'
                    )
            else:
                print(f'{node.node_id} {node.left_child_node} {node.right_child_node} {node.terminal_node}')

    def evaluate(self, bool_list):
        if len(bool_list) > len(self.variables):
            print('(BDD) Number of variables does not match the number of inputs')
            return False
        else:
            for x in range(1, len(bool_list) + 1):
                self.variables[x].value = bool_list[x - 1]
        node = self.nodes[1]
        while type(node.terminal_node) is bool:
            if node.decision_variable.value:
                node = node.left_child_node
            else:
                node = node.right_child_node
        return True if node.terminal_node == 1 else False

    def enumeration_verification(self, xbar: Crossbar):
        for x in range(pow(2, len(self.variables))):
            ones = format(x, f'0{len(self.variables)}b')
            bool_list = []
            for y in range(len(ones)):
                bool_list.append(True if int(ones[y]) == 1 else False)
            if not (self.evaluate(bool_list) == xbar.evaluate(bool_list)):
                return False
        return True

    def truth_table(self):
        for x in range(len(self.variables)):
            print(f'{("x_" + str(x+1)):3}|', end='')
        print(f'{"f":3}')
        for x in range(pow(2, len(self.variables))):
            ones = format(x, f'0{len(self.variables)}b')
            bools = []
            for y in range(len(ones)):
                bools.append(True if int(ones[y]) == 1 else False)
                print(f'{str(1 if bools[y] else 0):>3}|', end='')
            print(f'{str(1 if self.evaluate(bools) else 0):3}')

    def synthesize_xbar(self):
        # Start at initial node
        # place variable at (0,0)
        # on 1 place variable at (1,0)
        # on 0 place variable at (0,1) terminal conditions apply
        # (SC1) there is a variable above
        # while unvisited nodes:
            # if row is odd:
                # on 1 place variable at (r, c+1)
                # on 0 place variable at (r+1, c) (SC1)
                # if variable goes to 1
                    # on 1, place 1 in last col with last row 1 (SC1)
                    # on 0, place 1 in last row (SC1)
                # if variable goes to 0
                    # on 1, fill rows with 0s
                    # on 0, place 0s on all rows below
            # if row is even:
                # on 1 place variable at (r+1, c) (SC1)
                # on 0 place variable at (r, c+1)
                # if variable goes to 1
                    # on 1, place 1 on last row beneath variable (SC1)
                    # on 0, go to odd row and place on 1
                # if variable goes to 0
                    # on 1, place 0s on all rows below
                    # on 0, fill row with zeros
            # (SC1):
                # shift right by adding a 99 in col and 0 for all rows after (odd)
                # shift down by adding 1 above and padding with 0s (even)
        pass

    @staticmethod
    def read_bdd(file):
        bdd_file = open(file, "r")
        vars_line = bdd_file.readline()
        nodes_line = bdd_file.readline()
        label = vars_line.split(" ")
        nodes = None
        if len(label) > 1:
            if label[0] == "nodes":
                nodes = int(label[1])
        else:
            nodes = int(nodes_line)
        label = nodes_line.split(" ")
        if len(label) > 1:
            if label[0] == "nodes":
                nodes = int(label[1])
        bdd = BDD({})
        for x in range(1, nodes + 1):
            bdd.nodes.update({x: Node(x)})
        for x in range(nodes):
            line = bdd_file.readline()
            ints = line.split(" ")
            node = bdd.nodes[int(ints[0])]
            if int(ints[1]) == -1 and int(ints[2]) == -1:
                node.left_child_node = int(ints[1])
                node.right_child_node = int(ints[2])
                node.terminal_node = int(ints[3])
                node.decision_variable = node.terminal_node
            else:
                if bdd.variables.get(int(ints[3]), None) is None:
                    variable = Variable(variable_id=int(ints[3]))
                    bdd.variables.update({int(ints[3]): variable})
                else:
                    variable = bdd.variables[int(ints[3])]
                node.left_child_node = bdd.nodes[int(ints[1])]
                node.right_child_node = bdd.nodes[int(ints[2])]
                node.decision_variable = variable
        bdd_file.close()
        return bdd
