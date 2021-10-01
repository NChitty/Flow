from objects.variables import Variable


class Crossbar:
    def __init__(self, rows, cols, n_variables):
        # Variables to store information about crossbar
        self.rows = rows
        self.cols = cols
        self.n_variables = n_variables

        # Variables to store information about graph
        self.id_variable = {}
        self.variable_negation = {}
        self.matrix = {}
        self.graph = {}

    def print_matrix(self):
        print(f'vars {self.n_variables}\nrows {self.rows}\ncols {self.cols}')
        for x in range(self.rows):
            for y in range(self.cols):
                if type(self.matrix[(x, y)]) is Variable:
                    variable = self.matrix[(x, y)]
                    negated = self.variable_negation[(x, y)][variable]
                    print(f'{variable.id if not negated else -1 * variable.id} ', end='')
                else:
                    print(f'{self.matrix[(x, y)]} ', end='')
            print("")

    def fprint_matrix(self, filename):
        save_file = open(filename, "w")
        save_file.writelines(f'vars {self.variable_negation}\nrows {self.rows}\ncols {self.cols}\n')
        for x in range(len(self.matrix)):
            for y in self.matrix[x]:
                if type(self.matrix[(x, y)]) is Variable:
                    variable = self.matrix[(x, y)]
                    if self.variable_negation[variable.id][variable]:
                        save_file.write(f'{-1 * variable.id} ')
                    else:
                        save_file.write(f'{variable.id} ')
                else:
                    save_file.write(f'{self.matrix[(x, y)]} ')
            save_file.writelines("\n")

    def create_graph(self):
        for x in range(self.rows):
            self.graph.update({f'R{x}': GraphNode(f'R{x}')})
        for y in range(self.cols):
            self.graph.update({f'C{y}': GraphNode(f'C{y}')})
        for x in range(self.rows):
            for y in range(self.cols):
                row_node = self.graph[f'R{x}']
                col_node = self.graph[f'C{y}']
                if type(self.matrix[(x, y)]) is Variable:
                    row_node.connections.append(
                        Connection(col_node, self.matrix[(x, y)].id, (x, y))
                    )
                    col_node.connections.append(
                        Connection(row_node, self.matrix[(x, y)].id, (x, y))
                    )
                elif self.matrix[(x, y)] == 99:
                    row_node.connections.append(Connection(col_node))
                    col_node.connections.append(Connection(row_node))

    def allow_connection(self, connection):
        if connection.condition is None:
            return True
        variable = self.id_variable[connection.condition]
        return True if variable.value ^ self.variable_negation[connection.position][variable] else False

    def evaluate(self, bool_list):
        # Create graph if not already created
        if len(self.graph) == 0:
            self.create_graph()
        # Set values of all variables
        if len(bool_list) != self.n_variables:
            print(f'(Crossbar) Length of input and number of variables do not match:\n Inputs: {len(bool_list)}\tVariables: {self.n_variables}')
            return False
        else:
            for x in range(len(bool_list)):
                self.id_variable[x + 1].value = bool_list[x]
            visited = []
            return self.path_exists(self.graph["R0"], self.graph[f"R{self.rows - 1}"], visited)

    def path_exists(self, src, dest, visited):
        self.dfs(src, visited)
        return dest in visited

    def dfs(self, v, visited):
        visited.append(v)
        for connection in v.connections:
            if self.allow_connection(connection) and connection.node not in visited:
                self.dfs(connection.node, visited)

    def truthtable(self):
        for x in range(self.n_variables):
            print(f'{("x_" + str(x)):3}|', end='')
        print(f'{"f":3}')
        for x in range(pow(2, self.n_variables)):
            ones = format(x, f'0{self.n_variables}b')
            bools = []
            for y in range(len(ones)):
                bools.append(True if int(ones[y]) == 1 else False)
                print(f'{str(1 if bools[y] else 0):>3}|', end='')
            print(f'{str(1 if self.evaluate(bools) else 0):3}')

    """
    Prints all the connections of the matrix
    """

    def print_graph(self):
        for key in self.graph:
            node = self.graph[key]
            for connection in node.connections:
                print(f'{node.id}->{connection.node.id}')

    """
    Reads the input file
    :returns the equivalent crossbar matrix from file
    """

    @staticmethod
    def read_crossbar(file):
        crossbar_file = open(file, "r")
        init_lines = crossbar_file.readline()
        variables = None
        rows = None
        cols = None
        x = 0
        if len(init_lines.split(" ")) <= 2:
            label = crossbar_file.readline().split(" ")
            if len(label) > 1:
                if label[0] == "vars":
                    variables = int(label[1])
                elif label[0] == "rows":
                    rows = int(label[1])
                else:
                    cols = int(label[1])
            else:
                variables = int(label[1])
            x = 1
            while x < 2:
                label = crossbar_file.readline().split(" ")
                if len(label) > 1:
                    if label[0] == "vars":
                        variables = int(label[1])
                    elif label[0] == "rows":
                        rows = int(label[1])
                    else:
                        cols = int(label[1])
                else:
                    if x == 1:
                        rows = int(label[0])
                    else:
                        cols = int(label[0])
                x += 1
        else:
            cols = len(init_lines.split(" "))
            rows = len(crossbar_file.read().split("\n"))
            crossbar_file.seek(0)
        crossbar = Crossbar(rows, cols, 0 if variables is None else variables)
        x = 0
        for line in crossbar_file:
            cols = line.split(" ")
            for y in range(len(cols)):
                if 0 < abs(int(cols[y])) < 99:
                    if crossbar.id_variable.get(abs(int(cols[y])), None) is None:
                        variable = Variable(abs(int(cols[y])))
                        crossbar.n_variables += 1 if variables is None else crossbar.n_variables
                        crossbar.id_variable[variable.id] = variable
                    else:
                        variable = crossbar.id_variable[abs(int(cols[y]))]
                    if int(cols[y]) < 0:
                        crossbar.variable_negation.update({(x, y): {variable: True}})
                    else:
                        crossbar.variable_negation.update({(x, y): {variable: False}})
                    crossbar.matrix[(x, y)] = variable
                else:
                    crossbar.matrix[(x, y)] = int(cols[y])
            x = x + 1
        return crossbar


class GraphNode:
    def __init__(self, node_id):
        self.id = node_id
        self.connections = []

    def __repr__(self):
        return self.id


class Connection:
    def __init__(self, node, condition: int = None, position=None):
        self.node = node
        self.condition = condition
        self.position = position
