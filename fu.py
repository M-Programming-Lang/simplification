# ops: sin, cos, tan, ^, *, +, -, /, sec, csc, cot
# https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.657.2478&rep=rep1&type=pdf

# see:
# 0. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L1650
# 1. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L1555
# 2. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L210

class node:
    def __init__(self, op, *vals):
        self.op, self.vals = op, vals

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

    return ""

def count_trig_ops(graph):  # count trig operations in graph
    if type(graph) == str:
        return 0
    return graph.op not in ["+", "-", "*", "/", "^"] + sum(count_ops(i) for i in graph.vals)

def check_operator(graph, op):  # check if an operator is present in the graph
    if type(graph) == str:
        return False
    if graph.op == op:
        return True
    return any(check_operator(i, op) for i in graph.vals)

def TR0(graph):
    return ""

def TR1(graph):  # replace sec and cosec

    if type(graph) == str:
        return graph

    if graph.op == "csc":
        return node("/", "1", node("sin", TR1(graph.vals[0])))
    if graph.op == "sec":
        return node("/", "1", node("cos", TR1(graph.vals[0])))
    return node(graph.op, *[TR1(i) for i in graph.vals])


def TR2(graph):
    return ""
def TR3(graph):
    return ""

def TR4(graph):  # special angles

    if type(graph) == str:
        return graph

    if graph.op in ["cos", "sin", "tan"]:
        if graph.vals[0] == "0":
            if graph.op in ["sin", "tan"]:
                return "0"
            if graph.op == "cos":
                return "1"
        if type(graph.vals[0]) != str:
            if graph.vals[0].op == "/" and graph.vals[0].vals[0] == "pi":
                if graph.vals[0].vals[1] == "6":
                    if graph.op == "sin": return node("/", "1", "2")
                    if graph.op == "cos": return node("/", node("^", "3", node("/", "1", "2")), "2")
                    if graph.op == "tan": return node("/", node("^", "3", node("/", "1", "2")), "3")
                if graph.vals[0].vals[1] == "4":
                    if graph.op == "sin": return node("/", node("^", "2", node("/", "1", "2")), "2")
                    if graph.op == "cos": return node("/", node("^", "2", node("/", "1", "2")), "2")
                    if graph.op == "tan": return "1"
                if graph.vals[0].vals[1] == "3":
                    if graph.op == "sin": return node("/", node("^", "3", node("/", "1", "2")), "2")
                    if graph.op == "cos": return node("/", "1", "2")
                    if graph.op == "tan": return node("^", "3", node("/", "1", "2"))
                if graph.vals[0].vals[1] == "2":
                    if graph.op == "sin": return "1"
                    if graph.op == "cos": return "0"

    return node(graph.op, *[TR4(i) for i in graph.vals])


def TR5(graph):
    return ""
def TR6(graph):
    return ""
def TR7(graph):
    return ""
def TR8(graph):
    return ""
def TR9(graph):
    return ""
def TR10(graph):
    return ""
def TR11(graph):
    return ""
def TR12(graph):
    return ""
def TR13(graph):
    return ""
def CTR1(graph):
    return ""
def CTR2(graph):
    return ""
def CTR3(graph):
    return ""
def CTR4(graph):
    return ""

def RL1(graph):
    for TrigExpr in [TR4, TR3, TR4, TR12, TR4, TR13, TR4, TR0]:
        graph = TrigExpr(graph)
    return 

def RL2(graph):
    return ""

def get_rpn(graph):  # for printing the graph in reverse polish notation
    if type(graph) == str:
        return graph
    else:
        return " ".join([get_rpn(i) for i in graph.vals]) + " " + graph.op

def get_infix(graph, parens=False):  # for printing the graph with normal notation
    if type(graph) == str:
        return graph
    else:
        if len(graph.vals) == 1:
            return graph.op + "(" + get_infix(graph.vals[0], parens) + ")"
        if parens:
            return "(" + get_infix(graph.vals[0], True) + ") " + graph.op + " (" + get_infix(graph.vals[1], True) + ")"
        return get_infix(graph.vals[0]) + " " + graph.op + " " + get_infix(graph.vals[1])

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