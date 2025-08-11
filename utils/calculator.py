"""
Infix calculator for mathematical expressions with configurable constants and
functions.

This module provides a flexible mathematical expression calculator that
supports:
- Basic arithmetic operations (+, -, *, /, **, %)
- Mathematical functions (sin, cos, tan, abs, floor, etc.)
- Custom constants and variables
- Configurable calculator instances
- Expression parsing with proper operator precedence

Main classes:
- Calculator: Configurable calculator instance
- PeekableIterator: Iterator with lookahead support
- Scanner: Tokenizes mathematical expressions
- Parser: Parses and evaluates tokenized expressions

Global instance:
- calculator: Default calculator instance for simple usage

Usage:
    Basic usage with global calculator:
    >>> from utils.calculator import calculate
    >>> calculate('2 + 3 * 4')
    14.0

    Custom calculator with additional constants:
    >>> from utils.calculator import Calculator
    >>> calc = Calculator(custom_constants={'R': 1000, 'C': 1e-6})
    >>> calc.calculate('2 * pi * R * C')
    0.006283185307179587

Adapted from
https://gist.github.com/baileyparker/309436dddf2f34f06cfc363aa5a6c86f

EBNF formulation:

PrecedenceLast = ...
...
Precedence4 = Precedence3 { ("+"|"-") Term } ;
Precedence3 = Precedence2 { ("*"|"/"|"%") Precedence2 } ;
Precedence2 = Precedence1 { ("**") Precedence1 } ;
Precedence1 = Number | "(" PrecedenceLast ")" | Function "(" PrecedenceLast ")"
              | Constant | Variable ;

Function = "sin" | "cos" | "tan" | "abs" ... ;
Number = Integer { "." Integer } | "." Integer ;
Integer = Digit { Digit } ;
Digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
Constant = "e" | "pi" ;
Variable = "t" | ... ;
"""

from typing import (
    Iterable,
    List,
    Dict,
    Any,
    Union,
    Callable,
)
import numpy as np
import operator as op
from exceptions.calculatorexceptions import (
    UnexpectedCharacterError,
    BadNumberError,
    BadFunctionError,
    WrongArgsLenError,
    UnexpectedEndError,
    ReadOnlyError,
)

# Public API exports
__all__ = ["Calculator", "calculator", "calculate"]

# Constants for operator precedence
PREC_EXPONENTIATION = 1
PREC_MULT_DIV_MOD = 2
PREC_ADD_SUB = 3
PREC_RELATIONAL = 4
PREC_EQUALITY = 5
PREC_LOGICAL_AND = 6
PREC_LOGICAL_XOR = 7
PREC_LOGICAL_OR = 8


# Utility functions
def evaluate(items: List):
    """Evaluate a list of float-returning functions separated by operators
    (at the same level of precedence). Returns the result.

    >>> evaluate([lambda *args: 3, '*', lambda *args: 4, '/', lambda *args: 2])
    6
    """

    assert items, "Cannot evaluate empty list"
    assert len(items) % 2 == 1, "List must be of odd length"
    assoc = "left_to_right"  # Useful if one day we add right_to_left associativity

    if assoc == "right_to_left":
        while len(items) > 1:
            items[-3:] = [_evaluate_binary(*items[-3:])]

    if assoc == "left_to_right":
        while len(items) > 1:
            items[:3] = [_evaluate_binary(*items[:3])]

    return items[0]


def _evaluate_binary(lhs: Callable, op: str, rhs: Callable):
    """Evaluates a single binary operation op where lhs and rhs are functions
    returning floats or float arrays."""
    return lambda *args: flatten(operators)[op](lhs(*args), rhs(*args))


def flatten(iterable: Iterable):
    """Flattens a nested iterable by one nesting layer.

    >>> flatten([[1,2], [3]])
    [1, 2, 3]

    >>> flatten({1: {"a": "aa", "b": "bb"}, 2: {"c": "cc"}})
    {'a': 'aa', 'b': 'bb', 'c': 'cc'}
    """
    if isinstance(iterable, dict):
        newdict = {}
        for x in iterable.values():
            newdict.update(x)
        return newdict
    return [x for el in iterable for x in el]


def get_char(list_str: List, idx: int):
    """Returns a list of characters of index idx from strings
    listed in list_str. If the string is too short,
    returns an empty string.

    >>> get_char(["abc", "d", "ef"], 1)
    ["b", "", "f"]

    Args:
        list_str (list(str)): list of strings
        id (int): index of strings to retrieve

    Returns:
        list(str): list of characters at index id
    """
    return [string[idx] if idx < len(string) else "" for string in list_str]


def is_char_inorder(list_str: List[str]):
    """Generator for checking non-number tokens. It asks for the character
    to check, then takes all the tokens starting with this character
    and yields True if such tokens exist, False otherwise. It repeats
    until no more tokens can be checked.

    >>> x = is_char_inorder(["abc","d","ef","g","hij"])
    >>> next(x)
    None
    >>> x.send("h")
    True
    >>> next(x)
    None
    >>> x.send("i")
    True
    >>> next(x)
    None
    >>> x.send("c")
    False

    Yields:
        bool: does the next character correspond to a token
    """
    my_tokens = list_str
    for idx in range(max(len(tok) for tok in my_tokens)):
        list_char_idx = get_char(my_tokens, idx)
        c = yield
        my_tokens = [my_tokens[i] for i, x in enumerate(list_char_idx) if x == c]
        yield bool(my_tokens)


"""
Copied from https://en.cppreference.com/w/c/language/operator_precedence
Precedence                                                  Associativity
1	()	Function call	                                    Left-to-right
2   **      Power
3	* / %	Multiplication, division, and remainder
4	+ -	Addition and subtraction
6	< <=	For relational operators < and ≤ respectively
    > >=	For relational operators > and ≥ respectively
7	== !=	For relational = and ≠ respectively
8	&	Logical AND
9	^	Logical XOR (exclusive or)
10	|	Logical OR (inclusive or)
"""

# These take one value : func(expression)
functions = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "abs": np.abs,
    "floor": np.floor,
}

# These take two values and are disposed between them : expr op expr
operators = {
    PREC_EXPONENTIATION: {"**": op.pow},
    PREC_MULT_DIV_MOD: {"*": op.mul, "/": op.truediv, "%": op.mod},
    PREC_ADD_SUB: {"+": op.add, "-": op.sub},
    PREC_RELATIONAL: {"<": op.lt, "<=": op.le, ">": op.gt, ">=": op.ge},
    PREC_EQUALITY: {"==": op.eq, "!=": op.ne},
    PREC_LOGICAL_AND: {"&": op.and_},
    PREC_LOGICAL_XOR: {"^": op.xor},
    PREC_LOGICAL_OR: {"|": op.or_},
}


class Calculator:
    """A configurable mathematical expression calculator."""

    def __init__(
        self,
        custom_constants: Dict[str, float] = None,
        custom_variables: Dict[str, str] = None,
        custom_functions: Dict[str, Callable[[float], float]] = None,
    ):
        """Initialize calculator with optional custom constants, variables, and
        functions.

        Args:
            custom_constants (dict, optional): Additional constants to include
            custom_variables (list, optional): Additional variables to support
            custom_functions (dict, optional): Additional functions to include
        """
        # Base configuration
        self.constants = {"e": np.e, "pi": np.pi}
        self.variables = {"t": "t"}
        self.functions = functions.copy()

        # Mark built-in defaults as protected (read-only & non-removable)
        self._protected_constants = set(self.constants.keys())
        self._protected_variables = set(self.variables.keys())

        # Add custom configurations
        if custom_constants:
            self.constants.update(custom_constants)
        if custom_variables:
            self.variables.update(custom_variables)
        if custom_functions:
            self.functions.update(custom_functions)

        # Build tokens and chars for this calculator instance
        self._update_tokens()

    def _update_tokens(self):
        """Update all_tokens and all_chars based on current configuration."""
        self.all_tokens = (
            list(self.functions)
            + list(flatten(operators))
            + list(self.constants)
            + list(self.variables)
        )
        self.all_chars = "".join(self.all_tokens) + "0123456789.e-+()"

    def is_protected_constant(self, name: str) -> bool:
        return name in self._protected_constants

    def is_protected_variable(self, name: str) -> bool:
        return name in self._protected_variables

    def add_constants(self, constants: Dict[str, float]):
        """Add multiple constants to the calculator."""
        for name, value in constants.items():
            if name in self.constants:
                raise ValueError(f"Constant '{name}' already exists.")
            self.constants[name] = value
        self._update_tokens()

    def add_variables(self, variables: Dict[str, str]):
        """Add multiple variables to the calculator."""
        for name, expr in variables.items():
            if name in self.variables:
                raise ValueError(f"Variable '{name}' already exists.")
            self.variables[name] = expr
        self._update_tokens()

    def add_functions(self, functions: Dict[str, Callable[[float], float]]):
        """Add multiple functions to the calculator."""
        for name, func in functions.items():
            if name in self.functions:
                raise ValueError(f"Function '{name}' already exists.")
            self.functions[name] = func
        self._update_tokens()

    def set_constant(self, name: str, value: Union[int, float]):
        """Create or update a constant. Protected constants are read-only
        (cannot be changed)."""
        if name in self._protected_constants:
            # Allow no-op set to same value, but block changes
            current = self.constants.get(name)
            if current is None or float(value) != float(current):
                raise ReadOnlyError(name)
            return
        try:
            num_val = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Constant '{name}' must be a number.")
        self.constants[name] = num_val
        self._update_tokens()

    def set_variable(self, name: str, expr: str):
        """Create or update a variable token. Protected variables are read-only
        (cannot be changed)."""
        if name in self._protected_variables:
            current = self.variables.get(name)
            if current is None or expr != current:
                raise ReadOnlyError(name)
            return
        self.variables[name] = expr
        self._update_tokens()

    def remove_constant(self, name: str):
        """Remove a constant, unless it is protected."""
        if name in self._protected_constants:
            raise ValueError(f"Constant '{name}' is protected and cannot be removed.")
        if name in self.constants:
            del self.constants[name]
            self._update_tokens()

    def remove_variable(self, name: str):
        """Remove a variable, unless it is protected."""
        if name in self._protected_variables:
            raise ValueError(f"Variable '{name}' is protected and cannot be removed.")
        if name in self.variables:
            del self.variables[name]
            self._update_tokens()

    def load_constants(self, constants: Dict[str, float]):
        """Load multiple constants into the calculator."""
        self.clear_constants()
        for name, value in constants.items():
            try:
                value = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"Constant '{name}' must be a number.")
            try:
                self.set_constant(name, value)
            except ReadOnlyError:
                continue
        self._update_tokens()

    def load_variables(self, variables: Dict[str, str]):
        """Load multiple variables into the calculator."""
        self.clear_variables()
        for name, expr in variables.items():
            try:
                self.set_variable(name, expr)
            except ReadOnlyError:
                continue
        self._update_tokens()

    def clear_constants(self):
        """Clear all constants except protected ones."""
        for name in list(self.constants.keys()):
            if name not in self._protected_constants:
                del self.constants[name]
        self._update_tokens()

    def clear_variables(self):
        """Clear all variables except protected ones."""
        for name in list(self.variables.keys()):
            if name not in self._protected_variables:
                del self.variables[name]
        self._update_tokens()

    def calculate(self, expression: str, return_vars: bool = False):
        """Evaluates a mathematical expression and returns the result.

        Args:
            expression (str): Mathematical expression to evaluate
            return_vars (bool): Whether to return variables used in expression

        Returns:
            float or callable or tuple: Result of evaluation

        >>> calc = Calculator()
        >>> calc.calculate('3 * (1 + 6 / 3)')
        9.0
        """
        if expression == "t":

            def result(t):
                return t

            vars = ["t"]
            if return_vars:
                return result, vars
            return result

        scan = Scanner(expression, self).scan()
        result, vars = Parser(scan, self).parse()

        if return_vars:
            return (result(), vars) if not vars else (result, vars)

        if vars:
            vars_func = [self.calculate(self.variables[var]) for var in vars]
            return lambda t: result(*[f(t) for f in vars_func])

        return result()


# Default global calculator instance
calculator: Calculator = Calculator()


# Classes
class PeekableIterator:
    """An iterator that supports 1-lookahead (peek).
    >>> i = PeekableIterator([1, 2, 3])
    >>> i.peek()
    1
    >>> i.peek()
    1
    >>> next(i)
    1
    >>> next(i)
    2
    >>> i.peek()
    3
    """

    def __init__(self, iterable: Iterable):
        self._iterator = iter(iterable)
        self._next_item = next(self._iterator, None)
        self._done = self._next_item is None

    def peek(self):
        if self._done:
            raise StopIteration
        return self._next_item

    def __next__(self):
        if self._done:
            raise StopIteration
        next_item = self._next_item
        self._next_item = next(self._iterator, None)
        self._done = self._next_item is None
        return next_item

    def __iter__(self):
        return self


class BaseParser:
    """A base class containing utilities useful for a Parser."""

    def __init__(self, items: Iterable):
        self._items = PeekableIterator(items)

    def _take(self, predicate: Callable[[Any], bool]):
        """
        Yields a contiguous group of items from the items being parsed for
        which the predicate returns True.

        >>> p = BaseParser([2, 4, 3])
        >>> list(p._take(lambda x: x % 2 == 0))
        [2, 4]
        """
        while not self._items._done and predicate(self._items.peek()):
            yield next(self._items)


class Scanner(BaseParser):
    """Scanner scans an input string for calculator tokens and yields them.

    >>> calc = Calculator()
    >>> list(Scanner('11 * (2 + 3)', calc).scan())
    [11.0, '*', '(', 2.0, '+', 3.0, ')']
    """

    def __init__(self, items: Iterable, calculator_instance: Calculator):
        super().__init__(items)
        self.calc: Calculator = calculator_instance

    def scan(self):
        """Yields all tokens in the input."""
        while not self._items._done:
            self._consume_whitespace()
            self._check_supported()
            yield from self._take(lambda c: c in "()")
            yield from self._take_number()
            yield from self._take_function_operator_variable()

    def _consume_whitespace(self):
        list(self._take(str.isspace))

    def _check_supported(self):
        """Checks if next char is supported. Avoids infinite loops."""
        c = self._items.peek()
        if c not in self.calc.all_chars:
            raise UnexpectedCharacterError(c)

    def _take_number(self):
        """Yields a single number if there is one next in the input.
        Supports decimal and scientific notation.
        """
        number = "".join(self._take(lambda c: c.isdigit() or c == "."))
        if number:
            number += "".join(self._take(lambda c: c == "e"))
            if number[-1] == "e":
                number += "".join(self._take(lambda c: c in "-+"))
                number += "".join(self._take(lambda c: c.isdigit() or c == "."))
        if number:
            try:
                yield float(number)
            except ValueError:
                raise BadNumberError(number)

    def _take_function_operator_variable(self):
        """Yields a single function, operator or variable if there is one next
        in the input."""
        gen = is_char_inorder(self.calc.all_tokens)

        def check(c):
            try:
                next(gen)
                return gen.send(c)
            except StopIteration:
                return False

        fov = "".join(self._take(check))
        if fov:
            if fov not in self.calc.all_tokens:
                complete_fov = fov + "".join(
                    self._take(lambda c: c in "abcdefghijklmnopqrstuvwxyz0123456789")
                )
                raise BadFunctionError(complete_fov, self.calc.all_tokens)
            yield fov


class Parser(BaseParser):
    """Parser for tokenized calculator inputs."""

    def __init__(self, items: Iterable, calculator_instance: Calculator):
        super().__init__(items)
        self.calc = calculator_instance
        self.vars = []

    def parse(self):
        """Parse calculator input and return the result of evaluating it.

        >>> Parser([1, '*', '(', 2, '+', 3, ')']).parse()
        5
        """
        return self._parse_expression(max(operators.keys())), self.vars

    def _parse_expression(self, precedence: int):
        """Parse a Term and return the result of evaluating it.

        >>> Parser([3, '*', 2])._parse_expression(2)
        6
        """
        if precedence == PREC_EXPONENTIATION:
            parse = self._parse_factor
        else:

            def parse():
                return self._parse_expression(precedence - 1)

        # Parse the first (required) Factor
        factors = [parse()]
        # Parse any following ("op") Factor
        factors += flatten(
            (op, parse()) for op in self._take(lambda t: t in operators[precedence])
        )

        return evaluate(factors)

    def _parse_factor(self):
        """Parse a Factor and return the result of evaluating it.

        >>> Parser([1])._parse_factor()
        1

        >>> Parser(['(', 1, '+', 2, '*', 'abs',\
            '(', '-', 3, ')', ')'])._parse_factor()
        7
        """
        for value in self._take(lambda t: isinstance(t, float)):
            return lambda *args: value

        for var in self._take(lambda t: t in self.calc.variables):
            if var not in self.vars:
                self.vars.append(var)

            def lambd(*args):
                if len(args) != len(self.vars):
                    raise WrongArgsLenError(len(args), len(self.vars))
                return args[self.vars.index(var)]

            return lambd

        for sign in self._take(lambda t: t in "+-"):
            value = self._parse_factor()
            return lambda *args: (value(*args) if sign == "+" else -value(*args))

        for cons in self._take(lambda t: t in self.calc.constants):
            value = self.calc.constants[cons]
            assert isinstance(
                value, (int, float)
            ), f"Invalid constant {cons}: {value}, type: {type(value)}"
            return lambda *args: value

        for func in self._take(lambda t: t in self.calc.functions):
            self._expect("(")
            value = self._parse_expression(max(operators.keys()))
            self._expect(")")
            return lambda *args: self.calc.functions[func](value(*args))

        for _ in self._take(lambda t: t == "("):
            value = self._parse_expression(max(operators.keys()))
            self._expect(")")
            return lambda *args: value(*args)

        # Parsing the number, function and subexpresion failed
        raise self._unexpected("number", "(", "function")

    def _expect(self, char: str):
        """Expect a certain character, or raise if it is not next."""
        for _ in self._take(lambda t: t == char):
            return
        raise self._unexpected(char)

    def _unexpected(self, *expected: str):
        """Create an exception for an unexpected character."""
        try:
            return UnexpectedCharacterError(self._items.peek(), expected)
        except StopIteration:
            return UnexpectedEndError(expected)


def calculate(expression: str, return_vars: bool = False):
    """Evaluates a mathematical expression and returns the result using the
    global calculator.

    Args:
        expression (str): Mathematical expression to evaluate
        return_vars (bool): Whether to return variables used in expression

    Returns:
        float or callable or tuple: Result of evaluation

    >>> calculate('3 * (1 + 6 / 3)')
    9.0
    """
    return calculator.calculate(expression, return_vars)
