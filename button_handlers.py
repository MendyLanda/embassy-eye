"""
Handler functions for finding and clicking buttons.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from webdriver_utils import scroll_to_element


def find_next_button(driver):
    """Find the 'Select date' button or similar next/submit button."""
    print("Looking for 'Select date' button...")
    next_button = None
    
    # Try to find button by text "Select date" or "Dátum"
    try:
        next_button = driver.find_element(
            By.XPATH,
            "//button[contains(text(), 'Select date') or contains(text(), 'Dátum')]"
        )
        return next_button
    except:
        pass
    
    # Try to find by button text containing "date"
    if not next_button:
        try:
            next_button = driver.find_element(
                By.XPATH,
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'date')]"
            )
            return next_button
        except:
            pass
    
    # Try to find any button with submit type
    if not next_button:
        try:
            next_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            return next_button
        except:
            pass
    
    # List all buttons for debugging and try to match
    if not next_button:
        print("Button not found by text. Listing all buttons:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            btn_text = btn.text.strip()
            btn_id = btn.get_attribute("id")
            btn_class = btn.get_attribute("class")
            print(f"  - Button: id='{btn_id}', class='{btn_class}', text='{btn_text}'")
            # Try to match any button that looks like a next/submit button
            if btn_text and (">>" in btn_text or "»" in btn_text or "next" in btn_text.lower() or "date" in btn_text.lower()):
                next_button = btn
                print(f"    → Selected this button as next button")
                break
    
    return next_button


def click_next_button(driver):
    """Click the next button (using JavaScript to prevent form submission)."""
    next_button = find_next_button(driver)
    
    if next_button:
        print(f"Found button: '{next_button.text}'")
        print("Clicking button (form will NOT be submitted)...")
        
        # Scroll to button
        scroll_to_element(driver, next_button)
        time.sleep(0.5)
        
        # Click using JavaScript to prevent form submission
        driver.execute_script("arguments[0].click();", next_button)
        print("Button clicked (via JavaScript to prevent submission)")
        
        return True
    else:
        print("Next button not found!")
        return False

