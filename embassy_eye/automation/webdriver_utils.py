"""
WebDriver setup and utility functions.
"""

import sys
import os
import random
import json
import time
import threading
import base64

# Disable PyCharm debugger tracing to avoid warnings
if 'pydevd' in sys.modules:
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

from ..scrapers.hungary.config import BOOKING_URL, PAGE_LOAD_WAIT
import os


# Large pool of realistic, up-to-date user agents (2024-2025)
USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    
    # Chrome on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    
    # Chrome on Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    
    # Edge on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    
    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0',
    
    # Firefox on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0',
    
    # Safari on macOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15',
]

# Common screen resolutions
SCREEN_RESOLUTIONS = [
    (1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1280, 720),
    (1600, 900), (2560, 1440), (1920, 1200), (1680, 1050), (1280, 1024),
    (2560, 1600), (3840, 2160), (2048, 1152), (1920, 1080), (1360, 768),
]

# Common timezones
TIMEZONES = [
    'America/New_York', 'America/Los_Angeles', 'America/Chicago', 'America/Denver',
    'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome', 'Europe/Madrid',
    'Europe/Amsterdam', 'Europe/Vienna', 'Europe/Budapest', 'Europe/Prague',
    'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Hong_Kong', 'Asia/Singapore',
    'Australia/Sydney', 'Australia/Melbourne',
]

# Common languages
LANGUAGES = [
    ['en-US', 'en'], ['en-GB', 'en'], ['de-DE', 'de', 'en'], ['fr-FR', 'fr', 'en'],
    ['es-ES', 'es', 'en'], ['it-IT', 'it', 'en'], ['pt-BR', 'pt', 'en'],
    ['nl-NL', 'nl', 'en'], ['pl-PL', 'pl', 'en'], ['ru-RU', 'ru', 'en'],
    ['ja-JP', 'ja', 'en'], ['zh-CN', 'zh', 'en'], ['ko-KR', 'ko', 'en'],
]


def get_random_device_profile():
    """Generate a random device profile for fingerprinting."""
    user_agent = random.choice(USER_AGENTS)
    width, height = random.choice(SCREEN_RESOLUTIONS)
    timezone = random.choice(TIMEZONES)
    languages = random.choice(LANGUAGES)
    
    # Determine platform from user agent
    if 'Windows' in user_agent:
        platform = 'Win32'
        platform_version = random.choice(['10.0', '11.0'])
    elif 'Macintosh' in user_agent:
        platform = 'MacIntel'
        platform_version = random.choice(['10.15.7', '13.6.7', '14.7.1'])
    else:
        platform = 'Linux x86_64'
        platform_version = '5.15.0'
    
    # Hardware concurrency (CPU cores) - typically 4, 8, 12, 16
    hardware_concurrency = random.choice([4, 8, 8, 12, 16, 16])  # Weighted towards common values
    
    # Device memory in GB (converted to bytes)
    device_memory = random.choice([4, 8, 8, 16, 16, 32])  # Weighted towards common values
    
    # Color depth
    color_depth = random.choice([24, 24, 24, 30, 32])  # Mostly 24-bit
    
    # Pixel ratio
    pixel_ratio = random.choice([1.0, 1.0, 1.25, 1.5, 2.0])  # Weighted towards 1.0
    
    return {
        'user_agent': user_agent,
        'width': width,
        'height': height,
        'timezone': timezone,
        'languages': languages,
        'platform': platform,
        'platform_version': platform_version,
        'hardware_concurrency': hardware_concurrency,
        'device_memory': device_memory,
        'color_depth': color_depth,
        'pixel_ratio': pixel_ratio,
    }


def test_network_connectivity():
    """Test network connectivity to diagnose VPN/Docker issues."""
    print("\n  === Network Connectivity Test ===")
    sys.stdout.flush()
    
    import socket
    import subprocess
    import shutil
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: DNS resolution
    print("  [1] Testing DNS resolution...")
    sys.stdout.flush()
    try:
        socket.gethostbyname('google.com')
        print("    ✓ DNS resolution: OK")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ DNS resolution: FAILED ({e})")
        tests_failed += 1
    sys.stdout.flush()
    
    # Test 2: Get public IP address via api.ipify.org
    print("  [2] Getting public IP address...")
    sys.stdout.flush()
    ip_address = None
    try:
        import urllib.request
        import ssl
        context = ssl.create_default_context()
        response = urllib.request.urlopen('https://api.ipify.org/', timeout=10, context=context)
        if response.getcode() == 200:
            ip_address = response.read().decode('utf-8').strip()
            print(f"    ✓ Public IP: {ip_address}")
            tests_passed += 1
            
            # Send IP address to Telegram
            try:
                from ..notifications.telegram import send_telegram_message
                telegram_message = f"🌐 Network Connectivity Test\n\nPublic IP Address: {ip_address}"
                send_telegram_message(telegram_message)
                print("    ✓ IP address sent to Telegram")
            except Exception as telegram_error:
                print(f"    ⚠ Failed to send IP to Telegram: {telegram_error}")
                # Don't fail the test if Telegram send fails
        else:
            print(f"    ✗ Failed to get IP (status: {response.getcode()})")
            tests_failed += 1
    except Exception as e:
        print(f"    ✗ Failed to get IP address: {e}")
        tests_failed += 1
    sys.stdout.flush()
    
    # Test 3: Target website connectivity
    print(f"  [3] Testing connectivity to target website ({BOOKING_URL})...")
    sys.stdout.flush()
    try:
        import ssl
        context = ssl.create_default_context()
        response = urllib.request.urlopen(BOOKING_URL, timeout=10, context=context)
        print(f"    ✓ Target website: OK (status: {response.getcode()})")
        tests_passed += 1
    except Exception as e:
        print(f"    ✗ Target website: FAILED ({e})")
        tests_failed += 1
    sys.stdout.flush()
    
    # Test 4: Check VPN interface (if WireGuard is running)
    print("  [4] Checking for VPN interface...")
    sys.stdout.flush()
    try:
        # Check if 'ip' command is available
        ip_cmd = shutil.which('ip')
        if not ip_cmd:
            print("    ⚠ 'ip' command not available (likely running in Docker container)")
            print("    ⚠ Skipping VPN interface check")
            tests_passed += 1  # Not critical
        else:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True, timeout=5, check=False)
            if result.returncode == 0:
                if 'wg' in result.stdout.lower() or 'wireguard' in result.stdout.lower():
                    print("    ✓ VPN interface detected")
                    tests_passed += 1
                else:
                    print("    ⚠ VPN interface not found (might be using host network)")
                    tests_passed += 1  # Not a failure, just info
            else:
                print(f"    ⚠ Could not check VPN interface: command returned {result.returncode}")
                tests_passed += 1  # Not critical
    except FileNotFoundError:
        print("    ⚠ 'ip' command not found (likely running in Docker container)")
        tests_passed += 1  # Not critical
    except Exception as e:
        print(f"    ⚠ Could not check VPN interface: {e}")
        tests_passed += 1  # Not critical
    
    # Test 5: Check routing table
    print("  [5] Checking routing table...")
    sys.stdout.flush()
    try:
        # Check if 'ip' command is available
        ip_cmd = shutil.which('ip')
        if not ip_cmd:
            print("    ⚠ 'ip' command not available (likely running in Docker container)")
            print("    ⚠ Skipping routing table check")
            tests_passed += 1  # Not critical
        else:
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=5, check=False)
            if result.returncode == 0:
                routes = result.stdout.splitlines()
                print(f"    Routing info: {len(routes)} routes found")
                # Show first few routes
                for route in routes[:3]:
                    print(f"      - {route}")
                tests_passed += 1
            else:
                print(f"    ⚠ Could not check routing: command returned {result.returncode}")
                tests_passed += 1  # Not critical
    except FileNotFoundError:
        print("    ⚠ 'ip' command not found (likely running in Docker container)")
        tests_passed += 1  # Not critical
    except Exception as e:
        print(f"    ⚠ Could not check routing: {e}")
        tests_passed += 1  # Not critical
    sys.stdout.flush()
    
    # Test 6: Check if we can resolve Chrome-related domains
    print("  [6] Testing Chrome-related domain resolution...")
    sys.stdout.flush()
    chrome_domains = ['dl.google.com', 'clients2.google.com', 'update.googleapis.com']
    for domain in chrome_domains:
        try:
            socket.gethostbyname(domain)
            print(f"    ✓ {domain}: resolvable")
        except Exception as e:
            print(f"    ✗ {domain}: NOT resolvable ({e})")
    sys.stdout.flush()
    
    print(f"\n  === Test Summary: {tests_passed} passed, {tests_failed} failed ===")
    sys.stdout.flush()
    
    if tests_failed > 0:
        print("  ⚠ WARNING: Some connectivity tests failed. This might cause Chrome to hang.")
        print("  ⚠ VPN might be blocking or routing traffic incorrectly.")
        sys.stdout.flush()
    
    return tests_failed == 0


def create_driver(headless=False):
    """Create and configure a Chrome WebDriver instance with anti-detection measures.
    
    Each run uses a randomly generated device profile to avoid fingerprinting.
    """
    # Test network connectivity first (especially important with VPN)
    print("  Testing network connectivity...")
    sys.stdout.flush()
    network_ok = test_network_connectivity()
    
    if not network_ok:
        print("  ⚠ Network connectivity issues detected. Chrome might hang during initialization.")
        print("  Continuing anyway, but expect potential delays...")
        sys.stdout.flush()
    
    print("  Generating random device profile...")
    sys.stdout.flush()
    # Generate a random device profile for this session
    profile = get_random_device_profile()
    print(f"  Using user agent: {profile['user_agent'][:50]}...")
    sys.stdout.flush()
    
    if UC_AVAILABLE:
        # Try undetected-chromedriver first, fall back to regular selenium on error
        try:
            print("  Attempting to use undetected-chromedriver...")
            sys.stdout.flush()
            # Use undetected-chromedriver for better anti-detection
            options = uc.ChromeOptions()
            if headless:
                options.add_argument('--headless=new')  # Use new headless mode
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
            
            # Network-disabling flags to prevent hangs (especially with VPN)
            # These disable Chrome background services that can cause startup delays
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-component-update')
            options.add_argument('--no-first-run')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-breakpad')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-translate')
            options.add_argument('--metrics-recording-only')
            options.add_argument('--safebrowsing-disable-auto-update')
            options.add_argument('--password-store=basic')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            # DNS and network-related flags
            options.add_argument('--dns-prefetch-disable')
            options.add_argument('--disable-dns-prefetch')
            options.add_argument('--disable-features=NetworkService,NetworkServiceInProcess')
            
            # Additional stealth options
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-site-isolation-trials')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Use random user agent from profile
            options.add_argument(f'user-agent={profile["user_agent"]}')
            
            # Use random window size from profile
            options.add_argument(f'--window-size={profile["width"]},{profile["height"]}')
            
            # Configure proxy if available
            # Skip browser-level proxy if proxychains (system-level proxy) is being used
            use_system_proxy = os.getenv("USE_SYSTEM_PROXY", "").lower() in ("true", "1", "yes")
            if not use_system_proxy:
                # Check if we're running under proxychains by checking parent process
                try:
                    import psutil
                    current_process = psutil.Process()
                    parent = current_process.parent()
                    if parent and 'proxychains' in parent.name().lower():
                        use_system_proxy = True
                except ImportError:
                    # psutil not available, continue with browser-level proxy
                    pass
                except (AttributeError, psutil.NoSuchProcess, psutil.AccessDenied):
                    # psutil available but can't check process, continue with browser-level proxy
                    pass
            
            proxy_server = os.getenv("PROXY_SERVER", "").strip()
            proxy_username = os.getenv("PROXY_USERNAME", "").strip()
            proxy_password = os.getenv("PROXY_PASSWORD", "").strip()
            
            if proxy_server and not use_system_proxy:
                # Load proxy authentication extension if credentials are provided
                if proxy_username and proxy_password:
                    # Create dynamic extension with credentials baked in
                    # Based on: https://stackoverflow.com/questions/17082425/running-selenium-webdriver-with-a-proxy-in-python
                    import tempfile
                    from urllib.parse import urlparse
                    
                    parsed = urlparse(proxy_server)
                    proxy_host = parsed.hostname
                    proxy_port = parsed.port or (443 if parsed.scheme == 'https' else 80)
                    
                    # Extension manifest (Manifest V3)
                    manifest_json = '''{
    "manifest_version": 3,
    "name": "Proxy Auth",
    "version": "1.0",
    "permissions": ["proxy", "webRequest", "webRequestAuthProvider"],
    "host_permissions": ["<all_urls>"],
    "background": {"service_worker": "background.js"}
}'''
                    
                    # Background script with credentials hardcoded
                    background_js = f'''
// Configure proxy settings
chrome.proxy.settings.set({{
    value: {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                host: "{proxy_host}",
                port: {proxy_port},
                scheme: "{parsed.scheme or 'http'}"
            }},
            bypassList: ["localhost", "127.0.0.1"]
        }}
    }},
    scope: "regular"
}}, function() {{}});

// Supply proxy auth credentials when prompted
chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_username}",
                password: "{proxy_password}"
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);
'''
                    
                    # Create temporary extension directory
                    ext_dir = tempfile.mkdtemp(prefix="proxy_auth_ext_")
                    
                    with open(os.path.join(ext_dir, "manifest.json"), 'w') as f:
                        f.write(manifest_json)
                    
                    with open(os.path.join(ext_dir, "background.js"), 'w') as f:
                        f.write(background_js)
                    
                    options.add_argument(f'--load-extension={ext_dir}')
                    print(f"  Created dynamic proxy authentication extension")
                    print(f"  Using proxy: {parsed.scheme}://{proxy_username}:***@{proxy_host}:{proxy_port}")
                    
                    # Note: Don't set --proxy-server when using chrome.proxy API
                    # The extension handles proxy configuration
                else:
                    options.add_argument(f'--proxy-server={proxy_server}')
                    print(f"  Using proxy: {proxy_server}")
                sys.stdout.flush()
            
            print("  Creating Chrome driver instance...")
            sys.stdout.flush()
            
            # Create driver with timeout protection (for VPN-related hangs)
            driver = None
            driver_error = None
            
            def create_driver_thread():
                nonlocal driver, driver_error
                try:
                    # Try to get Chrome version to avoid auto-detection delays
                    import subprocess
                    try:
                        chrome_version_output = subprocess.check_output(
                            ['google-chrome', '--version'], 
                            stderr=subprocess.STDOUT, 
                            timeout=5
                        ).decode('utf-8')
                        # Extract version number (e.g., "Google Chrome 131.0.6778.85" -> 131)
                        import re
                        version_match = re.search(r'(\d+)\.', chrome_version_output)
                        if version_match:
                            version_main = int(version_match.group(1))
                            print(f"  Detected Chrome version: {version_main}")
                            sys.stdout.flush()
                            # Use specific version to avoid auto-detection
                            driver = uc.Chrome(options=options, use_subprocess=True, version_main=version_main)
                        else:
                            driver = uc.Chrome(options=options, use_subprocess=True)
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError):
                        # Fallback to auto-detection if version detection fails
                        print("  Could not detect Chrome version, using auto-detection...")
                        sys.stdout.flush()
                        driver = uc.Chrome(options=options, use_subprocess=True)
                except Exception as e:
                    driver_error = e
            
            # Start driver creation in a thread with timeout
            driver_thread = threading.Thread(target=create_driver_thread, daemon=True)
            driver_thread.start()
            driver_thread.join(timeout=60)  # 60 second timeout
            
            if driver_thread.is_alive():
                print("  ERROR: Chrome driver initialization timed out after 60 seconds")
                print("  This is likely caused by VPN blocking Chrome's network connections")
                print("  Trying fallback to regular Selenium...")
                sys.stdout.flush()
                raise TimeoutError("Chrome driver initialization timed out")
            
            if driver_error:
                raise driver_error
            
            if driver is None:
                raise RuntimeError("Failed to create Chrome driver (unknown error)")
            
            print("  Applying fingerprinting protection...")
            sys.stdout.flush()
            # Apply comprehensive fingerprinting protection via CDP
            _apply_fingerprint_protection(driver, profile)
            
            # Proxy authentication is handled by the extension with hardcoded credentials
            if proxy_server and proxy_username and proxy_password and not use_system_proxy:
                print("  ✓ Proxy authentication handled by extension")
                sys.stdout.flush()
            elif use_system_proxy and proxy_server:
                print("  ✓ Using system-level proxy (proxychains4) - skipping browser-level proxy configuration")
                sys.stdout.flush()
            
            return driver
        except Exception as e:
            print(f"  Warning: undetected-chromedriver failed ({e}), falling back to regular selenium with stealth")
            sys.stdout.flush()
            # Fall through to regular selenium implementation
    
    # Fallback to regular selenium with manual anti-detection (used if UC not available or fails)
    print("  Using regular Selenium WebDriver...")
    sys.stdout.flush()
    options = webdriver.ChromeOptions()
    
    # Network-disabling flags to prevent hangs (especially with VPN)
    # These disable Chrome background services that can cause startup delays
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-component-update')
    options.add_argument('--no-first-run')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-breakpad')
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-hang-monitor')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-prompt-on-repost')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-translate')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--safebrowsing-disable-auto-update')
    options.add_argument('--password-store=basic')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    # DNS and network-related flags
    options.add_argument('--dns-prefetch-disable')
    options.add_argument('--disable-dns-prefetch')
    options.add_argument('--disable-features=NetworkService,NetworkServiceInProcess')
    
    # Anti-detection arguments
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-site-isolation-trials')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Use random user agent from profile
    options.add_argument(f'user-agent={profile["user_agent"]}')
    
    if headless:
        options.add_argument('--headless=new')
    
    # Use random window size from profile
    options.add_argument(f'--window-size={profile["width"]},{profile["height"]}')
    
    # Configure proxy if available
    # Skip browser-level proxy if proxychains (system-level proxy) is being used
    use_system_proxy = os.getenv("USE_SYSTEM_PROXY", "").lower() in ("true", "1", "yes")
    if not use_system_proxy:
        # Check if we're running under proxychains by checking parent process
        try:
            import psutil
            current_process = psutil.Process()
            parent = current_process.parent()
            if parent and 'proxychains' in parent.name().lower():
                use_system_proxy = True
        except ImportError:
            # psutil not available, continue with browser-level proxy
            pass
        except (AttributeError, psutil.NoSuchProcess, psutil.AccessDenied):
            # psutil available but can't check process, continue with browser-level proxy
            pass
    
    proxy_server = os.getenv("PROXY_SERVER", "").strip()
    proxy_username = os.getenv("PROXY_USERNAME", "").strip()
    proxy_password = os.getenv("PROXY_PASSWORD", "").strip()
    
    if proxy_server and not use_system_proxy:
        if proxy_username and proxy_password:
            # Create dynamic extension with credentials baked in (same as UC path)
            import tempfile
            from urllib.parse import urlparse
            
            parsed = urlparse(proxy_server)
            proxy_host = parsed.hostname
            proxy_port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            manifest_json = '''{
    "manifest_version": 3,
    "name": "Proxy Auth",
    "version": "1.0",
    "permissions": ["proxy", "webRequest", "webRequestAuthProvider"],
    "host_permissions": ["<all_urls>"],
    "background": {"service_worker": "background.js"}
}'''
            
            background_js = f'''
chrome.proxy.settings.set({{
    value: {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                host: "{proxy_host}",
                port: {proxy_port},
                scheme: "{parsed.scheme or 'http'}"
            }},
            bypassList: ["localhost", "127.0.0.1"]
        }}
    }},
    scope: "regular"
}}, function() {{}});

chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_username}",
                password: "{proxy_password}"
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);
'''
            
            ext_dir = tempfile.mkdtemp(prefix="proxy_auth_ext_")
            with open(os.path.join(ext_dir, "manifest.json"), 'w') as f:
                f.write(manifest_json)
            with open(os.path.join(ext_dir, "background.js"), 'w') as f:
                f.write(background_js)
            
            options.add_argument(f'--load-extension={ext_dir}')
            print(f"  Created dynamic proxy authentication extension")
            print(f"  Using proxy: {parsed.scheme}://{proxy_username}:***@{proxy_host}:{proxy_port}")
        else:
            options.add_argument(f'--proxy-server={proxy_server}')
            print(f"  Using proxy: {proxy_server}")
        sys.stdout.flush()
    elif use_system_proxy and proxy_server:
        print("  ✓ Using system-level proxy (proxychains4) - skipping browser-level proxy configuration")
        sys.stdout.flush()
    
    print("  Creating Chrome driver instance...")
    sys.stdout.flush()
    driver = webdriver.Chrome(options=options)
    
    print("  Applying fingerprinting protection...")
    sys.stdout.flush()
    # Apply comprehensive fingerprinting protection via CDP
    _apply_fingerprint_protection(driver, profile)
    
    return driver


def _apply_fingerprint_protection(driver, profile):
    """Apply comprehensive fingerprinting protection via Chrome DevTools Protocol."""
    # Format languages array for JavaScript
    languages_js = json.dumps(profile["languages"])
    
    # Enhanced stealth script with device profile
    stealth_script = f'''
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined
        }});
        
        // Spoof plugins
        Object.defineProperty(navigator, 'plugins', {{
            get: () => {{
                const plugins = [
                    {{ name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }},
                    {{ name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' }},
                    {{ name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }}
                ];
                return plugins;
            }}
        }});
        
        // Spoof languages from profile
        Object.defineProperty(navigator, 'languages', {{
            get: () => {languages_js}
        }});
        
        // Spoof platform
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{profile["platform"]}'
        }});
        
        // Add chrome object
        window.chrome = {{
            runtime: {{}},
            loadTimes: function() {{}},
            csi: function() {{}},
            app: {{}}
        }};
        
        // Spoof permissions
        Object.defineProperty(navigator, 'permissions', {{
            get: () => ({{
                query: () => Promise.resolve({{ state: 'granted' }})
            }})
        }});
        
        // Spoof hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {profile["hardware_concurrency"]}
        }});
        
        // Spoof device memory
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {profile["device_memory"]}
        }});
        
        // Spoof max touch points
        Object.defineProperty(navigator, 'maxTouchPoints', {{
            get: () => 0
        }});
        
        // Override screen properties
        Object.defineProperty(screen, 'width', {{
            get: () => {profile["width"]}
        }});
        Object.defineProperty(screen, 'height', {{
            get: () => {profile["height"]}
        }});
        Object.defineProperty(screen, 'availWidth', {{
            get: () => {profile["width"]}
        }});
        Object.defineProperty(screen, 'availHeight', {{
            get: () => {profile["height"] - 40}
        }});
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {profile["color_depth"]}
        }});
        Object.defineProperty(screen, 'pixelDepth', {{
            get: () => {profile["color_depth"]}
        }});
        
        // Override device pixel ratio
        Object.defineProperty(window, 'devicePixelRatio', {{
            get: () => {profile["pixel_ratio"]}
        }});
        
        // Canvas fingerprinting protection - add noise to canvas
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {{
            const context = this.getContext('2d');
            if (context) {{
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] += Math.random() < 0.1 ? Math.floor(Math.random() * 2) - 1 : 0;
                }}
                context.putImageData(imageData, 0, 0);
            }}
            return originalToDataURL.apply(this, arguments);
        }};
        
        // WebGL fingerprinting protection
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return 'Intel Inc.';
            }}
            if (parameter === 37446) {{
                return 'Intel Iris OpenGL Engine';
            }}
            return getParameter.apply(this, arguments);
        }};
        
        // Audio context fingerprinting protection
        if (window.AudioContext || window.webkitAudioContext) {{
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
            AudioContext.prototype.createAnalyser = function() {{
                const analyser = originalCreateAnalyser.apply(this, arguments);
                const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                analyser.getFloatFrequencyData = function(array) {{
                    originalGetFloatFrequencyData.apply(this, arguments);
                    for (let i = 0; i < array.length; i++) {{
                        array[i] += Math.random() * 0.0001;
                    }}
                }};
                return analyser;
            }};
        }}
        
        // Override timezone
        const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
        Date.prototype.getTimezoneOffset = function() {{
            // Return a random offset within reasonable range (-12 to +14 hours)
            return Math.floor(Math.random() * 26) - 12;
        }};
    '''
    
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': stealth_script
    })
    
    # Set timezone via CDP
    try:
        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
            'timezoneId': profile['timezone']
        })
    except Exception:
        # Some CDP versions may not support this, ignore
        pass
    
    # Set geolocation to a random location (optional, can be disabled if not needed)
    try:
        # Random location within reasonable bounds
        driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
            'latitude': random.uniform(40.0, 50.0),
            'longitude': random.uniform(-5.0, 20.0),
            'accuracy': 100
        })
    except Exception:
        # Some CDP versions may not support this, ignore
        pass


def navigate_to_booking_page(driver, max_retries=3):
    """Navigate to the booking page and wait for form to load.
    
    Args:
        driver: WebDriver instance
        max_retries: Maximum number of retry attempts for connection errors (default: 3)
    
    Returns:
        WebDriverWait instance
        
    Raises:
        WebDriverException: If navigation fails after all retries
    """
    print("Opening https://konzinfobooking.mfa.gov.hu/...")
    
    # Add random delay before navigation to simulate human behavior
    time.sleep(random.uniform(1, 3))
    
    # Retry logic for connection errors
    for attempt in range(1, max_retries + 1):
        try:
            driver.get(BOOKING_URL)
            # If we get here, navigation succeeded
            break
        except WebDriverException as e:
            error_msg = str(e).lower()
            
            # Check if it's a connection-related error
            is_connection_error = any(
                err in error_msg 
                for err in [
                    'err_connection_closed',
                    'err_connection_reset',
                    'err_connection_refused',
                    'err_connection_timed_out',
                    'err_network_changed',
                    'net::err_connection',
                    'connection closed',
                    'connection reset',
                ]
            )
            
            if is_connection_error and attempt < max_retries:
                # Exponential backoff: 2^attempt seconds, with some randomness
                wait_time = (2 ** attempt) + random.uniform(0.5, 1.5)
                print(f"  Connection error on attempt {attempt}/{max_retries}: {e}")
                print(f"  Retrying in {wait_time:.1f} seconds...")
                sys.stdout.flush()
                time.sleep(wait_time)
                
                # Check if driver is still valid before retrying
                try:
                    # Try to get current URL to verify driver is still responsive
                    _ = driver.current_url
                except Exception:
                    print("  Driver appears to be in a bad state, cannot retry")
                    raise
            else:
                # Not a connection error, or we've exhausted retries
                if attempt >= max_retries:
                    # Last attempt failed, raise with context
                    if is_connection_error:
                        raise WebDriverException(
                            f"Failed to navigate after {max_retries} attempts: {e}"
                        ) from e
                    else:
                        # Non-connection error, raise immediately
                        raise
                else:
                    # Non-connection error on non-final attempt, raise immediately
                    raise
    
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


def get_full_page_screenshot(driver):
    """Capture a full page screenshot using Chrome DevTools Protocol.
    
    Returns PNG bytes of the entire page, not just the viewport.
    """
    try:
        # Get page dimensions using JavaScript
        page_dimensions = driver.execute_script("""
            return {
                width: Math.max(
                    document.body.scrollWidth,
                    document.body.offsetWidth,
                    document.documentElement.clientWidth,
                    document.documentElement.scrollWidth,
                    document.documentElement.offsetWidth
                ),
                height: Math.max(
                    document.body.scrollHeight,
                    document.body.offsetHeight,
                    document.documentElement.clientHeight,
                    document.documentElement.scrollHeight,
                    document.documentElement.offsetHeight
                )
            };
        """)
        
        # Use Chrome DevTools Protocol to capture full page screenshot
        screenshot_result = driver.execute_cdp_cmd('Page.captureScreenshot', {
            'format': 'png',
            'captureBeyondViewport': True
        })
        
        # Decode base64 screenshot
        screenshot_bytes = base64.b64decode(screenshot_result['data'])
        return screenshot_bytes
        
    except Exception as e:
        print(f"  Warning: Full page screenshot failed ({e}), falling back to viewport screenshot")
        # Fallback to regular viewport screenshot
        return driver.get_screenshot_as_png()


