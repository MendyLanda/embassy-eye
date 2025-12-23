"""
Telegram notification module for sending results and screenshots.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
HEALTHCHECK_BOT_TOKEN = os.getenv("HEALTHCHECK_BOT_TOKEN")


def _ensure_telegram_config() -> bool:
    """Verify that the Telegram bot credentials are configured."""
    if not TELEGRAM_BOT_TOKEN:
        print("Warning: TELEGRAM_BOT_TOKEN not set in .env file")
        return False
    if not TELEGRAM_USER_ID:
        print("Warning: TELEGRAM_USER_ID not set in .env file")
        return False
    return True


def send_telegram_message(message: str, screenshot_bytes: bytes = None):
    """
    Send a message to the user via Telegram bot.
    
    Args:
        message: Text message to send
        screenshot_bytes: Optional screenshot bytes to attach
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    if not _ensure_telegram_config():
        return False
    
    try:
        if screenshot_bytes:
            # Send message with photo from memory
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            
            files = {'photo': ('screenshot.png', screenshot_bytes, 'image/png')}
            data = {
                'chat_id': TELEGRAM_USER_ID,
                'caption': message
            }
            response = requests.post(url, files=files, data=data)
        else:
            # Send text message only
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TELEGRAM_USER_ID,
                'text': message
            }
            response = requests.post(url, json=data)
        
        response.raise_for_status()
        print(f"✓ Telegram message sent successfully")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram message: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending Telegram message: {e}")
        return False


def send_telegram_document(filename: str, caption: str, file_bytes: bytes) -> bool:
    """
    Send a document (e.g., HTML dump) to the user via Telegram bot.
    
    Args:
        filename: Name of the document (shown in Telegram)
        caption: Optional caption (max 1024 characters)
        file_bytes: File content in bytes
    
    Returns:
        bool: True if document was sent successfully, False otherwise
    """
    if not _ensure_telegram_config():
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        files = {'document': (filename, file_bytes, 'text/html')}
        data = {
            'chat_id': TELEGRAM_USER_ID,
            'caption': caption[:1024] if caption else ""
        }
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        print("✓ Telegram document sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending Telegram document: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending Telegram document: {e}")
        return False


def send_result_notification(slots_available: bool, screenshot_bytes: bytes = None, special_case: str = None, booking_url: str = None, location: str = None):
    """
    Send appointment availability result notification.
    Only sends notification when slots are found.
    
    Args:
        slots_available: True if slots are available, False otherwise
        screenshot_bytes: Optional screenshot bytes to attach (None for special cases)
        special_case: String indicating special case: "captcha_required", "email_verification", or None
        booking_url: Optional booking URL to include in the message
        location: Optional location string (e.g., "subotica", "belgrade") to include in the message
    """
    if not slots_available:
        # Don't send notification if no slots found
        return
    
    # Send healthcheck notification
    ip_address, country = get_ip_and_country()
    send_healthcheck_slots_found(country, location=location)
    
    # Base message
    location_display = location.capitalize() if location else ""
    location_prefix = f"[{location_display}] " if location_display else ""
    base_message = f"✅ SLOTS FOUND! {location_prefix}\n\nThere are available appointment slots!"
    
    # Add booking URL if provided
    if booking_url:
        base_message += f"\n\n🔗 {booking_url}"
    
    if special_case == "captcha_required":
        message = f"{base_message}\n\n⚠️ Site requests captcha check on site"
        # Send without screenshot for captcha case
        send_telegram_message(message, None)
    elif special_case == "email_verification":
        message = f"{base_message}\n\n⚠️ Site requested email verification (captcha was sent on email)"
        # Send without screenshot for email verification case
        send_telegram_message(message, None)
    else:
        message = base_message
        send_telegram_message(message, screenshot_bytes)


def _get_proxy_config():
    """
    Build proxy configuration from environment variables.
    
    Returns:
        dict: Proxy configuration for requests, or None if not configured
    """
    proxy_server = os.getenv("PROXY_SERVER")
    if not proxy_server:
        return None
    
    proxy_username = os.getenv("PROXY_USERNAME")
    proxy_password = os.getenv("PROXY_PASSWORD")
    
    if proxy_username and proxy_password:
        # Parse the proxy URL and inject credentials
        # Format: http://username:password@host:port
        if "://" in proxy_server:
            protocol, rest = proxy_server.split("://", 1)
            proxy_url = f"{protocol}://{proxy_username}:{proxy_password}@{rest}"
        else:
            proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_server}"
    else:
        proxy_url = proxy_server
    
    return {
        "http": proxy_url,
        "https": proxy_url
    }


def get_ip_and_country():
    """
    Get current public IP address and country.
    Uses proxy if configured in environment variables.
    
    Returns:
        tuple: (ip_address, country) or (None, None) if failed
    """
    proxies = _get_proxy_config()
    
    try:
        # Get IP address (through proxy if configured)
        ip_response = requests.get("https://api.ipify.org", timeout=10, proxies=proxies)
        if ip_response.status_code == 200:
            ip_address = ip_response.text.strip()
        else:
            # Fallback to alternative service
            ip_response = requests.get("https://ifconfig.me", timeout=10, proxies=proxies)
            if ip_response.status_code == 200:
                ip_address = ip_response.text.strip()
            else:
                return None, None
        
        # Get country from IP using ipapi.co (free, no API key needed)
        try:
            country_response = requests.get(f"https://ipapi.co/{ip_address}/country_name/", timeout=10, proxies=proxies)
            if country_response.status_code == 200:
                country = country_response.text.strip()
                if country and country != "None":
                    return ip_address, country
        except:
            pass
        
        # Fallback: try ip-api.com
        try:
            country_response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=10, proxies=proxies)
            if country_response.status_code == 200:
                data = country_response.json()
                if data.get("status") == "success":
                    country = data.get("country", "Unknown")
                    return ip_address, country
        except:
            pass
        
        # If we got IP but couldn't get country, return IP with Unknown country
        return ip_address, "Unknown"
        
    except Exception as e:
        print(f"Warning: Failed to get IP and country: {e}")
        return None, None


def send_healthcheck_message(message: str) -> bool:
    """
    Send a healthcheck message to the user via healthcheck Telegram bot.
    
    Args:
        message: Text message to send
    
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    if not HEALTHCHECK_BOT_TOKEN:
        # Silently fail if healthcheck bot is not configured
        return False
    
    if not TELEGRAM_USER_ID:
        print("Warning: TELEGRAM_USER_ID not set in .env file")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{HEALTHCHECK_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_USER_ID,
            'text': message
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending healthcheck message: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending healthcheck message: {e}")
        return False


def send_healthcheck_slots_found(country: str = None, location: str = None):
    """Send healthcheck notification when slots are found."""
    location_display = location.capitalize() if location else ""
    location_suffix = f" - {location_display}" if location_display else ""
    message = f"🔔 Healthcheck: Slots found{location_suffix}"
    if country:
        message += f" ({country})"
    send_healthcheck_message(message)


def send_healthcheck_slot_busy(country: str = None, location: str = None):
    """Send healthcheck notification when all slots are busy."""
    location_display = location.capitalize() if location else ""
    location_suffix = f" - {location_display}" if location_display else ""
    message = f"🔔 Healthcheck: Slot busy{location_suffix}"
    if country:
        message += f" ({country})"
    send_healthcheck_message(message)


def send_healthcheck_ip_blocked(ip_address: str, country: str = None, location: str = None):
    """Send healthcheck notification when IP is blocked."""
    location_display = location.capitalize() if location else ""
    location_suffix = f" - {location_display}" if location_display else ""
    message = f"🔔 Healthcheck: IP blocked{location_suffix}\nIP: {ip_address}"
    if country:
        message += f"\nCountry: {country}"
    send_healthcheck_message(message)


def send_healthcheck_reloaded_page(reason: str = None, location: str = None):
    """Send healthcheck notification when page is reloaded for refilling form."""
    location_display = location.capitalize() if location else ""
    location_suffix = f" - {location_display}" if location_display else ""
    message = f"🔔 Healthcheck: Reloaded page for refilling form{location_suffix}"
    if reason:
        message += f"\nReason: {reason}"
    send_healthcheck_message(message)

