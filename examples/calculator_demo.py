"""
Calculator Demo - Elastance Function Calculation
Demonstrates the use of the Calculator class with custom constants
and complex mathematical expressions for circuit analysis.
"""

import numpy as np
import matplotlib.pyplot as plt
from utils.calculator import Calculator


def demo_basic_calculator():
    """Demonstrate basic calculator functionality."""
    print("=== Basic Calculator Demo ===")
    from utils.calculator import calculate  # Using global calculator

    # Basic operations
    expressions = [
        "2 + 3 * 4",
        "(2 + 3) * 4",
        "2 ** 3",
        "sin(pi / 2)",
        "cos(0)",
        "abs(-5)",
        "floor(3.9)",
        "e ** 2",
        "2 * pi",
    ]

    for expr in expressions:
        result = calculate(expr)
        print(f"{expr} = {result}")

    print()


def demo_custom_constants():
    """Demonstrate calculator with custom constants for circuit analysis."""
    print("=== Custom Constants Demo ===")

    # Create calculator with custom constants for elastance function
    my_constants = {
        "Emin": 0.1,  # Minimum elastance
        "Emax": 2.0,  # Maximum elastance
        "T1": 0.15,  # Systole peak
        "T2": 0.3,  # End of systole
        "Tt": 0.7,  # Total cardiac cycle time
    }

    calc = Calculator(custom_constants=my_constants)

    # Test custom constants
    print(f"Emin = {calc.calculate('Emin')}")
    print(f"Emax = {calc.calculate('Emax')}")
    print(f"Emin + Emax = {calc.calculate('Emin + Emax')}")
    print(f"(Emax - Emin) / 2 = {calc.calculate('(Emax - Emin) / 2')}")

    print()
    return calc


def demo_elastance_function(calc: Calculator):
    """Demonstrate complex elastance function calculation and plotting."""
    print("=== Elastance Function Demo ===")

    # Define time modulo function for periodic cardiac cycle
    tmod_expr = "t - floor(t/Tt) * Tt"
    tmod = calc.calculate(tmod_expr)
    print(f"Time modulo function: {tmod_expr}")

    # Define complex elastance function
    El_expr = (
        "1.333e3 * (Emin + (Emax - Emin) * "
        "((t <= T2) * (t >= T1) * 1/2 * (1 + cos(pi * (t - T1) / (T2 - T1))) + "
        "(t < T1) * 1/2 * (1 - cos(pi * t / T1))))"
    )

    El = calc.calculate(El_expr)
    print(f"Elastance function: {El_expr}")

    # Generate time values and calculate elastance
    t = np.linspace(0, 3, 300)
    tmod_values = tmod(t)
    El_values = El(tmod_values)

    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(t, El_values, "b-", linewidth=2, label="Elastance Function")
    plt.title("Calculator Demo - Cardiac Elastance Function")
    plt.xlabel("Time (s)")
    plt.ylabel("Elastance (Pa/m³)")
    plt.grid(True, alpha=0.3)

    # Add annotations for cardiac cycle phases
    plt.axvspan(0.0, 0.3, alpha=0.2, color="red", label="Systole")
    plt.axvspan(0.7, 1.0, alpha=0.2, color="red")  # Second cycle
    plt.axvspan(1.4, 1.7, alpha=0.2, color="red")  # Third cycle

    plt.legend()
    plt.tight_layout()
    plt.show()

    print(f"Peak elastance: {np.max(El_values):.2f} Pa/m³")
    print(f"Min elastance: {np.min(El_values):.2f} Pa/m³")
    print()


def demo_variable_expressions():
    """Demonstrate expressions with variables."""
    print("=== Variable Expressions Demo ===")

    calc = Calculator()

    # Simple variable expression
    expr, vars = calc.calculate("2 * t + 5", return_vars=True)
    print("Expression: 2 * t + 5")
    print(f"Variables used: {vars}")
    print(f"f(3) = {expr(3)}")
    print(f"f(10) = {expr(10)}")

    # Quadratic expression
    expr2, vars2 = calc.calculate("t ** 2 - 3 * t + 2", return_vars=True)
    print("\nExpression: t² - 3t + 2")
    print(f"Variables used: {vars2}")
    for t_val in [0, 1, 2, 3]:
        print(f"f({t_val}) = {expr2(t_val)}")

    print()


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("=== Error Handling Demo ===")

    calc = Calculator()

    test_cases = [
        ("Invalid character", "2 + @"),
        ("Invalid number", "3.3.3"),
        ("Invalid function", "son(3)"),
        ("Unmatched parentheses", "2 + (3 * 4"),
        ("Wrong operator usage", "3 + * 2"),
    ]

    for description, expr in test_cases:
        try:
            result = calc.calculate(expr)
            print(f"{description}: {expr} = {result}")
        except Exception as e:
            print(f"{description}: {expr} -> ERROR: {type(e).__name__}: {e}")

    print()


if __name__ == "__main__":
    print("LUPA Calculator Demonstration")
    print("=" * 40)
    print()

    # Run all demos
    demo_basic_calculator()
    calc = demo_custom_constants()
    demo_elastance_function(calc)
    demo_variable_expressions()
    demo_error_handling()

    print("Demo completed!")
