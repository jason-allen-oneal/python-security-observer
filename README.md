# python-security-observer

A tool to submit a scan to Mozilla's HTTP Security Observatory and display the results, with both CLI and GUI interfaces.

## Features
- Submits domains to Mozilla's HTTP Observatory for security analysis
- CLI and modern GUI (PySide6) modes
- Verbose output and result saving
- Progress and summary display

## Requirements
- Python 3.7+
- See `requirements.txt` for dependencies:
  - rich
  - colorama
  - requests
  - PySide6

## Installation
```bash
pip3 install -r requirements.txt
```

## Usage

### Command-Line Interface (CLI)
Run a scan from the terminal:
```bash
python3 main.py --cli -u example.com
```

#### Options:
- `-u`, `--url` **TARGET**: Domain on which to perform tests. (REQUIRED)
- `-v`, `--verbose`: Show all output
- `-o`, `--out` **FILE**: File to which to write the program's output
- `-h`, `--help`: Show help message and exit
- `--version`: Show program's version number and exit

#### Example:
```bash
python3 main.py --cli -u www.example.com -v -o results.txt
```

### Graphical User Interface (GUI)
Just run:
```bash
python3 main.py
```
- Enter the domain, select options, and click "Start Scan".
- Optionally, save results to a file.

## Configuration
Some settings can be changed in `config.py`, such as:
- API base URL and timeout
- Scan check interval and cooldown
- Output format
- Logging level

## Project Structure
- `main.py`: Entry point for CLI/GUI
- `gui.py`: GUI implementation
- `scanner.py`: Handles scan logic and API calls
- `utils.py`: Utility functions and output formatting
- `config.py`: Configuration settings

## Contact
Created by z3r0POINTz3r0. For issues, open a GitHub issue or contact the author.

```
Usage: main.py [options]
example: python3 main.py -u www.example.com

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         Show all output
  -u TARGET, --url=TARGET
                        Domain on which to perform tests. (REQUIRED)
  -o WRITE, --out=WRITE
                        File to which to write the program's output
```
