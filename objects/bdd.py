from enum import Enum

from objects.crossbar import Crossbar, convert_matrix
from objects.variables import Variable


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.left_child_node: Node = None
        self.right_child_node: Node = None
        self.decision_variable: Variable = None
        self.terminal_node = False


def read_bdd(file):
    bdd_file = open(file, "r")
    print(f"Opened {file}, creating...")
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
    bdd = BDD(file, {})
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
    print("Finished reading bdd")
    return bdd


def minimize_matrix(matrix):
    # search rows first
    rows = len(matrix)
    x = 0
    while x < rows:
        flag = True
        for y in range(len(matrix[x])):
            if matrix[x][y] != 0:
                flag = False
                break
        if flag:
            rows -= 1
            matrix.pop(x)
            continue
        x += 1
    cols = len(matrix[rows - 1])
    y = 0
    # search cols
    while y < cols:
        flag = True
        for x in range(len(matrix)):
            if matrix[x][y] != 0:
                flag = False
                break
        if flag:
            for x in range(len(matrix)):
                matrix[x].pop(y)
            cols -= 1
            continue
        y += 1
    return matrix


class BDD:
    def __init__(self, file, nodes):
        self.file = file
        self.nodes = nodes
        self.variables = {}

    def print(self):
        print(f'vars {len(self.variables)}')
        print(f'nodes {len(self.nodes)}')
        for node_key in self.nodes.keys():
            node = self.nodes[node_key]
            if type(node.decision_variable) is Variable:
                print(
                    f'{node.node_id} {node.left_child_node.node_id} '
                    f'{node.right_child_node.node_id} {node.decision_variable.id}'
                )
            else:
                print(f'{node.node_id} {node.left_child_node} '
                      f'{node.right_child_node} {node.terminal_node}')

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
        val_list = []
        for x in range(pow(2, len(self.variables))):
            ones = format(x, f'0{len(self.variables)}b')
            bool_list = []
            for y in range(len(ones)):
                bool_list.append(True if int(ones[y]) == 1 else False)
            bdd_eval = self.evaluate(bool_list)
            xbar_eval = xbar.evaluate(bool_list)
            if bdd_eval != xbar_eval:
                bool_list.append(bdd_eval)
                bool_list.append(xbar_eval)
                val_list.append(bool_list)
        return val_list

    def truth_table(self):
        for x in range(len(self.variables)):
            print(f'{("x_" + str(x + 1)):3}|', end='')
        print(f'{"f":3}')
        for x in range(pow(2, len(self.variables))):
            ones = format(x, f'0{len(self.variables)}b')
            bools = []
            for y in range(len(ones)):
                bools.append(True if int(ones[y]) == 1 else False)
                print(f'{str(1 if bools[y] else 0):>3}|', end='')
            print(f'{str(1 if self.evaluate(bools) else 0):3}')

    def synthesize_xbar(self, file):
        # Create matrix a nodes x nodes matrix
        matrix = [[0 for x in range(len(self.nodes))] for y in range(len(self.nodes))]
        current = self.nodes[1]
        row = 0
        col = 0
        visited = [False] * len(self.nodes)
        self.synthesis_helper(current, True, row, col, visited, matrix)
        minimize_matrix(matrix)
        xbar = convert_matrix(matrix, len(self.variables))
        xbar.file = file
        return xbar

    def synthesis_helper(self, current: Node, horizontal: bool, row, col, visited, matrix):
        visited[current.node_id - 1] = True
        if current.terminal_node == 1 or current.terminal_node == 0 and current.terminal_node is not False:
            matrix[current.node_id - 1][current.node_id - 1] = 99
            return
        if horizontal:
            matrix[row][current.left_child_node.node_id - 1] = current.decision_variable.id
            matrix[row][current.right_child_node.node_id - 1] = -1 * current.decision_variable.id
            self.synthesis_helper(current.left_child_node, False, row, current.left_child_node.node_id - 1, visited,
                                  matrix)
            self.synthesis_helper(current.right_child_node, False, row, current.right_child_node.node_id - 1, visited,
                                  matrix)
        else:
            matrix[current.left_child_node.node_id - 1][col] = current.decision_variable.id
            matrix[current.right_child_node.node_id - 1][col] = -1 * current.decision_variable.id
            self.synthesis_helper(current.left_child_node, True, current.left_child_node.node_id - 1, col, visited,
                                  matrix)
            self.synthesis_helper(current.right_child_node, True, current.right_child_node.node_id - 1, col, visited,
                                  matrix)
