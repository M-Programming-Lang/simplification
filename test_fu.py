from math import prod
from fu import *
from simplify_polynomial import *
import unittest

class TestFu(unittest.TestCase):

      test_expr = node("-", terms[0], node("+", terms[1], node("+", terms[2], terms[3])))  # 1 - sin^2(2x)/4 - sin^2(y) - cos^4(x)

      def test_eq(self):
            self.assertEqual(node("sin", "x"), node("sin", "x"))
            self.assertEqual(node("sin", "x"), node("sin", "_"))
            self.assertEqual(node("sin", node("+", "2", "3")), node("sin", "_"))
            self.assertEqual(node("sin", node("+", "2", "3")), node("sin", node("+", "2", "3")))

            self.assertNotEqual(node("-", "x", "_"), node("-", "x"))
            self.assertNotEqual(node("-", "x", "_"), node("-", "y", "_"))
            self.assertNotEqual(node("sin", node("+", "2", "3")), node("sin", node("+", "2", node("tan", "x"))))
            self.assertNotEqual(node("sin", "x"), node("cos", "x"))
            self.assertNotEqual("3", node("cos", "x"))

      def test_count_trig_ops(self):
            self.assertEqual(3, count_trig_ops(self.test_expr))
            self.assertEqual(0, count_trig_ops(""))

      def test_check_operator(self):
            self.assertTrue(check_operator(node("sin", node("+", "2", "3")), "+"))
            self.assertTrue(check_operator(node("sin", node("+", "2", "3")), "sin"))

            self.assertFalse(check_operator(node("sin", node("+", "2", "3")), "cos"))

      def test_negative_to_infix(self):
            self.assertEqual(negative_to_infix(node("sin", "x")), node("sin", "x"))
            self.assertEqual(negative_to_infix(node("sin", node("+", "x", node("-", "y")))), node("sin", node("-", "x", "y")))

      def test_double_neg(self):
            self.assertEqual(double_neg(node("sin", node("-", node("-", "x")))), node("sin", "x"))
            self.assertEqual(double_neg(node("-", "x", node("-", "y"))), node("+", "x", "y"))

      def test_TR0(self):
            for n in [123, 2465, 23, 4, 65, 78, 754, 23]:
                  self.assertEqual(n, prod(calculate_pfs(n)))
            self.assertEqual([3, 41], calculate_pfs(123))

            self.assertFalse(is_computable(node("+", "1", node("/", node("^", "x" "2"), "0"))))
            self.assertEqual(to_prime_factors(node("+", "5", node("/", node("^", "x", "12"), "1"))),
                                              node("+", "5", node("/", node("^", "x", node("*", "2", node("*", "2", "3"))), "1")))
            self.assertEqual(remove_division(node("+", "1", node("/", node("^", "x" "2"), "x"))),
                                              node("+", "1", node("*", node("^", "x" "2"), node("^", "x", node("-", "1")))))


            # ((((x^y)*z)^x)^y)^z = x^(y*((x*y)*z))*z^((x*y)*z) ( = x^(y*x*y*z))*z^(x*y*z) )
            self.assertEqual(simplify_exponent(node("^", node("^", node("^", node("*", node("^", "x", "y"), "z"), "x"), "y"), "z")),
                                               node("*", node("^", "x", node("*", "y", node("*", node("*", "x", "y"), "z"))),
                                                         node("^", "z", node("*", node("*", "x", "y"), "z"))))

            self.assertEqual(remove_minus(node("-", node("-", "x", "y"))), node("*", "-1", node("+", "x", node("*", "y", "-1"))))
            self.assertEqual(eval_literal(node("*", node("+", node("^", "2", node("*", "2", node("-", node("+", node("*", node("^", "x",
                                          node("^", "0", "x")), node("^", "x", "1")), node("*", "2", "2")), "4"))), node("*", "0", "x")),
                                          node("^", "1", "x"))), node("^", "4", "x"))  # (2^(2*((x^(0^x)*x^1+2*2)-4))+0*x)*1^x -> 4^x   

            self.assertEqual(expand_multiplication(node("*", node("*", "x", node("+", "x", "2")), node("^", node("+", "x", "1"), "2"))),
            node("+", node("+", node("*", node("*", "1", node("*", node("^", "x", "2"), node("^", "1", "0"))), node("*", "x", "x")),
            node("+", node("*", node("*", "2", node("*", node("^", "x", "1"), node("^", "1", "1"))), node("*", "x", "x")),
            node("*", node("^", "1", "2"), node("*", "x", "x")))),
            node("+", node("*", node("*", "1", node("*", node("^", "x", "2"), node("^", "1", "0"))), node("*", "2", "x")),
            node("+", node("*", node("*", "2", node("*", node("^", "x", "1"), node("^", "1", "1"))), node("*", "2", "x")),
            node("*", node("^", "1", "2"), node("*", "2", "x"))))))
            # (x*(x+2))*(x+1)^2 -> ((1*(x^2*1^0))*(x*x)+((2*(x^1*1^1))*(x*x)+(1^2)*(x*x)))+((1*(x^2*1^0))*(2*x)+
            #                                                                   ((2*(x^1*1^1))*(2*x)+(1^2)*(2*x)))

            self.assertEqual(force_powers(node("*", "x", node("^", node("+", node("^", "1", "y"), node("*", "2", "3")), "z"))),
                                          node("*", node("^", "x", "1"), node("^", node("+", node("^", "1", "y"), node("^", node("*",
                                          node("^", "2", "1"), node("^", "3", "1")), "1")), "z")))
            # x * (1^y + 2*3)^z -> x^1 * (1^y + (2^1*3^1)^1)^z

      def test_TR1(self):
            self.assertEqual(TR1(node("sec", "x")), node("/", "1", node("cos", "x")))
            self.assertEqual(TR1(node("sin", node("csc", "x"))), node("sin", node("/", "1", node("sin", "x"))))

      def test_TR3(self):
            self.assertEqual(TR3(node("sin", node("-", "x"))), node("-", node("sin", "x")))
            self.assertEqual(TR3(node("cos", node("-", "pi", "x"))), node("-", node("cos", "x")))
            self.assertEqual(TR3(node("tan", node("+", "pi", "x"))), node("tan", "x"))
            self.assertEqual(TR3(node("cot", node("-", node("*", "2", "pi"), "x"))), node("-", node("cot", "x")))
            self.assertEqual(TR3(node("sin", node("+", node("*", "2", "pi"), "x"))), node("sin", "x"))
            self.assertEqual(TR3(node("cos", node("+", node("*", "4", "pi"), "x"))), node("cos", "x"))
            self.assertEqual(TR3(node("tan", node("-", node("sin", node("-", "x"))))), node("tan", node("sin", "x")))
            self.assertEqual(TR3(node("cot", node("-", node("cos", node("-", "x"))))), node("-", node("cot", node("cos", "x"))))

      def test_TR4(self):
            self.assertEqual(TR4(node("tan", node("/", "pi", "6"))), node("/", node("^", "3", node("/", "1", "2")), "3"))
            self.assertEqual(TR4(node("sin", node("cos", node("/", "pi", "6")))), node("sin", node("/", node("^", "3", node("/", "1", "2")), "2")))
            self.assertEqual(TR4(node("sin", node("sin", "0"))), "0")

      def test_TR12(self):
            self.assertEqual(TR12(node("sin", node("tan", node("-", "x", "y")))), node("sin", node("/", node("-", node("tan", "x"),
                        node("tan", "y")), node("+", "1", node("*", node("tan", "x"), node("tan", "y"))))))

            self.assertEqual(TR12(node("tan", node("+", "x", node("+", "y", "z")))), node("/", node("+", node("tan", "x"),
                        node("/", node("+", node("tan", "y"), node("tan", "z")), node("-", "1", node("*", node("tan", "y"),
                        node("tan", "z"))))), node("-", "1", node("*", node("tan", "x"), node("/", node("+", node("tan", "y"),
                        node("tan", "z")), node("-", "1", node("*", node("tan", "y"), node("tan", "z"))))))))  # apply twice for tan(x+y+z)

      def test_TR13(self):
            self.assertEqual(TR13(node("*", node("tan", "x"), node("tan", "y"))),
                             node("-", "1", node("+", node("/", node("tan", "x"), node("tan", node("+", "x", "y"))), node("/", node("tan", "y"), node("tan", node("+", "x", "y"))))))
            self.assertEqual(TR13(node("sin", node("*", node("cot", "x"), node("cot", "y")))),
                             node("sin", node("+", "1", node("+", node("/", node("cot", "x"), node("tan", node("+", "x", "y"))), node("/", node("cot", "y"), node("tan", node("+", "x", "y")))))))
            self.assertEqual(TR13(node("*", node("tan", "x"), node("/", node("tan", "y"), node("tan", "z")))),
                             node("/", node("-", "1", node("+", node("/", node("tan", "x"), node("tan", node("+", "x", "y"))), node("/", node("tan", "y"), node("tan", node("+", "x", "y"))))), node("tan", "z")))

      def test_get_rpn(self):
            self.assertEqual(get_rpn(self.test_expr), "1 2 x * sin 2 ^ 4 / y sin 2 ^ x cos 4 ^ + + -")

      def test_get_infix(self):
            self.assertEqual(get_infix(self.test_expr, True), "(1) - ((((sin((2) * (x))) ^ (2)) / (4)) + (((sin(y)) ^ (2)) + ((cos(x)) ^ (4))))")

if __name__ == "__main__":
      unittest.main()