"""
WebDriver setup and utility functions.
"""

import sys
import os

# Disable PyCharm debugger tracing to avoid warnings
if 'pydevd' in sys.modules:
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

from config import BOOKING_URL, PAGE_LOAD_WAIT


def create_driver(headless=False):
    """Create and configure a Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(options=options)


def navigate_to_booking_page(driver):
    """Navigate to the booking page and wait for form to load."""
    print("Opening https://konzinfobooking.mfa.gov.hu/...")
    driver.get(BOOKING_URL)
    
    wait = WebDriverWait(driver, PAGE_LOAD_WAIT)
    print("Waiting for page to load...")
    
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        print("Form detected")
    except TimeoutException:
        print("Warning: Form not found, but continuing...")
    
    # Give page extra time to render
    time.sleep(2)
    return wait


def inspect_form_fields(driver):
    """Inspect and print all form fields."""
    print("\n=== Inspecting Form Fields ===")
    
    inputs = driver.find_elements(By.TAG_NAME, "input")
    selects = driver.find_elements(By.TAG_NAME, "select")
    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    
    print(f"Found {len(inputs)} input fields, {len(selects)} select fields, {len(textareas)} textarea fields\n")
    
    # Debug: Print all input fields
    print("All input fields:")
    for i, inp in enumerate(inputs):
        input_type = inp.get_attribute("type") or "text"
        input_id = inp.get_attribute("id")
        input_name = inp.get_attribute("name")
        input_placeholder = inp.get_attribute("placeholder")
        print(f"  [{i}] type='{input_type}', id='{input_id}', name='{input_name}', placeholder='{input_placeholder}'")
    
    return inputs, selects, textareas


def scroll_to_element(driver, element):
    """Scroll an element into view."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.3)

