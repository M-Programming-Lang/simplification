from itertools import combinations, chain

# WRAPPERS

def return_strings(func):  # wrapper to return graph if graph is string
    def rs_function(graph, *args):
        if type(graph) == str:
            return graph
        return func(graph, *args)
    return rs_function

def prefix_minus_to_value(func):  # convert node("-", "1") to "-1" as wrapper (to go ahead of associative_cases)

    @return_strings
    def convert_vals(graph):
        if graph == node("-", "_", "_"):
            graph = node("+", graph.vals[0], node("-", graph.vals[1]))
        if graph == node("-", "_") and type(graph.vals[0]) == str and graph.vals[0] not in ["x", "y", "z", "pi"]:
            return "-" + graph.vals[0]
        return node(graph.op, *[convert_vals(i) for i in graph.vals])

    def pmtv_function(graph, *args):
        return func(convert_vals(graph))

    return pmtv_function
        

def associative_cases(*operations):  # function wrapper to call function on graphs that nest nodes in different ways to get same outputs
    '''
    examples:
     - graph -> list of graphs to call wrapped function on
     - (1 + 2) + 3 -> ((1 + 2) + 3, 1 + (2 + 3), (1 + 3) + 2)
     - 5 * (2 / 3) -> (5 * (2 / 3), (5 * 2) / 3, (5 / 3) * 2)
     - (1 + 2) + 5 * (2 / 3) -> (1 + 2) + 5 * (2 / 3), 1 + (2 +
            5 * (2 / 3)), (1 + 5 * (2 / 3)) + 2, (1 + 2) + (5 *
            2) / 3, 1 + (2 + (5 * 2) / 3), (1 + (5 * 2) / 3) +
            2, (1 + 2) + (5 / 3) * 2, 1 + (2 + (5 / 3) * 2), (1
            + (5 / 3) * 2) + 2
    only makes list based around operation given & assumes all operations given to be same precedence
    returns graph with the least nodes
    '''

    def get_graphs(graph, operators):

        if type(graph) == str:
            return [graph]

        if graph.op == "/" and len(graph.vals) == 1:
            return [node("/", i) for i in get_graphs(graph.vals[0], operators)]

        if graph.op not in operators:

            vals = [[]]
            for i in graph.vals:
                graphs = get_graphs(i, operators)
                new_vals = []
                for val in vals:
                    new_vals += [val + [g] for g in graphs]
                vals = new_vals

            return [node(graph.op, *v) for v in vals]

        def get_operands(graph, op):

            if type(graph) == str or graph.op not in op:
                return [graph]

            if graph.op == "/":
                return [i for i in get_operands(graph.vals[0], op)] + [node("/", graph.vals[1])]

            return [j for i in graph.vals for j in get_operands(i, op)]

        def get_all_binary_trees(op, leaves):

            def list_diff(l1, l2):  # computes l1 - l2 but with [1, 2, 2] - [2] = [1, 2] (not [1])
                l1, l2 = list(l1), list(l2)
                for i in l2:
                    l1.remove(i)
                return l1

            if len(leaves) == 1:
                return leaves

            lefts, splits = [], []  # splits is list of ways to split leaves into 2 non-empty sets
            for length in range(1, len(leaves)):
                lefts += list(combinations(leaves, length))

            for left in lefts[:int(len(lefts)/2)]:  # only take first half so dont get both [(a, b), (c, d)] and [(c, d), (a, b)]
                splits.append([left, tuple(list_diff(leaves, left))])

            trees = []
            for left_set, right_set in splits:
                for left in get_all_binary_trees(op, left_set):
                    for right in get_all_binary_trees(op, right_set):
                        trees.append(node(op, left, right))

            return trees

        operands = get_operands(graph, operators)

        vals = [[]]
        for i in operands:
            graphs = get_graphs(i, operators)
            new_vals = []
            for val in vals:
                new_vals += [val + [g] for g in graphs]
            vals = new_vals

        graphs = []
        for g in vals:
            graphs += get_all_binary_trees(operators[0], g)

        if "/" in operators:

            @return_strings
            def remove_prefix_divide(graph, first_call=False):

                graph = node(graph.op, *[remove_prefix_divide(i) for i in graph.vals])

                if graph.op == "*":
                    
                    if graph.vals[0] == node("/", "_"):
                        if graph.vals[1] == node("/", "_"):
                            return node("/", node(graph.vals[0].vals[0], graph.vals[1].vals[0]))
                        return node("/", remove_prefix_divide(graph.vals[1]), remove_prefix_divide(graph.vals[0].vals[0]))

                    if graph.vals[1] == node("/", "_"):
                        return node("/", remove_prefix_divide(graph.vals[0]), remove_prefix_divide(graph.vals[1].vals[0]))

                if first_call and graph.op == "/":
                    graph.vals = ["1", graph.vals[0]]

                return graph

            graphs = [remove_prefix_divide(i, True) for i in graphs]

        return graphs

    def wrapper(simplification):

        def ac_function(graph, *args):  # O(lots)

            if len(operations) > 1 and "+" in operations:
                simplified_graphs, new_operations = [], [i for i in operations if i != "+"]
                for new_graph in get_graphs(graph, ["+"]):
                    simplified_graphs += [simplification(g, *args) for g in get_graphs(new_graph, new_operations)]
            else:
                simplified_graphs = [simplification(g, *args) for g in get_graphs(graph, operations)]
            # simplified_graphs is a list of (graph, no. changes)
            return min(simplified_graphs, key=lambda x : (-x[1], count_ops(x[0])))[0]  # only return the graph

        return ac_function
    return wrapper
    
# NODE

class node:
    def __init__(self, op, *vals):
        self.op, self.vals = op, vals
        self.changes = 0

    def __eq__(self, graph):  # does not handle commutativity or "_" == "x" (obvs)
        if type(graph) == str:
            if graph == "_":
                return True
            return False
        if len(graph.vals) != len(self.vals):
            return False
        return graph.op == self.op and all(["_" in [str(a), str(b)] or a == b for a, b in zip(self.vals, graph.vals)])

    def __lt__(self, graph):
        return hash(self) < hash(graph)  # just needs to be consistent not logical

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"node({self.op}, {', '.join([str(i) for i in self.vals])})"
        #return get_infix(self)

@return_strings
def get_rpn(graph):  # for printing the graph in reverse polish notation
    return " ".join([get_rpn(i) for i in graph.vals]) + " " + graph.op

@return_strings
def get_infix(graph, parens=False):  # for printing the graph with normal notation
    if len(graph.vals) == 1:
        if graph.op == "-":
            return "-" + get_infix(graph.vals[0], parens)
        return graph.op + "(" + get_infix(graph.vals[0], parens) + ")"
    if parens:
        return "(" + get_infix(graph.vals[0], True) + ") " + graph.op + " (" + get_infix(graph.vals[1], True) + ")"
    return get_infix(graph.vals[0]) + " " + graph.op + " " + get_infix(graph.vals[1])

def commutative_eq(g1, g2):
    if type(g1) == str:
        if g1 == "_":
            return True
        return False
    if len(g1.vals) != len(g2.vals):
        return False
    if g1.op in ["*", "+"]:
        return g1.op == g2.op and all(["_" in [str(a), str(b)] or a == b for a, b in zip(sorted(g2.vals), sorted(g1.vals))])
    return g1.op == g2.op and all(["_" in [str(a), str(b)] or a == b for a, b in zip(g2.vals, g1.vals)])

@associative_cases("+", "*", "/")
def associative_eq(g1, g2):  # also handles commutativity
    eq = commutative_eq(g1, g2)
    return eq, eq  # testing if equal in any case (using True > False)

# OTHER FUNCTIONS

def check_operator(graph, op):  # check if an operator is present in the graph
    if type(graph) == str:
        return False
    if graph.op == op:
        return True
    return any(check_operator(i, op) for i in graph.vals)

@return_strings
def negative_to_infix(graph):  # convert a + (-b) to a - b
    if graph in [node("+", "_", node("-", "_")), node("+", node("-", "_"), "_")]:
        idx = 0
        if type(graph.vals[0]) != str and graph.vals[0].op == "-" and len(graph.vals[0].vals) == 1:
            idx = 1
        return node("-", negative_to_infix(graph.vals[idx]), negative_to_infix(graph.vals[abs(idx-1)].vals[0]))
    return node(graph.op, *[negative_to_infix(i) for i in graph.vals])

@return_strings
def double_neg(graph):  # remove double negatives (e.g. --x -> x)
    if graph == node("-", node("-", "_")):
        return double_neg(graph.vals[0].vals[0])
    if graph == node("-", "_", node("-", "_")):
        return double_neg(node("+", graph.vals[0], graph.vals[1].vals[0]))
    return node(graph.op, *[double_neg(i) for i in graph.vals])

def count_ops(graph):
    if type(graph) in [str, bool]:  # janky workaround for using assocaitive cases with bools
        return 0
    return 1 + sum(count_ops(i) for i in graph.vals)

def count_trig_ops(graph):
    if type(graph) in [str, bool]:  # and again
        return 0
    return (graph.op not in ["+", "-", "*", "/", "^"]) + sum(count_trig_ops(i) for i in graph.vals)