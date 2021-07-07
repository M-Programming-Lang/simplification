# ops: sin, cos, tan, ^, *, +, -, /, sec, csc, cot
# https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.657.2478&rep=rep1&type=pdf
# prefix "-" -> node("-", val); infix "-" -> node("-", plus_val, minus_val)
# leaves: "1", "2", "3", ..., "pi", "x", "y", "z"

# see:
# 0. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L1650
# 1. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L1555
# 2. https://github.com/sympy/sympy/blob/53017ff6aee002cf59620592c559f73d522503a0/sympy/simplify/fu.py#L1059

from math import pi

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
        return get_infix(self)

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

def count_trig_ops(graph):  # count trig operations in graph
    if type(graph) == str:
        return 0
    return (graph.op not in ["+", "-", "*", "/", "^"]) + sum(count_trig_ops(i) for i in graph.vals)

def check_operator(graph, op):  # check if an operator is present in the graph
    if type(graph) == str:
        return False
    if graph.op == op:
        return True
    return any(check_operator(i, op) for i in graph.vals)

def negative_to_infix(graph):  # convert a + (-b) to a - b
    if type(graph) == str:
        return graph
    if graph in [node("+", "_", node("-", "_")), node("+", node("-", "_"), "_")]:
        idx = 0
        if type(graph.vals[0]) != str and graph.vals[0].op == "-" and len(graph.vals[0].vals) == 1:
            idx = 1
        return node("-", negative_to_infix(graph.vals[idx]), negative_to_infix(graph.vals[abs(idx-1)].vals[0]))
    return node(graph.op, *[negative_to_infix(i) for i in graph.vals])

def double_neg(graph):
    if type(graph) == str:
        return graph
    if graph == node("-", node("-", "_")):
        return double_neg(graph.vals[0].vals[0])
    if graph == node("-", "_", node("-", "_")):
        return double_neg(node("+", graph.vals[0], graph.vals[1].vals[0]))
    return node(graph.op, *[double_neg(i) for i in graph.vals])

def TR0(graph):
    # remember to convert prefix - to infix - and 0 - x to -x
    return graph

def TR1(graph):  # replace sec and cosec

    if type(graph) == str:
        return graph

    if graph.op == "csc":
        return node("/", "1", node("sin", TR1(graph.vals[0])))
    if graph.op == "sec":
        return node("/", "1", node("cos", TR1(graph.vals[0])))
    return node(graph.op, *[TR1(i) for i in graph.vals])


def TR2(graph):
    return graph

def TR3(graph):  # e.g. sin(-x) -> -sin(x)

    if type(graph) == str:
        return graph

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


def TR4(graph):  # special angles

    if type(graph) == str:
        return graph

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

def TR12(graph):  # tan sum formula (TODO: handle tan(x) + (tan(y) + sin(y)) )

    if type(graph) == str:
        return graph

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

def TR13(graph):

    if type(graph) == str:
        return graph

    graph = node(graph.op, *[TR13(i) for i in graph.vals])  # bottom up (TODO: handle tan(a) * (tan(b) / tan(c)) )

    if graph == node("*", node("tan", "_"), node("tan", "_")):
        a, b = graph.vals[0].vals[0], graph.vals[1].vals[0]
        denom = node("tan", node("+", a, b))
        return node("-", "1", node("+", node("/", node("tan", a), denom), node("/", node("tan", b), denom)))
    if graph == node("*", node("cot", "_"), node("cot", "_")):  # can this ever happen ??
        a, b = graph.vals[0].vals[0], graph.vals[1].vals[0]
        denom = node("tan", node("+", a, b))
        return node("+", "1", node("+", node("/", node("cot", a), denom), node("/", node("cot", b), denom)))

    return graph

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