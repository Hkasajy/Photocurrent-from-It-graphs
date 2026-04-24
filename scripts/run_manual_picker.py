import os
import re
import sys
from pathlib import Path

# Ensure src/ is on path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd

from detector_analysis.io import load_it_data, resolve_device_list, write_results_excel
from detector_analysis.metrics import (
    compute_pulse_metrics_per_device,
    summarize_per_device,
)
from detector_analysis.plotting import (
    plot_all_devices_overlay,
    save_device_plot_png,
)
from detector_analysis.picker import pick_windows_interactive_shift_undo
from detector_analysis.utils import safe_filename


# =============================
# CONFIG
# =============================
FILEPATH = "Full analysis/X ray/Single crystals/140 cm/Data.xlsx"
SHEET_IT = 0
TIME_COL = "t(ms)"

DEVICES_TO_DO = "ALL"
PLOT_ALL_DEVICES_OVERLAY = True
USE_MEDIAN = True

OUTPUT_FILE = "Full analysis/X ray/Single crystals/140 cm/Results.xlsx"

PLOTS_DIR = "manual_window_plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

PLOT_DPI = 200


# =============================
# LOAD DATA
# =============================
df_it = load_it_data(FILEPATH, sheet_name=SHEET_IT)
device_list = resolve_device_list(df_it, TIME_COL, DEVICES_TO_DO)


# =============================
# OVERVIEW PLOT
# =============================
if PLOT_ALL_DEVICES_OVERLAY:
    plot_all_devices_overlay(df_it, device_list, TIME_COL)


# =============================
# MAIN LOOP
# =============================
all_perpulse = []
all_windows_rows = []
device_plot_files = {}

print("\n=== MANUAL WINDOW PICKING PER DEVICE ===")

for dev in device_list:
    print(f"\n--- Picking windows for {dev} ---")

    on_w, off_w = pick_windows_interactive_shift_undo(df_it, dev, TIME_COL)

    if len(on_w) == 0 or len(off_w) == 0:
        print(f"[{dev}] No windows picked — skipping.")
        continue

    n = min(len(on_w), len(off_w))

    # Store window bounds
    for k in range(n):
        all_windows_rows.append(
            {
                "Device": dev,
                "Pulse": k + 1,
                "t_on_start_ms": on_w[k][0],
                "t_on_end_ms": on_w[k][1],
                "t_off_start_ms": off_w[k][0],
                "t_off_end_ms": off_w[k][1],
            }
        )

    # Compute metrics
    perpulse_dev = compute_pulse_metrics_per_device(
        df_it,
        dev,
        on_w,
        off_w,
        time_col=TIME_COL,
        use_median=USE_MEDIAN,
    )

    all_perpulse.append(perpulse_dev)

    # Save plot
    safe_dev = safe_filename(dev)
    png_path = os.path.join(PLOTS_DIR, f"{safe_dev}_manual_windows.png")

    save_device_plot_png(
        df_it,
        dev,
        on_w,
        off_w,
        png_path,
        time_col=TIME_COL,
        dpi=PLOT_DPI,
    )

    device_plot_files[dev] = png_path


if len(all_perpulse) == 0:
    raise ValueError("No results: no windows were selected.")

perpulse_df = pd.concat(all_perpulse, ignore_index=True)
windows_df = pd.DataFrame(all_windows_rows)

summary_df = summarize_per_device(perpulse_df)

print("\nPer-device summary:")
print(summary_df)


# =============================
# WRITE OUTPUT
# =============================
write_results_excel(
    OUTPUT_FILE,
    windows_df,
    perpulse_df,
    summary_df,
    device_plot_files,
)

print(f"\nSaved results to: {OUTPUT_FILE}")
print(f"Plots saved in: {PLOTS_DIR}")