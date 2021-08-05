from util import *

def is_computable(graph):  # only supports explicit x/0, not 1/(1*0) for example
    if type(graph) == str:
        return True
    if graph == node("/", "_", "0"):
        return False
    return all([is_computable(i) for i in graph.vals])

def calculate_pfs(value):
    if value == 1: return [value]
    factor, factors = 2, []
    while factor ** 2 <= value:
        if value % factor != 0:
            factor += 1
        else:
            value /= factor
            factors.append(factor)
    if value > 1:
        factors.append(int(value))
    return factors

def to_prime_factors(graph):

    def construct_subtree(vals):
        if len(vals) == 1:
            return str(vals[0])
        return node("*", str(vals[0]), construct_subtree(vals[1:]))
    
    if type(graph) == str and graph not in ["x", "y", "z", "pi"]:
        return construct_subtree(calculate_pfs(int(graph)))  # nasty multiplication will be cleaned up later
            
    if type(graph) != str:
        return node(graph.op, *[to_prime_factors(i) for i in graph.vals])

    return graph

@return_strings
def remove_division(graph):
    graph = node(graph.op,*[remove_division(i) for i in graph.vals])

    if graph == node("/", "_", "_"):
        graph = node("*", graph.vals[0], node("^", graph.vals[1], node("-", "1")))
    return graph


def simplify_exponent(graph):
    '''
    simplify cases:
     bring down exponents: (a^b)^c -> a^(bc)
     split power bases: (ab)^c -> a^c*b^c
    repeat calling in order until second case is no longer triggered
    '''

    @return_strings
    def unstack_exp(graph):

        graph = node(graph.op, *[unstack_exp(i) for i in graph.vals])

        if graph == node("^", node("^", "_", "_"), "_"):
            graph = node("^", graph.vals[0].vals[0], node("*", graph.vals[0].vals[1], graph.vals[1]))

        return graph

    def split_exp_bases(graph):

        if type(graph) == str:
            return graph, False

        changed = False

        vals = []
        for g in graph.vals:
            v, c = split_exp_bases(g)
            changed |= c
            vals.append(v)

        graph = node(graph.op, *vals)

        if graph == node("^", node("*", "_", "_"), "_"):
            graph = node("*", node("^", graph.vals[0].vals[0], graph.vals[1]), node("^", graph.vals[0].vals[1], graph.vals[1]))
            changed = True

        return graph, changed

    changed = True
    while changed:
        graph = unstack_exp(graph)
        graph, changed = split_exp_bases(graph)

    return graph

@return_strings
def remove_minus(graph):
    graph = node(graph.op, *[remove_minus(i) for i in graph.vals])

    if graph == node("-", "_"):
        graph = node("*", "-1", graph.vals[0])
    elif graph == node("-", "_", "_"):
        graph = node("+", graph.vals[0], node("*", graph.vals[1], "-1"))

    return graph

global depth
depth = 0

@prefix_minus_to_value
@associative_cases(["+", "*"])
def eval_literal(graph, factors=False, minuses=False):

    '''
    simplify expressions by evaluating literal function calls bottom up (order *shouldn't* matter):
     0. node("-", "1") -> "-1" (wrapper)
     1. 2+3 -> 5
     2. 4*5 -> 20
     3. 2^(2x) -> 4^x
     4. 1*x -> x
     5. 0+x -> x
     6. 0*x -> 0
     7. x^0 -> 1
     8. 0^x -> 0
     9. x^1 -> x
     10. 1^x -> 1
    if factors convert all integers to prime factors again at end
    if not minuses call remove_minus
    '''

    def eval_literal_recursive(graph):

        if type(graph) == str:
            return graph, 0

        vals = [eval_literal_recursive(i) for i in graph.vals]
        changes = sum([i[1] for i in vals])
        vals = [i[0] for i in vals]
        graph = node(graph.op, *vals)  # evaluate bottom up to handle cases such as 2*3 + 4

        if graph == node("+", "_", "_") and all([type(i) == str and i not in ["x", "y", "z", "pi"] for i in graph.vals]):  # 1
            graph = str(eval("+".join(graph.vals)))
        elif graph == node("*", "_", "_") and all([type(i) == str and i not in ["x", "y", "z", "pi"] for i in graph.vals]):  # 2
            graph = str(eval("*".join(graph.vals)))
        elif graph == node("^", "_", "_") and all([type(i) == str and i not in ["x", "y", "z", "pi"] for i in graph.vals]):  # 3
            graph = str(eval("**".join(graph.vals)))
        elif graph == node("^", "_", node("*", "_", "_")) and all([type(i) == str and i not in ["x", "y", "z", "pi"] for i in [graph.vals[0], graph.vals[1].vals[0]]]):  # 3
            graph = node("^", str(eval(graph.vals[0] + "**" + graph.vals[1].vals[0])), graph.vals[1].vals[1])
        elif graph == node("^", "_", node("*", "_", "_")) and all([type(i) == str and i not in ["x", "y", "z", "pi"] for i in [graph.vals[0], graph.vals[1].vals[1]]]):  # 3
            graph = node("^", str(eval(graph.vals[0] + "**" + graph.vals[1].vals[1])), graph.vals[1].vals[0])
        elif graph in [node("*", "1", "_"), node("+", "0", "_")]:  # 4, 5
            graph = graph.vals[1]
        elif graph in [node("*", "_", "1"), node("+", "_", "0"), node("^", "_", "1")]:  # 4, 5, 9
            graph = graph.vals[0]
        elif graph == node("*", "0", "_") or graph == node("*", "_", "0") or graph == node("^", "0", "_"):  # 6, 8
            graph = "0"
        elif graph == node("^", "_", "0") or graph == node("^", "1", "_"):  # 7, 10
            graph = "1"

        else:  # add one to changes IFF a change is made
            changes -= 1
        changes += 1

        return graph, changes

    graph, changes = eval_literal_recursive(graph)

    if not minuses:  # these are not counted to changes total
        graph = remove_minus(graph)
    if factors:
        graph = to_prime_factors(graph)

    return graph, changes

@return_strings
def expand_multiplication(graph):
    '''
    (x*(x+2))*(x+1)^2 -> (x*x+2*x)*(1*(x^2*1^0)+(2*(x^1*1^1)+1^2)) -> (x*x)*(1*(x^2*1^0)+(2*(x^1*1^1)+1^2))+
    (2*x)*(1*(x^2*1^0)+(2*(x^1*1^1)+1^2)) -> ((1*(x^2*1^0))*(x*x)+(2*(x^1*1^1)+1^2)*(x*x))+((1*(x^2*1^0))*(2*x)+(2*(x^1*1^1)+1^2)*(2*x))
     -> ((1*(x^2*1^0))*(x*x)+((2*(x^1*1^1))*(x*x)+(1^2)*(x*x)))+((1*(x^2*1^0))*(2*x)+((2*(x^1*1^1))*(2*x)+(1^2)*(2*x)))
    ( -> x^4 + 4x^3 + 5x^2 + 2x)

    for (x_0 + x_1 + ... + x_k)^n
    then instead of calculating the multinomial coeficient directly, use binonial as:
    (x_0 + (x_1 + ... + x_k))^n -> sum^n_k=0(nCk * x_0^(n-k) * (x_1 + ... + x_k)*k)
    and then calculate (x_1 + ... + x_k)*k again recursively
    '''

    factorial = lambda x : 1 if x == 0 else x * factorial(x-1)

    graph = node(graph.op, *[expand_multiplication(i) for i in graph.vals])

    # expand powers
    if graph == node("^", node("+", "_", "_"), "_") and type(graph.vals[1]) == str and graph.vals[1] not in ["x", "y", "z", "pi"]:
        n = eval(graph.vals[1])

        new_graph = expand_multiplication(node("^", graph.vals[0].vals[1], graph.vals[1]))
        for k in range(n-1, -1, -1):
            coef = int(factorial(n) / (factorial(k) * factorial(n-k)))  # nCk
            next_node = node("*", str(coef), node("*", expand_multiplication(node("^", graph.vals[0].vals[0], str(n-k))),
                                                       expand_multiplication(node("^", graph.vals[0].vals[1], str(k)))))
            new_graph = node("+", next_node, new_graph)

        graph = new_graph

    elif graph in [node("*", node("+", "_", "_"), "_"), node("*", "_", node("+", "_", "_"))]:
        if graph.vals[0] == node("+", "_", "_"):
            graph = node("+", expand_multiplication(node("*", graph.vals[0].vals[0], graph.vals[1])),
                              expand_multiplication(node("*", graph.vals[0].vals[1], graph.vals[1])))
        else:
            graph = node("+", expand_multiplication(node("*", graph.vals[1].vals[0], graph.vals[0])),
                              expand_multiplication(node("*", graph.vals[1].vals[1], graph.vals[0])))

    return graph

def simplify_polynomial(graph, factor=True):

    '''
     0. check is computable (e.g. not division by 0)
     1. convert a/b -> ab^-1
     2. simplify_exponent
     4. eval_literal
     5. expand multiplication (top down): (a+b)^n*(c+d) -> ca^n + nca^(n-1)b + ... + cb^n + da^n + nda^(n-1)b + ... + db^n
     6. convert to prime factors (NOTE: -1 should be node("-", "1") not "-1" in input but can be internally stored as "-1")
     7. simplify_exponent
     8. eval_literal (factors=True)
     9. force powers on sum or product level terms: a * a^n -> a^1 * a^n
     10. collect exponents: a^b * a^c -> a^(a + c)
     11. eval_literal (factors=True)
     12. factorise (if factor) and rationalise denominator (bottom up, eval after change w/factors=True): x^2 + 3*y^-0.5x -> xy^-1*(x*y + 3y^0.5)
     13. force powers on sum or product level terms: a * a^n -> a^1 * a^n
     14. collect exponents: a^b * a^c -> a^(a + c)
     15. collect bases: a^n*b^n -> (ab)^n
     16. eval_literal
     17. replace - and /: ab^-1 -> a/b, a + b*-1 -> a - b, b^-1 -> -b
     18. collect denominators (if factor) (bottom up): 1/x + 1/y -> (x+y)/(xy)
     19. eval_literal (minuses=True)
     20. make nice order (not necessary for python system but may be useful in rust)


    example (changed made after this but generally correct):
     0. x * 1 * (x + 2 + 0) ^ 2 * 3 + 4 * x - (((x / 3) ^ 2) ^ 2) ^ 1
     1. x * 1 * (x + 2 + 0) ^ 2 * 3 + 2 ^ 2 * x - (((x / 3) ^ 2) ^ 2) ^ 1
     2. x * 1 * (x + 2 + 0) ^ 2 * 3 + 2 ^ 2 * x - (((x * 3 ^ - 1) ^ 2) ^ 2) ^ 1
     3. x * 1 * (x + 2 + 0) ^ 2 * 3 + 2 ^ 2 * x - (x * 3 ^ - 1) ^ (2 * 2)
        x * 1 * (x + 2 + 0) ^ 2 * 3 + 2 ^ 2 * x - x ^ (2 * 2) * (3 ^ - 1) ^ (2 * 2)
        x * 1 * (x + 2 + 0) ^ 2 * 3 + 2 ^ 2 * x - x ^ (2 * 2) * 3 ^ (- 1 * 2 * 2)
     4. x * 1 * (x + 2 + 0) ^ 2 * 3 + 2 ^ 2 * x + - 1 * x ^ (2 * 2) * 3 ^ (- 1 * 2 * 2)
     5. x * (x + 2) ^ 2 * 3 + 2 ^ 2 * x + - 1 * x ^ (2 ^ 2) * 3 ^ (- 1 * 2 ^ 2)
     6. x * (x ^ 2 + 2 * 2 * x + 2 ^ 2) * 3 + 2 ^ 2 * x + - 1 * x ^ 2 ^ 2 * 3 ^ (- 1 * 2 ^ 2)
        3 * x * x ^ 2 + 3 * x * 2 * 2 * x + 3 * x * 2 ^ 2 + 2 ^ 2 * x + - 1 * x ^ 2 ^ 2 * 3 ^ (- 1 * 2 ^ 2)
     7. 3 * x * x ^ 2 + 3 * x * 2 * 2 * x + 3 * x * 2 ^ 2 + 2 ^ 2 * x + - 1 * x ^ 2 ^ 2 * 3 ^ (- 1 * 2 ^ 2)
     8. 3 * x * x ^ 2 + 3 * 2 ^ 2 * x * x + 3 * x * 2 ^ 2 + 2 ^ 2 * x + - 1 * x ^ 2 ^ 2 * 3 ^ (- 1 * 2 ^ 2)
     9. 3 ^ 1 * x ^ 1 * x ^ 2 + 3 ^ 1 * 2 ^ 2 * x ^ 1 * x ^ 1 + 3 ^ 1 * x ^ 1 * 2 ^ 2 + 2 ^ 2 * x ^ 1 + (- 1)
                        ^ 1 * x ^ 2 ^ 2 * 3 ^ ((- 1) ^ 1 * 2 ^ 2)
     10. 3 ^ 1 * x ^ (1 + 2) + 3 ^ 1 * 2 ^ 2 * x ^ (1 + 1) + 3 ^ 1 * x ^ 1 * 2 ^ 2 + 2 ^ 2 * x ^ 1 + (- 1)
                        ^ 1 * x ^ 2 ^ 2 * 3 ^ ((- 1) ^ 1 * 2 ^ 2)
     11. 3 * x ^ 3 + 3 * 2 ^ 2 * x ^ 2 + 3 * 2 ^ 2 * x + 2 ^ 2 * x + - x ^ 2 ^ 2 * 3 ^ (- 1 * 2 ^ 2)
     12. x * (3 * x ^ 2 + 3 * 2 ^ 2 * x ^ 1 + 3 * 2 ^ 2 * x ^ 0 + 2 ^ 2 * x ^ 0 + - x ^ (2 ^ 2 - 1) * 3 ^ (- 1 * 2 ^ 2))
         x * (3 * x ^ 2 + 3 * 2 ^ 2 * x + 2 ^ 2 ^ 2 + - x ^ 3 * 3 ^ (- 1 * 2 ^ 2))
     13. x * (3 ^ 1 * x ^ 2 + 3 ^ 1 * 2 ^ 2 * x ^ 1 + 2 ^ 2 ^ 2 + - x ^ 3 * 3 ^ ((- 1) ^ 1 * 2 ^ 2))
     14. x * (3 ^ 1 * x ^ 2 + 3 ^ 1 * 2 ^ 2 * x ^ 1 + 2 ^ 2 ^ 2 + - x ^ 3 * 3 ^ ((- 1) ^ 1 * 2 ^ 2))
     15. x * (3 ^ 1 * x ^ 2 + (3 * x) ^ 1 * 2 ^ 2 + 2 ^ 2 ^ 2 + - x ^ 3 * 3 ^ ((- 1) ^ 1 * 2 ^ 2))
     16. x * (3 * x ^ 2 + 12 * x + 16 - x ^ 3 * 81 ^ - 1)
     17. x * (3 * x ^ 2 + 12 * x + 16 - x ^ 3 / 81)
     18. x / 81 * (81 * 3 * x ^ 2 + 81 * 12 * x + 81 * 16 - x ^ 3)
     19. x / 81 * (243 * x ^ 2 + 972 * x + 1296 - x ^ 3)
     20. x * (- x ^ 3 + 243 * x ^ 2 + 972 * x + 1296) / 81

     so x * 1 * (x + 4 + 0) ^ 2 * 3 + 4 * x - (((x / 3) ^ 2) ^ 2) ^ 1 = x * (- x ^ 3 + 243 * x ^ 2 + 972 * x + 1296) / 81
    '''

    if not is_computable(graph):  # 0
        return node("undefined")

    graph = remove_division(graph)  # 1
    graph = simplify_exponent(graph)  # 2
    graph = remove_prefix_minus(graph)  # 3
    graph = eval_literal(graph)  # 4
    graph = expand_multiplication(graph)  # 5

    return graph