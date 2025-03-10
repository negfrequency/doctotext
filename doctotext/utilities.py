# -*- coding: utf-8 -*-

import datetime

def formatted_hex(value):
    """Reformats a hexadecimal value to ensure it is in 4-character (2-byte) format."""
    # Mask to keep only the least significant 16 bits
    new_value = value & 0xFFFF  
    # Format as 4-character hex with '0x' prefix
    return f"0x{new_value:04X}"


def find_value_by_key(data: dict,
                      key: str):
    """
    @param data: recursive object containings lists and/or dicts
    @param key: a key name. Does not necessarily have to be a string.
    RETURNS: value of first key found
    """

    # Check if data is a dictionary
    if isinstance(data, dict):
        # Check if the key exists in the current dictionary
        if key in data:
            return data[key]
        # If the key is not found, search in the values of the dictionary
        for value in data.values():
            result = find_value_by_key(value, key)
            if result is not None:
                return result
    # Check if data is a list
    elif isinstance(data, list):
        # Search for the key in the list elements
        for item in data:
            result = find_value_by_key(item, key)
            if result is not None:
                return result
    # If data is neither a dictionary nor a list, return None
    return None


def filetime_to_datetime(dwLowDateTime, dwHighDateTime):
    # Combine the high and low parts into a single 64-bit integer
    filetime = (dwHighDateTime << 32) + dwLowDateTime
    
    # Convert from Windows file time (100-nanosecond intervals since 1601-01-01) to Unix timestamp
    unix_timestamp = (filetime - 116444736000000000) // 10_000  # Convert to milliseconds
    
    # Convert to a timezone-aware datetime object
    return datetime.datetime.fromtimestamp(unix_timestamp / 1000, datetime.UTC)