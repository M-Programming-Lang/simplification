from math import pi

class node:
    def __init__(self, op, *vals):
        self.op, self.vals = op, vals

    def __eq__(self, graph):  # does not handle commutativity
        if type(graph) == str:
            if graph == "_":
                return True
            return False
        if len(graph.vals) != len(self.vals):
            return False
        return graph.op == self.op and all(["_" in [str(a), str(b)] or a == b for a, b in zip(self.vals, graph.vals)])

def TR3(graph):  # e.g. sin(-x) -> -sin(x)

    if type(graph) == str:
        return graph

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
                
    return node(graph.op, *[TR3(i) for i in graph.vals])

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

print(get_infix(node("sin", node("-", "x"))), "=", get_infix(TR3(node("sin", node("-", "x")))))  # -sin(x)
print(get_infix(node("sin", node("-", "pi", "x"))), "=", get_infix(TR3(node("sin", node("-", "pi", "x")))))  # sin(x)
print(get_infix(node("sin", node("+", node("*", "2", "pi"), "x"))), "=",
      get_infix(TR3(node("sin", node("+", node("*", "2", "pi"), "x")))))  # sin(x)