#!/usr/bin/env python3
"""
Main runner that delegates to country-specific scrapers.
"""

import sys
import os

# Import country-specific scrapers
from ..scrapers.hungary.runner import fill_booking_form as fill_hungary_form, fill_booking_form_both_locations
from ..scrapers.italy.runner import fill_italy_login_form


def fill_booking_form(scraper="hungary", location="tel_aviv"):
    """
    Fill the booking form using the specified scraper.
    
    Args:
        scraper: The scraper to use ('hungary' or 'italy'). Defaults to 'hungary'.
        location: For Hungary scraper, either 'subotica', 'belgrade', 'tel_aviv', or 'both'. Defaults to 'tel_aviv'.
    """
    scraper = scraper.lower()
    location = location.lower()
    
    if scraper == "hungary":
        if location == "both":
            fill_booking_form_both_locations()
        else:
            fill_hungary_form(location=location)
    elif scraper == "italy":
        fill_italy_login_form()
    else:
        print(f"✗ Error: Unknown scraper '{scraper}'. Available scrapers: 'hungary', 'italy'")
        sys.stdout.flush()
        return


if __name__ == "__main__":
    # Allow scraper selection via command line argument or environment variable
    scraper = "hungary"  # Default
    location = "tel_aviv"  # Default
    
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
