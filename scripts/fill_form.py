#!/usr/bin/env python3
"""
CLI entry point for running the embassy-eye form filler.
"""

import sys
import os
from embassy_eye.runner import fill_booking_form


def main():
    """Execute the booking workflow."""
    # Allow scraper selection via command line argument or environment variable
    scraper = "hungary"  # Default
    location = "subotica"  # Default
    
    if len(sys.argv) > 1:
        scraper = sys.argv[1]
    elif os.getenv("SCRAPER"):
        scraper = os.getenv("SCRAPER")
    
    # Allow location selection for Hungary scraper via second argument or environment variable
    if scraper == "hungary":
        if len(sys.argv) > 2:
            location = sys.argv[2]
        elif os.getenv("HUNGARY_LOCATION"):
            location = os.getenv("HUNGARY_LOCATION")
    
    fill_booking_form(scraper, location=location)


if __name__ == "__main__":
    main()

