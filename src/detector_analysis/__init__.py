"""Core analysis package for photocurrent I-t processing."""

from .metrics import (
    compute_pulse_metrics_per_device,
    stat_in_window,
    summarize_per_device,
)

__all__ = [
    "compute_pulse_metrics_per_device",
    "stat_in_window",
    "summarize_per_device",
]

__version__ = "0.1.0"
