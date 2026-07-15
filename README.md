# Authorized TCP Port Scanner

## Student Details

- **Name:** Mohit Aggarwal
- **Intern ID:** CITS6527

## Overview

Authorized TCP Port Scanner is a beginner-friendly Python 3 command-line tool that performs TCP connect port scanning using only Python standard library modules. The program is designed for learning, basic network testing, and simple validation of reachable TCP services on systems that the user owns or has explicit permission to assess.

The scanner uses `socket.connect_ex()` to check whether a TCP port is open. It supports scanning a single port, multiple comma-separated ports, and port ranges. It also supports direct IPv4 addresses, hostnames, and `localhost` as targets.

## Ethical Use Notice

This tool must be used **only** on systems that are owned by the user or on systems for which the user has explicit written or verbal permission to test. Unauthorized scanning may be illegal, may violate organizational policies, and may trigger security monitoring or defensive controls.

This project is intentionally limited to safe, beginner-level TCP connect scanning. It does **not** include stealth scanning, SYN scanning, raw packet crafting, OS fingerprinting, vulnerability exploitation, banner grabbing, evasion techniques, or any offensive capability.

## Objectives of the Project

This project was created to demonstrate:

- Safe and basic TCP connect scanning in Python.
- Careful validation of user input.
- Proper hostname and IPv4 resolution.
- Simple concurrency with `ThreadPoolExecutor`.
- Clean command-line design with `argparse`.
- Error-resistant programming with readable messages.
- Unit testing of a core parser function with `unittest`.

## Features

- Accepts target input as:
  - A single IPv4 address, such as `192.168.1.10`
  - A hostname, such as `example.com`
  - `localhost`
- Accepts port input in these formats:
  - Single port, such as `80`
  - Comma-separated list, such as `22,80,443`
  - Range, such as `1-1024`
  - Mixed comma-separated entries with ranges, such as `20-25,53,80,443`
- Validates:
  - Empty target input
  - Invalid IPv4 input
  - Invalid hostname resolution
  - Invalid port syntax
  - Reversed ranges such as `100-10`
  - Ports outside the valid range `1-65535`
  - Invalid timeout and worker values
- Resolves hostnames safely using `socket.gethostbyname()`.
- Creates a fresh socket for each scanned port.
- Uses `socket.AF_INET`, `socket.SOCK_STREAM`, and `connect_ex()`.
- Uses `ThreadPoolExecutor` to improve scan speed while keeping code readable.
- Prints:
  - The target entered by the user
  - The resolved IPv4 address
  - The scan start time
  - Open ports only
  - Total scan duration
- Handles common errors cleanly, including keyboard interruption.

## Technologies and Modules Used

This project uses only Python standard library modules.

| Module | Purpose |
|--------|---------|
| `socket` | TCP socket creation, timeout handling, hostname resolution, and port connection attempts |
| `argparse` | Command-line argument parsing and help text |
| `concurrent.futures` | Concurrent port scanning with `ThreadPoolExecutor` |
| `datetime` | Scan start time and total duration reporting |
| `ipaddress` | IPv4 validation |
| `sys` | Clean exit handling and error output |
| `typing` | Type hints for readability and maintainability |

## Project Structure

```text
authorized_port_scanner/
├── scanner.py
├── requirements.txt
├── README.md
└── tests/
    └── test_ports_parser.py
```

## File Description

### `scanner.py`
This is the main application file. It contains all scanning logic, command-line argument parsing, validation, hostname/IP resolution, threaded scanning, and formatted output.

Main functions included:

- `parse_ports(port_text: str) -> list[int]`
- `resolve_target(target: str) -> str`
- `scan_port(ip: str, port: int, timeout: float) -> tuple[int, bool]`
- `run_scan(ip: str, ports: list[int], timeout: float, workers: int) -> list[int]`
- `build_parser() -> argparse.ArgumentParser`
- `main() -> None`

### `requirements.txt`
This file clearly states that no third-party packages are required.

### `README.md`
This file explains the project, usage, structure, setup steps, and ethical limitations.

### `tests/test_ports_parser.py`
This file contains unit tests for the `parse_ports()` function using Python's built-in `unittest` module.

## How the Scanner Works

The scanner follows a simple workflow:

1. Read command-line arguments.
2. Validate timeout and worker values.
3. Parse and validate the provided port specification.
4. Resolve the target to an IPv4 address.
5. Record the scan start time.
6. Use a thread pool to attempt TCP connections on the requested ports.
7. Collect only the ports where `connect_ex()` returns success.
8. Print the results and the total scan duration.

The scanner does not attempt any low-level or stealth behavior. It performs standard TCP connection attempts in a straightforward and transparent way.

## Setup Instructions

### Prerequisites

- Python 3 installed on the system
- Access to a terminal or command prompt
- Authorization to scan the target system

### Installation Steps

1. Copy or download the project folder.
2. Open a terminal in the project directory.
3. Ensure Python 3 is available:

```bash
python --version
```

4. Move into the project folder:

```bash
cd authorized_port_scanner
```

No package installation is required.

## Usage

### Basic Syntax

```bash
python scanner.py <target> -p <ports> [--timeout VALUE] [--workers VALUE]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `target` | Yes | Hostname, single IPv4 address, or `localhost` |
| `-p`, `--ports` | Yes | Port specification: single port, comma-separated list, or range |
| `--timeout` | No | Socket timeout in seconds, default is `0.5` |
| `--workers` | No | Number of worker threads, default is `100` |

## Example Commands

### Scan a few common ports on localhost

```bash
python scanner.py 127.0.0.1 -p 22,80,443
```

### Scan a port range on localhost

```bash
python scanner.py localhost -p 1-1000 --timeout 0.5 --workers 100
```

### Scan selected ports on a hostname

```bash
python scanner.py example.com -p 80,443 --timeout 1.0 --workers 50
```

### Scan a single port

```bash
python scanner.py 192.168.1.20 -p 3389
```

## Sample Output

```text
Authorized use only: scan systems you own or have explicit permission to test.
Target entered: localhost
Resolved IP: 127.0.0.1
Scan start time: 2026-07-15 20:45:00
Open port: 22
Open port: 80
Total scan duration: 0.214 seconds
```

## Error Handling

The program is designed to return clear and readable error messages.

Examples of handled cases include:

- Invalid hostname
- Invalid IPv4 address
- Invalid port format
- Reversed port range
- Port outside `1-65535`
- Invalid timeout value
- Invalid workers value
- Keyboard interruption by the user
- Socket-related runtime errors

Example error messages:

```text
Error: Invalid hostname or unable to resolve: 'bad-hostname'
```

```text
Error: Invalid IP address: '999.999.999.999'
```

```text
Error: Invalid port range: '100-10' (start is greater than end).
```

```text
Error: Port out of range: '70000' (valid ports are 1-65535).
```

## Testing

This project includes unit tests for the `parse_ports()` function.

### Run Tests

```bash
python -m unittest tests/test_ports_parser.py
```

### Covered Test Cases

- Single port parsing
- Comma-separated port parsing
- Range parsing
- Duplicate removal and sorting
- Reversed range rejection
- Out-of-range low port rejection
- Out-of-range high port rejection
- Invalid text rejection
- Empty segment rejection

## Design Decisions

Several choices were made to keep the project simple, safe, and readable:

- **Standard library only:** avoids hidden dependencies and keeps setup easy.
- **TCP connect scanning only:** safer and easier to understand than raw-packet techniques.
- **Fresh socket per port:** avoids socket reuse issues and keeps behavior predictable.
- **ThreadPoolExecutor:** improves performance for multiple ports while remaining beginner-friendly.
- **Explicit validation:** prevents confusing runtime failures and improves usability.
- **Open ports only in output:** keeps the terminal output clean and focused.

## Limitations

This scanner is intentionally limited in scope.

- It supports IPv4 targets only.
- It performs TCP connect scans only.
- It does not detect service versions.
- It does not identify operating systems.
- It does not perform UDP scanning.
- It does not perform vulnerability assessment.
- Scan speed depends on timeout, network conditions, and target responsiveness.

## Future Safe Improvements

Possible non-offensive improvements that could still keep the project educational and safe include:

- Optional saving of results to a text or CSV file
- Better formatting of console output
- Optional closed-port count summary
- Separate validation tests for `resolve_target()`
- Optional IPv6 support in a future version

## Conclusion

This project is a clean and beginner-friendly example of an authorized TCP connect port scanner implemented in Python 3. It focuses on correctness, readability, safe functionality, and strong input validation while avoiding offensive or advanced scanning behavior.