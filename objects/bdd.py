from objects.crossbar import Crossbar
from objects.variables import Variable


class Node:
    def __init__(self, node_id):
        self.node_id = node_id
        self.left_child_node: Node = None
        self.right_child_node: Node = None
        self.decision_variable: Variable = None
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
        # Create matrix with rows = number of nodes - 1
        # Cols = number of nodes - 1
        matrix = [[0 for x in range(len(self.nodes))] for y in range(len(self.nodes))]
        # place 99 in bottom right position
        matrix[-1][-1] = 99
        visited = [False] * len(self.nodes)
        current = self.nodes[1]
        row = 0
        col = 0
        reserved = []
        while False in visited:
            self.synthesis_helper(current, visited, matrix, row, col, reserved)
        xbar = Crossbar.convert_matrix(matrix, len(self.variables))
        return xbar

    def synthesis_helper(self, current: Node, visited, matrix, row, col, reserved):
        # do not try to process terminal nodes
        if current.right_child_node == -1 or current.left_child_node == -1:
            return
        # If there is no unvisited node continue
        if False not in visited:
            return
        visited[current.node_id - 1] = True
        # Place variable in row, col
        while (row, col) in reserved:
            col = col + 1
        if col <= len(matrix[row])-1:
            matrix[row][col] = current.decision_variable.id
        else:
            for r in range(len(matrix)):
                matrix[r].append(0)
        matrix[row][col] = current.decision_variable.id
        reserved.append((row, col))
        if current.left_child_node.terminal_node is False:
            # if node goes to another node, place 99 immediately below and variable to right on 1
            matrix[current.left_child_node.node_id - 1][col] = 99
            reserved.append((current.left_child_node.node_id - 1, col))
            self.synthesis_helper(
                current.left_child_node,
                visited,
                matrix,
                current.left_child_node.node_id - 1,
                col + 1,
                reserved
            )
        else:
            # if node goes to terminal node
            visited[current.left_child_node.node_id - 1] = True
            # if node goes to 0 on 1
            if current.left_child_node.terminal_node == 0:
                # place 0s in all rows below in same col
                for x in range(row + 1, len(matrix)):
                    reserved.append((x, col))
                    matrix[x][col] = 0
            # if node goes to 1 on 1
            if current.left_child_node.terminal_node == 1:
                # place 99 in same col underneath current
                matrix[-1][col] = 99
                reserved.append((len(matrix) - 1, col))
        if current.right_child_node.terminal_node is False:
            # if node goes to another node, place not variable to right and variable immediately below on 0
            col = col + 1
            matrix[row][col] = -1 * current.decision_variable.id
            reserved.append((row, col))
            matrix[current.right_child_node.node_id-1][col] = 99
            self.synthesis_helper(
                current.right_child_node,
                visited,
                matrix,
                current.right_child_node.node_id - 1,
                col + 1,
                reserved
            )
        else:
            visited[current.right_child_node.node_id - 1] = True
            # if node goes to 0 on 0
            if current.right_child_node.terminal_node == 0:
                # place 0s in row
                for y in range(col + 1, len(matrix[row])):
                    reserved.append((row, y))
                    matrix[row][y] = 0
            # if node goes to 1 on 0
            if current.right_child_node.terminal_node == 1:
                # negate variable and place 99 in last row in same col
                reserved.append((row, len(matrix[row]) - 1))
                matrix[row][-1] = 99
        return

    def fix_reserved(self,  row, col, reserved, matrix):
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


