# LUPA Examples

This folder contains demonstration scripts and example files showcasing various LUPA functionalities.

## Calculator Examples

### calculator_demo.py
Comprehensive demonstration of the Calculator class capabilities:
- Basic arithmetic operations
- Mathematical functions (sin, cos, tan, abs, floor, etc.)
- Custom constants for circuit analysis
- Complex expressions with variables
- Elastance function calculation and plotting
- Error handling examples

**Usage:**
```bash
cd examples
python calculator_demo.py
```

## Circuit Examples

### Basic Circuit Files
The following JSON files demonstrate different circuit configurations:

- `simple_rc_circuit.json` - Basic RC circuit example
- `voltage_divider.json` - Voltage divider circuit
- `bridge_circuit.json` - Bridge circuit configuration

### Analysis Scripts

- `circuit_analysis_demo.py` - Demonstrates circuit loading and analysis
- `combined_demo.py` - Shows integration of calculator and circuit analysis

## File Structure

```
examples/
├── __init__.py                 # Package marker
├── README.md                   # This file
├── calculator_demo.py          # Calculator functionality demo
├── circuit_analysis_demo.py    # Circuit analysis demo
├── combined_demo.py           # Combined functionality demo
├── simple_rc_circuit.json     # Basic RC circuit
├── voltage_divider.json       # Voltage divider circuit
└── bridge_circuit.json        # Bridge circuit
```

## Running Examples

All examples can be run from the examples directory:

```bash
cd /path/to/LUPA/examples
python calculator_demo.py
python circuit_analysis_demo.py
python combined_demo.py
```

## Dependencies

Examples may require additional packages:
- numpy
- matplotlib (for plotting examples)
- Any dependencies required by the main LUPA package
