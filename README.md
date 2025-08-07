# LPMS - Lumped-Parameter Model Solver

<div align="center">
  <img src="icons/LPMS_256.png" alt="LPMS Logo" width="128" height="128">
  
  [![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
  [![Status](https://img.shields.io/badge/status-alpha-yellow.svg)](https://github.com/maximerenault/LPMS)
</div>

## Overview

LPMS (Lumped-Parameter Model Solver) is a comprehensive GUI application for electrical circuit simulation and analysis. Built with Python and Tkinter, it provides an intuitive interface for designing, analyzing, and solving lumped-parameter electrical circuits.

## Features

- **Interactive Circuit Design**: Visual circuit editor with drag-and-drop components
- **Component Library**: Support for various electrical components:
  - Resistors (R)
  - Capacitors (C) 
  - Inductors (L)
  - Diodes (D)
  - Voltage Sources (P)
  - Current Sources (Q)
  - Ground connections (G)
- **Advanced Solver**: Robust numerical solver for circuit analysis
- **Time-Domain Simulation**: Support for transient analysis
- **Multiple Integration Methods**: BDF (Backwards Differentiation Formula) and BDF2
- **Export Capabilities**: Save and load circuit configurations
- **Real-time Visualization**: Plot results with matplotlib integration

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install numpy scipy matplotlib pandas networkx
```

### Install via pip (recommended)

```bash
pip install -e .
```

After installation, you can run LPMS from anywhere using:
```bash
lpms
```

### Run from Source

```bash
git clone https://github.com/maximerenault/LPMS.git
cd LPMS
python main.py
```

## Usage

### Command Line Interface

LPMS provides a command line interface with the following options:

```bash
# Start the GUI application
lpms

# Show version
lpms --version

# Show help
lpms --help

# Open a specific circuit file on startup
lpms path/to/circuit.json

# Command-line mode (not yet implemented)
lpms --no-gui
```

### GUI Usage

1. **Start the Application**: Run `lpms` or `python main.py` to launch the GUI
2. **Design Your Circuit**: Use the drawing board to place and connect components
3. **Set Parameters**: Configure component values and simulation settings
4. **Solve**: Run the simulation to analyze your circuit
5. **View Results**: Examine the output plots and data

## Project Structure

```
LPMS/
├── elements/         # Circuit element definitions
├── GUI/              # User interface components
├── solvers/          # Circuit solving algorithms
├── utils/            # Utility functions
├── exceptions/       # Custom exception classes
├── tests/            # Test suite
├── icons/            # Application icons
├── main.py           # Main application entry point
└── pyproject.toml    # Project configuration
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
```

### Type Checking

```bash
mypy .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Maxime Renault**
- GitHub: [@maximerenault](https://github.com/maximerenault)

## Acknowledgments

- Built with Python and Tkinter
- Uses NumPy and SciPy for numerical computations
- Matplotlib for visualization
