import unittest
import numpy as np
from lupa.utils.calculator import calculate
from lupa.exceptions.calculatorexceptions import (
    UnexpectedCharacterError,
    BadNumberError,
    BadFunctionError,
    WrongArgsLenError,
    UnexpectedEndError,
)


class TestCalculator(unittest.TestCase):

    def test_basic_arithmetic(self):
        self.assertAlmostEqual(calculate("3 + 4"), 7)
        self.assertAlmostEqual(calculate("10 - 2"), 8)
        self.assertAlmostEqual(calculate("6 * 3"), 18)
        self.assertAlmostEqual(calculate("8 / 2"), 4)

    def test_parentheses(self):
        self.assertAlmostEqual(calculate("(1 + 2) * 3"), 9)
        self.assertAlmostEqual(calculate("3 * (2 + 1)"), 9)
        self.assertAlmostEqual(calculate("3 * (2 + (1 - 3))"), 0)

    def test_exponentiation(self):
        self.assertAlmostEqual(calculate("2 ** 3"), 8)
        self.assertAlmostEqual(calculate("4 ** 0.5"), 2)

    def test_functions(self):
        self.assertAlmostEqual(calculate("sin(pi / 2)"), 1)
        self.assertAlmostEqual(calculate("cos(0)"), 1)
        self.assertAlmostEqual(calculate("abs(-5)"), 5)
        self.assertAlmostEqual(calculate("floor(3.9)"), 3)

    def test_constants(self):
        self.assertAlmostEqual(calculate("pi"), np.pi)
        self.assertAlmostEqual(calculate("e"), np.e)
        self.assertAlmostEqual(calculate("2 * pi"), 2 * np.pi)
        self.assertAlmostEqual(calculate("3e3"), 3e3)

    def test_variables(self):
        result, vars = calculate("2 * t", return_vars=True)
        self.assertAlmostEqual(result(5), 10)
        self.assertEqual(vars, ["t"])
        result, vars = calculate("t * t", return_vars=True)
        self.assertAlmostEqual(result(3), 9)
        self.assertEqual(vars, ["t"])

    def test_combined_expressions(self):
        self.assertAlmostEqual(calculate("2 * sin(pi / 2) + cos(0)"), 3)
        self.assertAlmostEqual(calculate("2 + 3 * 4"), 14)
        self.assertAlmostEqual(calculate("(2 + 3) * 4"), 20)
        self.assertAlmostEqual(calculate("2 ** 3 * 4"), 32)
        self.assertAlmostEqual(calculate("2 ** (3 * 4)"), 2**12)

    def test_invalid_characters(self):
        with self.assertRaises(UnexpectedCharacterError):
            calculate("3 + @")

    def test_invalid_numbers(self):
        with self.assertRaises(BadNumberError):
            calculate("3.3.3")
        with self.assertRaises(BadNumberError):
            calculate("3e3.3")

    def test_invalid_functions(self):
        with self.assertRaises(BadFunctionError):
            calculate("son(3)")

    def test_invalid_expressions(self):
        with self.assertRaises(UnexpectedEndError):
            calculate("2 + (3 * 4")
        with self.assertRaises(UnexpectedCharacterError):
            calculate("3 + * 2")

    def test_wrong_args_length(self):
        expr = calculate("t + 1")
        with self.assertRaises(WrongArgsLenError):
            expr(1, 2)
        with self.assertRaises(WrongArgsLenError):
            expr()


if __name__ == "__main__":
    unittest.main()
