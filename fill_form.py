#!/usr/bin/env python3
"""
Script to fill the booking form on konzinfobooking.mfa.gov.hu
"""

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
from telegram_notifier import send_result_notification
from pathlib import Path


def fill_booking_form():
    """Fill the booking form with acceptable values and click save (without submitting)"""
    
    # Initialize Chrome driver
    driver = create_driver(headless=True)
    
    try:
        # Navigate to the booking page
        wait = navigate_to_booking_page(driver)
        
        # Inspect form fields
        inputs, selects, textareas = inspect_form_fields(driver)

        print("\n=== Parsing started ===\n")
        
        # Step 1: Select consulate option (Serbia - Subotica)
        select_consulate_option(driver)
        
        # Step 2: Select visa type option
        select_visa_type_option(driver)
        
        # Fill standard HTML select dropdowns
        fill_select_dropdowns(driver, selects)
        
        # Fill form fields with default data
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
        
        # If nothing was filled, persist the current page HTML once for offline inspection
        if filled_count == 0:
            html_path = Path("screenshots/filled_0_fields.html")
            try:
                if not html_path.exists():
                    html_path.parent.mkdir(parents=True, exist_ok=True)
                    with html_path.open("w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print(f"Saved HTML to {html_path}")
                else:
                    print(f"HTML already exists at {html_path}, skipping download")
            except Exception as e:
                print(f"Failed to save HTML: {e}")
        
        # Click the next button
        slots_available = None
        if click_next_button(driver):
            # Check for appointment availability
            slots_available = check_appointment_availability(driver)
            
            # Only send notification if slots are found
            if slots_available:
                screenshot_bytes = driver.get_screenshot_as_png()
                send_result_notification(slots_available, screenshot_bytes)
        
        # Keep browser open for inspection (only if not headless)
        # Since we're in headless mode, skip the inspection delay
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing browser...")
        driver.quit()


if __name__ == "__main__":
    fill_booking_form()
