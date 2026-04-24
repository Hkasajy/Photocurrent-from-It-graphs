"""Shared utilities for detector analysis."""
import re


def excel_safe_sheet_name(name: str, prefix: str = "Plot_") -> str:
    """
    Convert a string into a valid Excel sheet name.

    Excel sheet names:
    - cannot exceed 31 characters
    - cannot contain: : \\ / ? * [ ]
    """
    s = re.sub(r"[:\\/?*\[\]]", "_", str(name))
    s = prefix + s
    return s[:31]


def safe_filename(name: str) -> str:
    """
    Convert a string into a safe filename.

    Keeps only:
    - letters
    - numbers
    - underscore
    - dash

    All other characters are replaced with underscores.
    """
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", str(name))