def return_strings(func):  # is it possible to import this from fu.py?
    def function(graph, *args):
        if type(graph) == str:
            return graph
        return func(graph, *args)
    return function

class node:  # or this?
    def __init__(self, op, *vals):
        self.op, self.vals = op, vals
    def __eq__(self, graph):
        if type(graph) == str:
            if graph == "_":
                return True
            return False
        if len(graph.vals) != len(self.vals):
            return False
        return graph.op == self.op and all(["_" in [str(a), str(b)] or a == b for a, b in zip(self.vals, graph.vals)])
    def __repr__(self):
        return f"node({self.op}, {', '.join([str(i) for i in self.vals])})"

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


def eval_literal(graph, factors=False):
    '''
    simplify expressions by evaluating literal function calls bottom up:
     - 2+3 -> 5
     - 4*5 -> 20
     - 2^(2x) -> 4^x
     - 1*x -> x
     - 0+x -> x
     - 0*x -> 0
     - x^0 -> 1
     - 2^-2 -> 4^-1
    if primes convert all integers to prime factors again at end
    '''

    if type(graph) == str:
        return graph

    graph = node(graph.op, *[eval_literal(i) for i in graph.vals])  # evaluate bottom up to handle cases such as 2*3 + 4

def simplify_exponent(graph):
    '''
    simplify cases:
     bring down exponents: (a^b)^c -> a^(bc)
     split power bases: (ab)^c -> a^c*b^c
    repeat calling in order until second case is no longer triggered
    '''

def simplify_polynomial(graph):

    '''
     0. check is computable (e.g. not division by 0)
     1. convert to prime factors (inc separating prefix - if necessary)
     2. convert a/b -> ab^-1
     3. simplify_exponent
     4. convert - to multiplication: a - b -> a + -b -> a + -1*b
     5. eval literal (factors=True)
     6. expand multiplication (top down): (a+b)^n*(c+d) -> ca^n + nca^(n-1)b + ... + cb^n + da^n + nda^(n-1)b + ... + db^n
     7. simplify_exponent
     8. eval_literal (factors=True)
     9. force powers on sum or product level terms: a * a^n -> a^1 * a^n
     10. collect exponents: a^b * a^c -> a^(a + c)
     11. eval_literal (factors=True)
     12. factorise and rationalise denominator (bottom up, eval after change w/factors=True): x^2 + 3*y^-0.5x -> xy^-1*(x*y + 3y^0.5)
     13. force powers on sum or product level terms: a * a^n -> a^1 * a^n
     14. collect exponents: a^b * a^c -> a^(a + c)
     15. collect bases: a^n*b^n -> (ab)^n
     16. eval_literal
     17. replace - and /: ab^-1 -> a/b, a + b*-1 -> a - b, b^-1 -> -b
     18. collect denominators (bottom up): 1/x + 1/y -> (x+y)/(xy)
     19. eval_literal
     20. make nice order (not necessary for python system but may be useful in rust)


    example:
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

    graph = to_prime_factors(graph)  # 1
    graph = remove_division(graph)  # 2


    return graph
