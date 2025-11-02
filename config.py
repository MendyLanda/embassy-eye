"""
Configuration constants and default values for the booking form filler.
"""

# URL Configuration
BOOKING_URL = "https://konzinfobooking.mfa.gov.hu/"

# Default form values
DEFAULT_VALUES = {
    "name": "John Smith",
    "email": "john.smith@example.com",
    "phone": "+3612345678",
    "date_of_birth": "30/01/1990",
    "date_of_birth_iso": "1990-01-30",  # ISO format for date picker
    "passport": "AB123456",
    "citizenship": "Serbian",
    "residence_permit": "123456789",
    "residential_community": "Belgrade",
    "applicants": "1"
}

# Field mapping by ID
FIELD_MAP = {
    "label4": ("name", DEFAULT_VALUES["name"]),
    "birthDate": ("date_of_birth", DEFAULT_VALUES["date_of_birth"]),
    "label6": ("applicants", DEFAULT_VALUES["applicants"]),
    "label9": ("phone", DEFAULT_VALUES["phone"]),
    "label10": ("email", DEFAULT_VALUES["email"]),
    "label1000": ("residence_permit", DEFAULT_VALUES["residence_permit"]),
    "label1001": ("citizenship", DEFAULT_VALUES["citizenship"]),
    "label1002": ("passport", DEFAULT_VALUES["passport"]),
    "label1003": ("residential_community", DEFAULT_VALUES["residential_community"]),
    "slabel13": ("checkbox", None),  # First consent checkbox
    "label13": ("checkbox", None),   # Second consent checkbox
}

# Dropdown IDs and options
CONSULATE_DROPDOWN_NAME = "ugyfelszolgalat"
CONSULATE_DROPDOWN_ID = "f05149cd-51b4-417d-912b-9b8e1af999b6"
CONSULATE_OPTION_TEXT = "Serbia - Subotica"

VISA_TYPE_DROPDOWN_ID = "7c357940-1e4e-4b29-8e87-8b1d09b97d07"
VISA_TYPE_OPTION_TEXT = "Visa application (Schengen visa- type 'C')"

# Timing constants (in seconds)
PAGE_LOAD_WAIT = 20
ELEMENT_WAIT_TIME = 0.3
CHAR_TYPE_DELAY = 0.08
SCROLL_WAIT = 0.5
INSPECTION_TIME = 30

# Textarea default value
DEFAULT_TEXTAREA_VALUE = "Test message"

