# ops: sin, cos, tan, ^, *, +, -, /, sec, csc, cot
# https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.657.2478&rep=rep1&type=pdf
# prefix "-" -> node("-", val); infix "-" -> node("-", plus_val, minus_val)
# leaves: "1", "2", "3", ..., "pi", "x", "y", "z"

# see:
# 0. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L1650
# 1. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L1555
# 2. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L31

from simplify_polynomial import *
from math import pi
from itertools import combinations, chain

class node:
    def __init__(self, op, *vals):
        self.op, self.vals = op, vals

    def __eq__(self, graph):  # does not handle commutativity or "_" == "x" (obvs)
        if type(graph) == str:
            if graph == "_":
                return True
            return False
        if len(graph.vals) != len(self.vals):
            return False
        return graph.op == self.op and all(["_" in [str(a), str(b)] or a == b for a, b in zip(self.vals, graph.vals)])

    def __repr__(self):
        return f"node({self.op}, {', '.join([str(i) for i in self.vals])})"
        #return get_infix(self)

terms = [
    "1",  # 1
    node("/", node("^", node("sin", node("*", "2", "x")), "2"), "4"),  # sin^2(2x)/4
    node("^", node("sin", "y"), "2"),  # sin^2(y)
    node("^", node("cos", "x"), "4")  # cos^4(x)
]

test = node("-", terms[0], node("+", terms[1], node("+", terms[2], terms[3])))  # 1 - sin^2(2x)/4 - sin^2(y) - cos^4(x)

def fu(graph):

    if check_operator(graph, "sec") or check_operator(graph, "csc"):
        graph = TR1(graph)

    if check_operator(graph, "tan") or check_operator(graph, "cot"):
        RL1_graph = RL1(graph)

        if count_trig_ops(graph) > count_trig_ops(RL1_graph):  # only apply Rule 1 if it reduces L(graph)
            graph = RL1_graph

        if check_operator(graph, "tan") or check_operator(graph, "cot"):
            graph = TR2(graph)

    graph = TR0(graph)

    if check_operator(graph, "sin") or check_operator(graph, "cos"):
        graph = RL2(graph)

    return graph

def count_trig_ops(graph):
    if type(graph) == str:
        return 0
    return (graph.op not in ["+", "-", "*", "/", "^"]) + sum(count_trig_ops(i) for i in graph.vals)

def count_ops(graph):
    if type(graph) == str:
        return 0
    return 1 + sum(count_trig_ops(i) for i in graph.vals)

def check_operator(graph, op):  # check if an operator is present in the graph
    if type(graph) == str:
        return False
    if graph.op == op:
        return True
    return any(check_operator(i, op) for i in graph.vals)

def return_strings(func):  # wrapper to return graph if graph is string
    def function(graph, *args):
        if type(graph) == str:
            return graph
        return func(graph, *args)
    return function

@return_strings
def negative_to_infix(graph):  # convert a + (-b) to a - b
    if graph in [node("+", "_", node("-", "_")), node("+", node("-", "_"), "_")]:
        idx = 0
        if type(graph.vals[0]) != str and graph.vals[0].op == "-" and len(graph.vals[0].vals) == 1:
            idx = 1
        return node("-", negative_to_infix(graph.vals[idx]), negative_to_infix(graph.vals[abs(idx-1)].vals[0]))
    return node(graph.op, *[negative_to_infix(i) for i in graph.vals])

@return_strings
def double_neg(graph):
    if graph == node("-", node("-", "_")):
        return double_neg(graph.vals[0].vals[0])
    if graph == node("-", "_", node("-", "_")):
        return double_neg(node("+", graph.vals[0], graph.vals[1].vals[0]))
    return node(graph.op, *[double_neg(i) for i in graph.vals])

def associative_cases(operations):  # function wrapper to call function on graphs that nest nodes in different ways to get same outputs
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

            return [j for i in graph.vals for j in get_operands(i, op)]  # ?

        def get_all_binary_trees(op, leaves):
            
            if len(leaves) == 1:
                return leaves


            lefts, splits = [], []  # splits is list of ways to split leaves into 2 non-empty sets
            for length in range(1, len(leaves)):
                lefts += list(combinations(leaves, length))

            for left in lefts[:int(len(lefts)/2)]:  # only take first half so dont get both [(a, b), (c, d)] and [(c, d), (a, b)]
                splits.append([left, tuple([elem for elem in leaves if elem not in left])])

            trees = []
            for left_set, right_set in splits:
                for left in get_all_binary_trees(op, left_set):
                    for right in get_all_binary_trees(op, right_set):
                        trees.append(node(op, left, right))

            return trees

        operands = get_operands(graph, operators)
        graphs = get_all_binary_trees(operators[0], operands)

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

        def new_function(graph):  # O(lots)

            original_graphs = get_graphs(graph, operations)
            simplified_graphs = [simplification(graph) for graph in original_graphs]
            changed = [s for o, s in zip(original_graphs, simplified_graphs) if o != s]
            if not changed:
                return graph
            return min(changed, key=count_ops)  # minimise number of operations if multiple graphs are changed
                                                # TODO: could first pick graph that has had the operation performed
                                                # the most times so operations that make the graph larger (e.g. 
                                                # TR13) are applied as many times as poss when called

        return new_function
    return wrapper

def TR0(graph):
    return simplify_polynomial(graph)

@return_strings
def TR1(graph):  # replace sec and cosec

    if graph.op == "csc":
        return node("/", "1", node("sin", TR1(graph.vals[0])))
    if graph.op == "sec":
        return node("/", "1", node("cos", TR1(graph.vals[0])))
    return node(graph.op, *[TR1(i) for i in graph.vals])


def TR2(graph):
    return graph

@return_strings
def TR3(graph):  # e.g. sin(-x) -> -sin(x)

    graph = node(graph.op, *[TR3(i) for i in graph.vals])
    graph = double_neg(graph)
    graph = negative_to_infix(graph)

    if graph.op in ["sin", "cos", "tan", "cot"]:

        if type(graph.vals[0]) != str:

            v = graph.vals[0]

            if v == node("-", "_"):  # -x
                if graph.op == "cos": return node("cos", v.vals[0])  # cos(-x) = cos(x)
                return node("-", node(graph.op, v.vals[0]))  # sin/tan/cot(-x) = -sin/tan/cot(x)
            if v == node("-", "pi", "_"):  # pi - x
                if graph.op == "sin": return node("sin", v.vals[1])  # sin(pi - x) = sin(x)
                return node("-", node(graph.op, v.vals[1]))  # cos/tan/cot(pi - x) = -cos/tan/cot(pi - x)
            if v in [node("+", "pi", "_"), node("+", "_", "pi")]:  # pi + x
                idx = 0
                if v.vals[0] == "pi":  # dealing with commutativity
                    idx = 1
                if graph.op in ["tan", "cot"]: return node(graph.op, v.vals[idx])  # tan/cot(pi + x) = tan/cot(x)
                return node("-", node(graph.op, v.vals[idx]))  # sin/cos(pi + x) = -sin/cos(x)
            if v in [node("-", node("*", "2", "pi"), "_"), node("-", node("*", "pi", "2"), "_")]:  # 2pi - x (is this not redundant?)
                if graph.op == "cos": return node("cos", v.vals[1])  # cos(2pi - x) = cos(x)
                return node("-", node(graph.op, v.vals[1]))  # sin/tan/cot(2pi - x) = -sin/tan/cot(x)
            if v in [node("+", node("*", "_", "pi"), "_"), node("+", node("*", "pi", "_"), "_")] and \
                    type(v.vals[0].vals[0]) == str == type(v.vals[0].vals[1]) and \
                    eval("*".join(v.vals[0].vals)+"/pi")%2 == 0:  # 2kpi + x (but not x + 2kpi)
                idx = 1
                if v == node("+", node("*", "pi", "_"), "_") and v.vals[0].vals[0] == "pi":
                    idx = 0
                return node(graph.op, v.vals[idx])  # sin/cos/tan/cot(2kpi + x) = sin/cos/tan/cot(x)
            if v in [node("+", "_", node("*", "_", "pi")), node("+", "_", node("*", "pi", "_"))] and \
                    type(v.vals[1].vals[0]) == str == type(v.vals[1].vals[1]) and \
                    eval("*".join(v.vals[1].vals)+"/pi")%2 == 0:  # x + 2kpi
                idx = 1
                if v == node("+", "_", node("*", "pi", "_")) and v.vals[1].vals[0] == "pi":
                    idx = 0
                return node(graph.op, v.vals[idx])  # sin/cos/tan/cot(x + 2kpi) = sin/cos/tan/cot(x)

    return graph

@return_strings
def TR4(graph):  # special angles

    graph = node(graph.op, *[TR4(i) for i in graph.vals])

    if graph.op in ["cos", "sin", "tan"]:
        if graph.vals[0] == "0":
            if graph.op in ["sin", "tan"]: return "0"
            if graph.op == "cos": return "1"

        if graph.vals[0] == node("/", "pi", "6"):
            if graph.op == "sin": return node("/", "1", "2")
            if graph.op == "cos": return node("/", node("^", "3", node("/", "1", "2")), "2")
            if graph.op == "tan": return node("/", node("^", "3", node("/", "1", "2")), "3")

        if graph.vals[0] == node("/", "pi", "4"):
            if graph.op == "sin": return node("/", node("^", "2", node("/", "1", "2")), "2")
            if graph.op == "cos": return node("/", node("^", "2", node("/", "1", "2")), "2")
            if graph.op == "tan": return "1"

        if graph.vals[0] == node("/", "pi", "3"):
            if graph.op == "sin": return node("/", node("^", "3", node("/", "1", "2")), "2")
            if graph.op == "cos": return node("/", "1", "2")
            if graph.op == "tan": return node("^", "3", node("/", "1", "2"))

        if graph.vals[0] == node("/", "pi", "2"):
            if graph.op == "sin": return "1"
            if graph.op == "cos": return "0"

    return graph


def TR5(graph):
    return graph
def TR6(graph):
    return graph
def TR7(graph):
    return graph
def TR8(graph):
    return graph
def TR9(graph):
    return graph
def TR10(graph):
    return graph
def TR11(graph):
    return graph

@return_strings
def TR12(graph):  # tan sum formula

    graph = negative_to_infix(graph)

    if graph == node("tan", node("+", "_", "_")):
        x, y = graph.vals[0].vals
        num = node("+", TR12(node("tan", x)), TR12(node("tan", y)))
        den = node("-", "1", node("*", TR12(node("tan", x)), TR12(node("tan", y))))
        return node("/", num, den)  # tan(x + y) = (tan(x) + tan(y))/(1 - tan(x) * tan(y))
    if graph == node("tan", node("-", "_", "_")):
        x, y = graph.vals[0].vals
        num = node("-", TR12(node("tan", x)), TR12(node("tan", y)))
        den = node("+", "1", node("*", TR12(node("tan", x)), TR12(node("tan", y))))
        return node("/", num, den)  # tan(x - y) = (tan(x) - tan(y))/(1 + tan(x) * tan(y))

    return node(graph.op, *[TR12(i) for i in graph.vals])

@associative_cases(["*", "/"])  # handle tan(a) * (tan(b) / tan(c))
def TR13(graph):

    @return_strings
    def recursive_TR13(graph):

        graph = node(graph.op, *[recursive_TR13(i) for i in graph.vals])  # bottom up

        if graph == node("*", node("tan", "_"), node("tan", "_")):
            a, b = graph.vals[0].vals[0], graph.vals[1].vals[0]
            denom = node("tan", node("+", a, b))
            return node("-", "1", node("+", node("/", node("tan", a), denom), node("/", node("tan", b), denom)))
        if graph == node("*", node("cot", "_"), node("cot", "_")):  # can this ever happen ??
            a, b = graph.vals[0].vals[0], graph.vals[1].vals[0]
            denom = node("tan", node("+", a, b))
            return node("+", "1", node("+", node("/", node("cot", a), denom), node("/", node("cot", b), denom)))

        return graph

    return recursive_TR13(graph)

def CTR1(graph):
    return graph
def CTR2(graph):
    return graph
def CTR3(graph):
    return graph
def CTR4(graph):
    return graph

def RL1(graph):
    for TrigExpr in [TR4, TR3, TR4, TR12, TR4, TR13, TR4, TR0]:
        graph = TrigExpr(graph)
    return 

def RL2(graph):
    return graph

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


if __name__ == "__main__":
    
    print(f"input (RPN):              {get_rpn(test)}")
    print(f"input (infix):            {get_infix(test, True)}")
    print(f"input (infix, no parens): {get_infix(test)}", end="\n\n")

    simplified = fu(test)

    print(f"simplified (RPN):              {get_rpn(simplified)}")
    print(f"simplified (infix):            {get_infix(simplified, True)}")
    print(f"simplified (infix, no parens): {get_infix(simplified)}", end="\n\n")

    target = node("*", node("sin", node("+", "x", "y")), node("sin", node("-", "x", "y")))  # sin(x + y)sin(x - y)

    print(f"target (RPN):              {get_rpn(target)}")
    print(f"target (infix):            {get_infix(target, True)}")
    print(f"target (infix, no parens): {get_infix(target)}")
