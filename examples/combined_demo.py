"""
Combined Demo - Calculator and Circuit Analysis
Demonstrates the integration of calculator functionality with circuit analysis
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import os
from utils.calculator import Calculator


def demo_parametric_circuit_analysis():
    """Demonstrate parametric analysis using calculator expressions."""
    print("=== Parametric Circuit Analysis Demo ===")

    # Create calculator with circuit-specific constants
    circuit_constants = {
        "Vcc": 5.0,  # Supply voltage
        "R1": 1000,  # Base resistor value
        "freq": 1000,  # Frequency in Hz
        "pi": np.pi,  # Ensure pi is available
        "e": np.e,  # Ensure e is available
    }

    calc = Calculator(custom_constants=circuit_constants)

    # Define parametric expressions for different R2 values
    print("Voltage Divider Analysis with Variable R2:")
    print("Vout = Vcc * R2 / (R1 + R2)")
    print()

    # Calculate for different R2 values
    R2_values = [500, 1000, 1500, 2000, 2500, 3000]
    results = []

    for R2 in R2_values:
        # Update calculator with current R2 value
        calc.constants["R2"] = R2
        calc._update_tokens()

        # Calculate output voltage
        Vout = calc.calculate("Vcc * R2 / (R1 + R2)")
        Vgain = calc.calculate("R2 / (R1 + R2)")

        results.append((R2, Vout, Vgain))
        print(f"R2 = {R2:4d}Ω  →  Vout = {Vout:.3f}V  →  Gain = {Vgain:.3f}")

    # Plot results
    R2_vals, Vout_vals, Gain_vals = zip(*results)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Output voltage plot
    ax1.plot(R2_vals, Vout_vals, "bo-", linewidth=2, markersize=6)
    ax1.set_xlabel("R2 (Ω)")
    ax1.set_ylabel("Output Voltage (V)")
    ax1.set_title("Voltage Divider Output vs R2")
    ax1.grid(True, alpha=0.3)

    # Gain plot
    ax2.plot(R2_vals, Gain_vals, "ro-", linewidth=2, markersize=6)
    ax2.set_xlabel("R2 (Ω)")
    ax2.set_ylabel("Voltage Gain")
    ax2.set_title("Voltage Gain vs R2")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print()


def demo_frequency_response():
    """Demonstrate frequency response calculation using calculator."""
    print("=== RC Circuit Frequency Response Demo ===")

    # Circuit parameters
    R = 1000  # 1kΩ
    C = 1e-6  # 1µF

    circuit_constants = {"R": R, "C": C, "pi": np.pi}

    calc = Calculator(custom_constants=circuit_constants)

    # Calculate cutoff frequency
    fc = calc.calculate("1 / (2 * pi * R * C)")
    print("RC Circuit Parameters:")
    print(f"R = {R} Ω")
    print(f"C = {C*1e6} µF")
    print(f"Cutoff frequency: {fc:.1f} Hz")
    print()

    # Generate frequency response
    frequencies = np.logspace(0, 4, 100)  # 1 Hz to 10 kHz

    # Calculate magnitude response for each frequency
    magnitudes = []
    phases = []

    for f in frequencies:
        # Update frequency in calculator
        calc.constants["f"] = f
        calc._update_tokens()

        # Calculate transfer function magnitude: |H(jω)| = 1/√(1 + (ωRC)²)
        omega = calc.calculate("2 * pi * f")
        calc.constants["omega"] = omega
        calc._update_tokens()

        calc.functions["log10"] = np.log10
        calc._update_tokens()

        magnitude_db = calc.calculate(
            "20 * log10(1 / (1 + (omega * R * C) ** 2) ** 0.5)"
        )
        phase = calc.calculate("-atan(omega * R * C) * 180 / pi")

        magnitudes.append(magnitude_db)
        phases.append(phase)

    # Add log10 function to calculator for dB calculation
    calc.functions["log10"] = np.log10
    calc.functions["atan"] = np.arctan
    calc._update_tokens()

    # Recalculate with log function available
    magnitudes = []
    phases = []

    for f in frequencies:
        calc.constants["f"] = f
        calc.constants["omega"] = 2 * np.pi * f
        calc._update_tokens()

        magnitude_db = calc.calculate(
            "20 * log10(1 / (1 + (omega * R * C) ** 2) ** 0.5)"
        )
        phase = calc.calculate("-atan(omega * R * C) * 180 / pi")

        magnitudes.append(magnitude_db)
        phases.append(phase)

    # Plot frequency response
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # Magnitude plot
    ax1.semilogx(frequencies, magnitudes, "b-", linewidth=2)
    ax1.axvline(fc, color="r", linestyle="--", alpha=0.7, label=f"fc = {fc:.1f} Hz")
    ax1.axhline(-3, color="r", linestyle="--", alpha=0.7, label="-3dB")
    ax1.set_ylabel("Magnitude (dB)")
    ax1.set_title("RC Low-Pass Filter Frequency Response")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Phase plot
    ax2.semilogx(frequencies, phases, "g-", linewidth=2)
    ax2.axvline(fc, color="r", linestyle="--", alpha=0.7)
    ax2.axhline(-45, color="r", linestyle="--", alpha=0.7, label="-45°")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Phase (degrees)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plt.show()

    print(f"At cutoff frequency ({fc:.1f} Hz):")
    calc.constants["f"] = fc
    calc.constants["omega"] = 2 * np.pi * fc
    calc._update_tokens()

    mag_at_fc = calc.calculate("20 * log10(1 / (1 + (omega * R * C) ** 2) ** 0.5)")
    phase_at_fc = calc.calculate("-atan(omega * R * C) * 180 / pi")

    print(f"Magnitude: {mag_at_fc:.1f} dB")
    print(f"Phase: {phase_at_fc:.1f}°")
    print()


def demo_circuit_optimization():
    """Demonstrate circuit optimization using calculator expressions."""
    print("=== Circuit Optimization Demo ===")

    # Find optimal R2 for specific voltage output
    target_voltage = 3.3  # Target 3.3V output
    Vcc = 5.0
    R1 = 1000

    calc = Calculator(
        custom_constants={"Vcc": Vcc, "R1": R1, "Vtarget": target_voltage}
    )

    # Solve for R2: Vout = Vcc * R2 / (R1 + R2) = Vtarget
    # Rearranging: R2 = R1 * Vtarget / (Vcc - Vtarget)
    R2_optimal = calc.calculate("R1 * Vtarget / (Vcc - Vtarget)")

    print("Voltage Divider Optimization:")
    print(f"Target output: {target_voltage}V from {Vcc}V supply")
    print(f"Given R1 = {R1}Ω")
    print(f"Calculated optimal R2 = {R2_optimal:.1f}Ω")

    # Verify the calculation
    calc.add_constants({"R2": R2_optimal})
    actual_voltage = calc.calculate("Vcc * R2 / (R1 + R2)")
    error = calc.calculate("abs(Vtarget - Vcc * R2 / (R1 + R2))")

    print(f"Verification: Actual output = {actual_voltage:.6f}V")
    print(f"Error: {error:.6f}V")
    print()

    # Power analysis
    current = calc.calculate("Vcc / (R1 + R2)")
    calc.add_constants({"current": current})
    power_R1 = calc.calculate("current * current * R1")
    power_R2 = calc.calculate("current * current * R2")
    calc.add_constants({"power_R1": power_R1, "power_R2": power_R2})
    power_total = calc.calculate("power_R1 + power_R2")
    calc.add_constants({"power_total": power_total})

    print("Power Analysis:")
    print(f"Current: {current:.6f}A")
    print(f"Power in R1: {power_R1:.6f}W")
    print(f"Power in R2: {power_R2:.6f}W")
    print(f"Total power: {power_total:.6f}W")
    print()


def load_and_enhance_circuit(filename):
    """Load circuit and enhance with calculator-based analysis."""
    print(f"=== Enhanced Analysis: {filename} ===")

    try:
        with open(filename, "r") as f:
            circuit = json.load(f)
    except FileNotFoundError:
        print(f"Circuit file {filename} not found")
        return None

    print(f"Circuit: {circuit.get('name', 'Unnamed')}")

    # Extract component values and create calculator constants
    constants = {}
    components = circuit.get("components", {})

    for comp_name, comp_data in components.items():
        value = comp_data.get("value", "0")
        try:
            # Try to convert to float
            numeric_value = float(value)
            constants[comp_name] = numeric_value
        except ValueError:
            # If it's an expression, keep as string for later evaluation
            constants[comp_name + "_expr"] = value

    # Create enhanced calculator
    calc = Calculator(custom_constants=constants)

    # Perform enhanced analysis based on circuit type
    if "voltage_divider" in filename:
        if "R1" in constants and "R2" in constants and "V1" in constants:
            Vout = calc.calculate("V1 * R2 / (R1 + R2)")
            efficiency = calc.calculate("(V1 * R2 / (R1 + R2)) / V1 * 100")
            print("Enhanced Analysis Results:")
            print(f"Output voltage: {Vout:.3f}V")
            print(f"Efficiency: {efficiency:.1f}%")

    elif "rc_circuit" in filename:
        if "R1" in constants and "C1" in constants:
            tau = calc.calculate("R1 * C1")
            freq_3db = calc.calculate("1 / (2 * pi * R1 * C1)")
            print("Enhanced Analysis Results:")
            print(f"Time constant: {tau:.6g}s")
            print(f"3dB frequency: {freq_3db:.3f}Hz")

    print()
    return circuit


if __name__ == "__main__":
    print("LUPA Combined Demo - Calculator + Circuit Analysis")
    print("=" * 55)
    print()

    # Change to examples directory
    examples_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(examples_dir)

    try:
        # Run all demos
        demo_parametric_circuit_analysis()
        print("=" * 55)

        demo_frequency_response()
        print("=" * 55)

        demo_circuit_optimization()
        print("=" * 55)

        # Enhanced circuit analysis
        for circuit_file in ["voltage_divider.json", "simple_rc_circuit.json"]:
            load_and_enhance_circuit(circuit_file)

    except Exception as e:
        print(f"Demo error: {e}")
        import traceback

        traceback.print_exc()

    print("Combined demo completed!")
