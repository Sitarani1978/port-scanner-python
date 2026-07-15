"""Authorized TCP connect port scanner.

Warning:
    Use this tool only on systems you own or have explicit permission to test.
    Unauthorized scanning may be illegal or violate network policies.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import ipaddress
import socket
import sys
from typing import Iterable


WARNING_TEXT = (
    "Authorized use only: scan systems you own or have explicit permission to test."
)


def parse_ports(port_text: str) -> list[int]:
    """Parse a port specification into a sorted list of unique ports.

    Supports a single port ("80"), a comma-separated list ("22,80,443"),
    or a range ("1-1024"). Mixed comma-separated ranges are also supported.

    Args:
        port_text: Text entered by the user that describes one or more ports.

    Returns:
        A sorted list of unique port numbers.

    Raises:
        ValueError: If the format is invalid, a range is reversed, or a port is
            outside the valid range of 1 to 65535.
    """
    if not port_text or not port_text.strip():
        raise ValueError("Invalid port format: value cannot be empty.")

    ports: set[int] = set()
    parts = [part.strip() for part in port_text.split(",")]

    if any(part == "" for part in parts):
        raise ValueError("Invalid port format: empty port entry found.")

    for part in parts:
        if "-" in part:
            range_parts = [item.strip() for item in part.split("-")]
            if len(range_parts) != 2 or not range_parts[0] or not range_parts[1]:
                raise ValueError(f"Invalid port format: '{part}'.")
            if not range_parts[0].isdigit() or not range_parts[1].isdigit():
                raise ValueError(f"Invalid port format: '{part}'.")

            start = int(range_parts[0])
            end = int(range_parts[1])

            if start > end:
                raise ValueError(
                    f"Invalid port range: '{part}' (start is greater than end)."
                )
            if start < 1 or end > 65535:
                raise ValueError(
                    f"Port out of range in '{part}': valid ports are 1-65535."
                )

            ports.update(range(start, end + 1))
        else:
            if not part.isdigit():
                raise ValueError(f"Invalid port format: '{part}'.")

            port = int(part)
            if port < 1 or port > 65535:
                raise ValueError(
                    f"Port out of range: '{port}' (valid ports are 1-65535)."
                )
            ports.add(port)

    return sorted(ports)


def resolve_target(target: str) -> str:
    """Resolve a user-provided target into an IPv4 address string.

    Accepts localhost, a direct IPv4 address, or a hostname resolvable through
    DNS with socket.gethostbyname().

    Args:
        target: The target entered by the user.

    Returns:
        A resolved IPv4 address as a string.

    Raises:
        ValueError: If the target is empty, not a valid IPv4 address, or the
            hostname cannot be resolved.
    """
    cleaned_target = target.strip()
    if not cleaned_target:
        raise ValueError("Invalid hostname: target cannot be empty.")

    if cleaned_target.lower() == "localhost":
        return "127.0.0.1"

    try:
        ipaddress.IPv4Address(cleaned_target)
        return cleaned_target
    except ipaddress.AddressValueError:
        if all(char.isdigit() or char == "." for char in cleaned_target):
            raise ValueError(f"Invalid IP address: '{cleaned_target}'.") from None

    try:
        return socket.gethostbyname(cleaned_target)
    except socket.gaierror as exc:
        raise ValueError(
            f"Invalid hostname or unable to resolve: '{cleaned_target}'."
        ) from exc
    except OSError as exc:
        raise ValueError(f"Socket-related error while resolving target: {exc}") from exc


def scan_port(ip: str, port: int, timeout: float) -> tuple[int, bool]:
    """Attempt a TCP connect scan for a single port.

    Args:
        ip: Target IPv4 address.
        port: TCP port number to scan.
        timeout: Socket timeout in seconds.

    Returns:
        A tuple of (port, is_open).

    Raises:
        OSError: If a socket-related error occurs while setting up the socket.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        return port, result == 0


def run_scan(ip: str, ports: list[int], timeout: float, workers: int) -> list[int]:
    """Scan multiple ports concurrently and return open ports.

    Args:
        ip: Target IPv4 address.
        ports: Ports to scan.
        timeout: Socket timeout in seconds.
        workers: Number of worker threads.

    Returns:
        A sorted list of open ports.

    Raises:
        OSError: If a socket-related error occurs during scanning.
    """
    open_ports: list[int] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_port = {
            executor.submit(scan_port, ip, port, timeout): port for port in ports
        }

        for future in concurrent.futures.as_completed(future_to_port):
            port, is_open = future.result()
            if is_open:
                open_ports.append(port)

    return sorted(open_ports)


def build_parser() -> argparse.ArgumentParser:
    """Build and return the command-line argument parser."""
    description = (
        "Beginner-friendly authorized TCP connect port scanner using Python's "
        "standard library only. "
        "Use only on systems you own or have explicit permission to test."
    )

    parser = argparse.ArgumentParser(
        description=description,
        epilog=WARNING_TEXT,
    )
    parser.add_argument(
        "target",
        help="Target hostname, single IPv4 address, or localhost.",
    )
    parser.add_argument(
        "-p",
        "--ports",
        required=True,
        help=(
            "Port selection: single port (80), comma-separated list "
            "(22,80,443), or range (1-1024)."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.5,
        help=(
            "Socket timeout in seconds. Use only on authorized targets. "
            "Default: 0.5"
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=100,
        help="Number of worker threads to use. Default: 100",
    )
    return parser


def _validate_positive_float(value: float, name: str) -> None:
    """Validate that a float argument is greater than zero."""
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0.")


def _validate_positive_int(value: int, name: str) -> None:
    """Validate that an integer argument is greater than zero."""
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0.")


def _print_open_ports(open_ports: Iterable[int]) -> None:
    """Print discovered open ports in a user-friendly format."""
    found_any = False
    for port in open_ports:
        found_any = True
        print(f"Open port: {port}")
    if not found_any:
        print("No open ports found in the specified set.")


def main() -> None:
    """Parse arguments, validate input, and run the port scan."""
    parser = build_parser()

    try:
        args = parser.parse_args()
        _validate_positive_float(args.timeout, "Timeout")
        _validate_positive_int(args.workers, "Workers")

        ports = parse_ports(args.ports)
        resolved_ip = resolve_target(args.target)

        start_dt = datetime.datetime.now()
        start_perf = datetime.datetime.now()

        print(WARNING_TEXT)
        print(f"Target entered: {args.target}")
        print(f"Resolved IP: {resolved_ip}")
        print(f"Scan start time: {start_dt.isoformat(sep=' ', timespec='seconds')}")

        open_ports = run_scan(resolved_ip, ports, args.timeout, args.workers)
        _print_open_ports(open_ports)

        duration = datetime.datetime.now() - start_perf
        print(f"Total scan duration: {duration.total_seconds():.3f} seconds")

    except KeyboardInterrupt:
        print("Scan interrupted by user.", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Socket-related error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()