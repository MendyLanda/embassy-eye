"""
Notification utilities for embassy-eye.
"""

from .telegram import (
    send_result_notification,
    send_telegram_message,
    send_telegram_document,
    send_healthcheck_message,
    send_healthcheck_slots_found,
    send_healthcheck_slot_busy,
    send_healthcheck_ip_blocked,
    send_healthcheck_reloaded_page,
    get_ip_and_country,
)

__all__ = [
    "send_result_notification",
    "send_telegram_message",
    "send_telegram_document",
    "send_healthcheck_message",
    "send_healthcheck_slots_found",
    "send_healthcheck_slot_busy",
    "send_healthcheck_ip_blocked",
    "send_healthcheck_reloaded_page",
    "get_ip_and_country",
]

