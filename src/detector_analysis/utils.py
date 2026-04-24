"""Shared utilities for detector analysis."""
import re


def excel_safe_sheet_name(name: str, prefix: str = "Plot_") -> str:
    """
    This function converts a string into a valid Excel sheet name, to assure no naming errors happen

    """
    s = re.sub(r"[:\\/?*\[\]]", "_", str(name))
    s = prefix + s
    return s[:31]


def safe_filename(name: str) -> str:
    """
    This function converts a string into a safe filename, by keeping only
    - letters, number, underscores, and dashes. All other characters are replaced with underscores.
    """
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", str(name))