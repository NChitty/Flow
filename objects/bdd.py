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
            print('Number of variables does not match the number of inputs')
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

    def truthtable(self):
        for x in range(len(self.variables)):
            print(f'{("x_" + str(x)):3}|', end='')
        print(f'{"f":3}')
        for x in range(pow(2, len(self.variables))):
            ones = format(x, '04b')
            bools = []
            for y in range(len(ones)):
                bools.append(True if int(ones[y]) == 1 else False)
                print(f'{str(1 if bools[y] else 0):>3}|', end='')
            print(f'{str(1 if self.evaluate(bools) else 0):3}')

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
