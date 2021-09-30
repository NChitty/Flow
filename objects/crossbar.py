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

        # Variables for pathfinding algorithm
        self.src_queue = []
        self.dest_queue = []
        # List of visited nodes
        self.src_visited = {}
        self.dest_visited = {}
        # List list of parent nodes
        self.src_parent = {}
        self.dest_parent = {}

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
        return True if ((variable.value and not self.variable_negation[connection.position][variable])
                        or
                        (not variable.value and self.variable_negation[connection.position][variable])) \
            else False

    def evaluate(self, bool_list):
        # Create graph if not already created
        if len(self.graph) == 0:
            self.create_graph()
        # Set values of all variables
        if len(bool_list) != len(self.id_variable):
            print('Length of input and number of variables do not match')
        else:
            for x in range(len(bool_list)):
                self.id_variable[x + 1].value = bool_list[x]
            # Initialize variables
            for key in self.graph.keys():
                self.src_visited[self.graph[key]] = False
                self.src_visited[self.graph[key]] = False
                self.src_parent[self.graph[key]] = None
                self.dest_parent[self.graph[key]] = None
            return self.bidirectional_search()

    def bfs(self, direction='forward'):
        # Breadth first search in forward direction
        if direction == 'forward':
            current = self.src_queue.pop(0)
            for connection in current.connections:
                vertex = connection.node if self.allow_connection(connection) else None

                if vertex is not None:
                    if not self.src_visited[vertex]:
                        self.src_queue.append(vertex)
                        self.src_visited[vertex] = True
                        self.src_parent = current
        # Breadth first search in reverse direction
        else:
            current = self.dest_queue.pop(0)
            for connection in current.connections:
                vertex = connection.node if self.allow_connection(connection) else None

                if vertex is not None:
                    if not self.dest_visited.get(vertex, False):
                        self.dest_queue.append(vertex)
                        self.dest_visited[vertex] = True
                        self.dest_parent = current

    def is_intersection(self):
        for key in self.src_visited:
            if self.src_visited[key] and self.dest_visited[key]:
                return key
        return False

    def bidirectional_search(self):
        # we are always trying to get from R0 to Rx
        # x is always the rows - 1
        src = self.graph["R0"]
        self.src_queue.append(src)
        self.src_visited[src] = True
        self.src_parent[src] = -1

        dest = self.graph[f"R{self.rows-1}"]
        self.dest_queue.append(dest)
        self.dest_visited[src] = True
        self.dest_parent[dest] = -1

        while self.src_queue and self.dest_queue:
            self.bfs('forward')
            self.bfs('backward')

            intersecting_node = self.is_intersection()

            if intersecting_node != -1:
                return True

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
        init_lines = [crossbar_file.readline(), crossbar_file.readline(), crossbar_file.readline()]
        variables = None
        rows = None
        cols = None
        x = 0
        for line in init_lines:
            label = line.split(" ")
            if len(label) > 1:
                if label[0] == "vars":
                    variables = int(label[1])
                elif label[0] == "rows":
                    rows = int(label[1])
                else:
                    cols = int(label[1])
            else:
                if label[0] == "vars":
                    variables = int(label[1])
                elif x == 1:
                    rows = int(label[0])
                else:
                    cols = int(label[0])
            x += 1
        crossbar = Crossbar(rows, cols, variables)
        for x in range(rows):
            line = crossbar_file.readline()
            cols = line.split(" ")
            for y in range(len(cols)):
                if 0 < abs(int(cols[y])) < 99:
                    if crossbar.id_variable.get(abs(int(cols[y])), None) is None:
                        variable = Variable(abs(int(cols[y])))
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
        return crossbar


class GraphNode:
    def __init__(self, node_id):
        self.id = node_id
        self.connections = []


class Connection:
    def __init__(self, node, condition: int = None, position=None):
        self.node = node
        self.condition = condition
        self.position = position
