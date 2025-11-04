"""
WebDriver setup and utility functions.
"""

import sys
import os
import random

# Disable PyCharm debugger tracing to avoid warnings
if 'pydevd' in sys.modules:
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

from config import BOOKING_URL, PAGE_LOAD_WAIT


def create_driver(headless=False):
    """Create and configure a Chrome WebDriver instance with anti-detection measures."""
    if UC_AVAILABLE:
        # Try undetected-chromedriver first, fall back to regular selenium on error
        try:
            # Use undetected-chromedriver for better anti-detection
            options = uc.ChromeOptions()
            if headless:
                options.add_argument('--headless=new')  # Use new headless mode
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
            
            # Additional stealth options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-site-isolation-trials')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Randomize window size to avoid fingerprinting
            width = random.randint(1280, 1920)
            height = random.randint(720, 1080)
            options.add_argument(f'--window-size={width},{height}')
            
            # Create driver with undetected_chromedriver (let it auto-detect version)
            driver = uc.Chrome(options=options, use_subprocess=True)
            
            # Remove webdriver property
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                    window.chrome = {
                        runtime: {}
                    };
                    Object.defineProperty(navigator, 'permissions', {
                        get: () => ({
                            query: () => Promise.resolve({ state: 'granted' })
                        })
                    });
                '''
            })
            
            return driver
        except Exception as e:
            print(f"Warning: undetected-chromedriver failed ({e}), falling back to regular selenium with stealth")
            # Fall through to regular selenium implementation
    
    # Fallback to regular selenium with manual anti-detection (used if UC not available or fails)
    options = webdriver.ChromeOptions()
    
    # Anti-detection arguments
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-site-isolation-trials')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Random user agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    if headless:
        options.add_argument('--headless=new')
    
    # Randomize window size
    width = random.randint(1280, 1920)
    height = random.randint(720, 1080)
    options.add_argument(f'--window-size={width},{height}')
    
    driver = webdriver.Chrome(options=options)
    
    # Remove webdriver property and add stealth scripts
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            window.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
        '''
    })
    
    return driver


def navigate_to_booking_page(driver):
    """Navigate to the booking page and wait for form to load."""
    print("Opening https://konzinfobooking.mfa.gov.hu/...")
    
    # Add random delay before navigation to simulate human behavior
    time.sleep(random.uniform(1, 3))
    
    driver.get(BOOKING_URL)
    
    wait = WebDriverWait(driver, PAGE_LOAD_WAIT)
    print("Waiting for page to load...")
    
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
        print("Form detected")
    except TimeoutException:
        print("Warning: Form not found, but continuing...")
    
    # Give page extra time to render with random delay
    time.sleep(random.uniform(2, 4))
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
    """Scroll an element into view with human-like behavior."""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
    # Random delay to simulate human scrolling speed
    time.sleep(random.uniform(0.3, 0.7))


