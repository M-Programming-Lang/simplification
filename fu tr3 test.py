from math import pi

class node:
    def __init__(self, op, *vals):
        self.op, self.vals = op, vals

    def __eq__(self, graph):
        if type(graph) == str:
            return False
        if len(graph.vals) != len(self.vals):
            return False
        return graph.op == self.op and all([a == b for a, b in zip(self.vals, graph.vals)])

def TR3(graph):  # e.g. sin(-x) -> -sin(x)

    if type(graph) == str:
        return graph

    if graph.op in ["sin", "cos", "tan", "cot"]:

        if type(graph.vals[0]) != str:
            if graph.vals[0].op == "-" and len(graph.vals[0].vals) == 1:  # -x
                if graph.op == "cos": return node("cos", graph.vals[0].vals[0])  # cos(-x) = cos(x)
                return node("-", node(graph.op, graph.vals[0].vals[0]))  # sin/tan/cot(-x) = -sin/tan/cot(x)
            if len(graph.vals[0].vals) == 2 and graph.vals[0].vals[0] == "pi" and graph.vals[0].op == "-":  # pi - x
                if graph.op == "sin": return node("sin", graph.vals[0].vals[1])  # sin(pi - x) = sin(x)
                return node("-", node(graph.op, graph.vals[0].vals[1]))  # cos/tan/cot(pi - x) = -cos/tan/cot(pi - x)
            if len(graph.vals[0].vals) == 2 and \
                        graph.vals[0].op == "+" and \
                        "pi" in graph.vals[0].vals:  # pi + x
                idx = 0
                if graph.vals[0].vals[0] == "pi":  # dealing with commutativity
                    idx = 1
                if graph.op in ["tan", "cot"]: return node(graph.op, graph.vals[0].vals[idx])  # tan/cot(pi + x) = tan/cot(x)
                return node("-", node(graph.op, graph.vals[0].vals[idx]))  # sin/cos(pi + x) = -sin/cos(x)
            if len(graph.vals[0].vals) == 2 and \
                        (node("*", "2", "pi") in graph.vals[0].vals or node("*", "pi", "2") in graph.vals[0].vals) and \
                        graph.vals[0].op == "-":  # 2pi - x (is this not redundant?)
                idx = 0
                if node("*", "2", "pi") in graph.vals[0].vals[0] or node("*", "pi", "2") in graph.vals[0].vals[0]:  # commutativity
                    idx = 1
                if graph.op == "cos": return node("cos", graph.vals[0].vals[idx])  # cos(2pi - x) = cos(x)
                return node("-", node(graph.op, graph.vals[0].vals[idx]))  # sin/tan/cot(2pi - x) = -sin/tan/cot(x)
            if len(graph.vals[0].vals) == 2 and \
                        (any([
                            (type(val) != str and val.op == "*" and "pi" in val.vals and eval("*".join(val.vals) + "/pi")%2 == 0)  # check if val is 2kpi ("AND" is not commutative bc eval order)
                            for val in graph.vals[0].vals])) and \
                        graph.vals[0].op == "+":  # 2kpi + x
                idx = 0
                if type(graph.vals[0].vals[0]) != str and graph.vals[0].vals[0].op == "*" and "pi" in graph.vals[0].vals[0].vals and eval("*".join(graph.vals[0].vals[0].vals) + "/pi")%2 == 0:  # commutativity
                    idx = 1
                return node(graph.op, graph.vals[0].vals[idx])  # sin/cos/tan/cot(2kpi + x) = sin/cos/tan/cot(x)
                
    return graph(graph.op, *[TR3(i) for i in graph.vals])

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

# FIRST TRY LETS GOOO
print(get_infix(node("sin", node("-", "x"))), "=", get_infix(TR3(node("sin", node("-", "x")))))  # -sin(x)
print(get_infix(node("sin", node("-", "pi", "x"))), "=", get_infix(TR3(node("sin", node("-", "pi", "x")))))  # sin(x)
print(get_infix(node("sin", node("+", node("*", "2", "pi"), "x"))), "=",
      get_infix(TR3(node("sin", node("+", node("*", "2", "pi"), "x")))))  # sin(x)