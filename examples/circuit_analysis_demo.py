"""
Circuit Analysis Demo
Demonstrates loading and analyzing circuit JSON files with LUPA
"""

import json
import sys
import os

# Add parent directory to path to import LUPA modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.calculator import Calculator


def load_circuit(filename):
    """Load a circuit from JSON file."""
    try:
        with open(filename, "r") as f:
            circuit = json.load(f)
        print(f"✓ Successfully loaded circuit: {circuit.get('name', 'Unnamed')}")
        return circuit
    except FileNotFoundError:
        print(f"✗ Circuit file not found: {filename}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in {filename}: {e}")
        return None


def analyze_circuit_values(circuit):
    """Analyze circuit component values using the calculator."""
    print(f"\n=== Circuit Analysis: {circuit.get('name', 'Unnamed')} ===")
    print(f"Description: {circuit.get('description', 'No description')}")

    # Create calculator for component value calculations
    calc = Calculator()

    components = circuit.get("components", {})
    print(f"\nComponents ({len(components)} total):")

    total_resistance = 0
    total_capacitance = 0

    for comp_name, comp_data in components.items():
        comp_type = comp_data.get("type", "unknown")
        value = comp_data.get("value", "0")
        unit = comp_data.get("unit", "")
        nodes = comp_data.get("nodes", [])

        print(f"  {comp_name}: {comp_type}")
        print(f"    Value: {value} {unit}")
        print(f"    Nodes: {' -> '.join(nodes)}")

        # Calculate numeric value if possible
        try:
            numeric_value = calc.calculate(str(value))
            print(f"    Calculated: {numeric_value:.6g} {unit}")

            # Sum up resistances and capacitances for basic analysis
            if comp_type == "resistor":
                total_resistance += numeric_value
            elif comp_type == "capacitor":
                total_capacitance += numeric_value

        except Exception as e:
            print(f"    Calculation error: {e}")

        print()

    # Basic circuit analysis
    if total_resistance > 0:
        print(f"Total resistance: {total_resistance:.6g} ohms")
    if total_capacitance > 0:
        print(f"Total capacitance: {total_capacitance:.6g} farads")
        if total_resistance > 0:
            time_constant = total_resistance * total_capacitance
            print(f"RC time constant: {time_constant:.6g} seconds")


def analyze_voltage_divider():
    """Specific analysis for voltage divider circuit."""
    circuit = load_circuit("voltage_divider.json")
    if not circuit:
        return

    analyze_circuit_values(circuit)

    # Specific voltage divider calculations
    calc = Calculator()

    # Extract component values
    components = circuit["components"]
    R1 = float(components["R1"]["value"])
    R2 = float(components["R2"]["value"])
    Vin = float(components["V1"]["value"])

    # Calculate output voltage using voltage divider formula
    Vout = calc.calculate(f"{Vin} * {R2} / ({R1} + {R2})")
    current = calc.calculate(f"{Vin} / ({R1} + {R2})")
    power_total = calc.calculate(f"{Vin} * {current}")

    print("=== Voltage Divider Analysis ===")
    print(f"Input voltage: {Vin} V")
    print(f"R1: {R1} Ω")
    print(f"R2: {R2} Ω")
    print(f"Output voltage: {Vout:.3f} V")
    print(f"Current: {current:.6f} A")
    print(f"Total power: {power_total:.6f} W")
    print(f"Voltage ratio: {Vout/Vin:.3f}")


def analyze_rc_circuit():
    """Specific analysis for RC circuit."""
    circuit = load_circuit("simple_rc_circuit.json")
    if not circuit:
        return

    analyze_circuit_values(circuit)

    # RC-specific calculations
    calc = Calculator()

    components = circuit["components"]
    R = float(components["R1"]["value"])
    C = float(components["C1"]["value"])
    V = float(components["V1"]["value"])

    # Calculate time constant and other RC parameters
    tau = calc.calculate(f"{R} * {C}")
    f_3db = calc.calculate(f"1 / (2 * pi * {tau})")

    print("=== RC Circuit Analysis ===")
    print(f"Resistance: {R} Ω")
    print(f"Capacitance: {C} F")
    print(f"Supply voltage: {V} V")
    print(f"Time constant (τ): {tau:.6g} s")
    print(f"3dB frequency: {f_3db:.3f} Hz")
    print(f"Time to 63.2% charge: {tau:.6g} s")
    print(f"Time to 95% charge: {3*tau:.6g} s")


def analyze_bridge_circuit():
    """Specific analysis for bridge circuit."""
    circuit = load_circuit("bridge_circuit.json")
    if not circuit:
        return

    analyze_circuit_values(circuit)

    # Bridge-specific calculations
    calc = Calculator()

    components = circuit["components"]
    R1 = float(components["R1"]["value"])
    R2 = float(components["R2"]["value"])
    R3 = float(components["R3"]["value"])
    R4 = float(components["R4"]["value"])
    V = float(components["V1"]["value"])

    # Calculate bridge voltages and balance condition
    Vb = calc.calculate(f"{V} * {R2} / ({R1} + {R2})")  # Voltage at node B
    Vc = calc.calculate(f"{V} * {R4} / ({R3} + {R4})")  # Voltage at node C
    Vbridge = calc.calculate(f"{Vb} - {Vc}")  # Bridge voltage

    # Balance condition
    ratio1 = calc.calculate(f"{R1} / {R3}")
    ratio2 = calc.calculate(f"{R2} / {R4}")

    print("=== Bridge Circuit Analysis ===")
    print(f"R1: {R1} Ω,  R2: {R2} Ω")
    print(f"R3: {R3} Ω,  R4: {R4} Ω")
    print(f"Supply voltage: {V} V")
    print(f"Voltage at B: {Vb:.3f} V")
    print(f"Voltage at C: {Vc:.3f} V")
    print(f"Bridge voltage (B-C): {Vbridge:.3f} V")
    print(f"Ratio R1/R3: {ratio1:.3f}")
    print(f"Ratio R2/R4: {ratio2:.3f}")

    if abs(ratio1 - ratio2) < 0.001:
        print("✓ Bridge is BALANCED")
    else:
        print("✗ Bridge is UNBALANCED")
        print(f"Balance error: {abs(ratio1 - ratio2):.6f}")


def list_available_circuits():
    """List all available circuit files."""
    circuit_files = ["simple_rc_circuit.json", "voltage_divider.json", "bridge_circuit.json"]

    print("=== Available Circuit Examples ===")
    for filename in circuit_files:
        if os.path.exists(filename):
            circuit = load_circuit(filename)
            if circuit:
                print(f"✓ {filename}: {circuit.get('name', 'Unnamed')}")
        else:
            print(f"✗ {filename}: File not found")
    print()


if __name__ == "__main__":
    print("LUPA Circuit Analysis Demonstration")
    print("=" * 40)
    print()

    # Change to examples directory if not already there
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(examples_dir)

    # List available circuits
    list_available_circuits()

    # Analyze each circuit type
    try:
        analyze_voltage_divider()
        print("\n" + "=" * 50 + "\n")

        analyze_rc_circuit()
        print("\n" + "=" * 50 + "\n")

        analyze_bridge_circuit()
        print("\n" + "=" * 50 + "\n")

    except Exception as e:
        print(f"Analysis error: {e}")

    print("Circuit analysis demo completed!")
