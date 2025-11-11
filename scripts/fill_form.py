#!/usr/bin/env python3
"""
CLI entry point for running the embassy-eye form filler.
"""

from embassy_eye.runner import fill_booking_form


def main():
    """Execute the booking workflow."""
    fill_booking_form()


if __name__ == "__main__":
    main()

