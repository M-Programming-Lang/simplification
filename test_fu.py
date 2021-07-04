from math import pi
from fu import *
import unittest

class TestFu(unittest.TestCase):

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
            self.assertEqual(3, count_trig_ops(test))
            self.assertEqual(0, count_trig_ops(""))

      def test_check_operator(self):
            self.assertTrue(check_operator(node("sin", node("+", "2", "3")), "+"))
            self.assertTrue(check_operator(node("sin", node("+", "2", "3")), "sin"))

            self.assertFalse(check_operator(node("sin", node("+", "2", "3")), "cos"))

      def test_negative_to_infix(self):
            self.assertEqual(negative_to_infix(node("sin", "x")), node("sin", "x"))
            self.assertEqual(negative_to_infix(node("sin", node("+", "x", node("-", "y")))), node("sin", node("-", "x", "y")))

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

      def test_get_rpn(self):
            self.assertEqual(get_rpn(test), "1 2 x * sin 2 ^ 4 / y sin 2 ^ x cos 4 ^ + + -")

      def test_get_infix(self):
            self.assertEqual(get_infix(test, True), "(1) - ((((sin((2) * (x))) ^ (2)) / (4)) + (((sin(y)) ^ (2)) + ((cos(x)) ^ (4))))")
            
      def test_double_neg(self):
            self.assertEqual(double_neg(node("sin", node("-", node("-", "x")))), node("sin", "x"))
            self.assertEqual(double_neg(node("-", "x", node("-", "y"))), node("+", "x", "y"))
      

if __name__ == "__main__":
      unittest.main()