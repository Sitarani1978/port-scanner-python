"""Unit tests for parse_ports()."""

import unittest

from scanner import parse_ports


class TestParsePorts(unittest.TestCase):
    """Tests for the parse_ports function."""

    def test_single_port(self) -> None:
        self.assertEqual(parse_ports("80"), [80])

    def test_comma_separated_ports(self) -> None:
        self.assertEqual(parse_ports("22,80,443"), [22, 80, 443])

    def test_range(self) -> None:
        self.assertEqual(parse_ports("5-8"), [5, 6, 7, 8])

    def test_mixed_and_duplicates(self) -> None:
        self.assertEqual(parse_ports("80,22,80,20-22"), [20, 21, 22, 80])

    def test_reject_reversed_range(self) -> None:
        with self.assertRaises(ValueError):
            parse_ports("100-10")

    def test_reject_out_of_range_low(self) -> None:
        with self.assertRaises(ValueError):
            parse_ports("0")

    def test_reject_out_of_range_high(self) -> None:
        with self.assertRaises(ValueError):
            parse_ports("65536")

    def test_reject_invalid_text(self) -> None:
        with self.assertRaises(ValueError):
            parse_ports("abc")

    def test_reject_empty_segment(self) -> None:
        with self.assertRaises(ValueError):
            parse_ports("22,,80")


if __name__ == "__main__":
    unittest.main()