#!/usr/bin/env python3
"""
Script to fill the booking form on konzinfobooking.mfa.gov.hu
"""

import time

from webdriver_utils import create_driver, navigate_to_booking_page, inspect_form_fields
from dropdown_handlers import select_consulate_option, select_visa_type_option
from form_helpers import (
    fill_select_dropdowns,
    fill_reenter_email_field,
    fill_fields_by_map,
    fill_remaining_fields,
    fill_textareas
)
from button_handlers import click_next_button
from modal_checker import check_appointment_availability
from config import INSPECTION_TIME


def fill_booking_form():
    """Fill the booking form with acceptable values and click save (without submitting)"""
    
    # Initialize Chrome driver
    driver = create_driver(headless=False)
    
    try:
        # Navigate to the booking page
        wait = navigate_to_booking_page(driver)
        
        # Inspect form fields
        inputs, selects, textareas = inspect_form_fields(driver)
        
        print("\n=== Filling Form Fields ===\n")
        
        # Step 1: Select consulate option (Serbia - Subotica)
        select_consulate_option(driver)
        
        # Step 2: Select visa type option
        select_visa_type_option(driver)
        
        # Fill standard HTML select dropdowns
        fill_select_dropdowns(driver, selects)
        
        # Fill form fields with default data
        print("\n=== Filling Form Fields with Default Data ===")
        filled_count = 0
        
        # Fill re-enter email field (special handling)
        filled_count += fill_reenter_email_field(driver)
        
        # Fill fields by field map
        filled_count += fill_fields_by_map(driver)
        
        # Fill any remaining fields
        filled_count += fill_remaining_fields(driver, inputs)
        
        # Fill textareas
        filled_count += fill_textareas(driver, textareas, wait)
        
        print(f"\n=== Summary: Filled {filled_count} field(s) ===\n")
        
        # Click the next button
        if click_next_button(driver):
            # Check for appointment availability
            check_appointment_availability(driver)
        
        # Keep browser open for inspection
        print(f"\nKeeping browser open for {INSPECTION_TIME} seconds for inspection...")
        print("Press Ctrl+C in terminal to close early")
        time.sleep(INSPECTION_TIME)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing browser...")
        driver.quit()


if __name__ == "__main__":
    fill_booking_form()
