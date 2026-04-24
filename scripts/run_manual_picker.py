import sys
from pathlib import Path
from tkinter import Tk, filedialog

import pandas as pd

# Ensure src/ is on path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from detector_analysis.io import load_it_data, resolve_device_list, write_results_excel
from detector_analysis.metrics import (
    compute_pulse_metrics_per_device,
    summarize_per_device,
)
from detector_analysis.picker import pick_windows_interactive_shift_undo
from detector_analysis.plotting import plot_all_devices_overlay, save_device_plot_png
from detector_analysis.utils import safe_filename


def select_input_file() -> Path:
    """
    Force the user to select an Excel file via dialog.
    """
    root = Tk()
    root.withdraw()

    filepath = filedialog.askopenfilename(
        title="Select I–t Excel data file",
        filetypes=[
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()

    if not filepath:
        raise FileNotFoundError("No input file was selected.")

    return Path(filepath)


# =============================
# CONFIG
# =============================
SHEET_IT = 0
TIME_COL = "t(ms)"

DEVICES_TO_DO = "ALL"
PLOT_ALL_DEVICES_OVERLAY = True
USE_MEDIAN = True

PLOT_DPI = 200


# =============================
# INPUT FILE
# =============================
FILEPATH = select_input_file()

print("Using input file:", FILEPATH)


# =============================
# OUTPUT PATHS
# =============================
OUTPUT_DIR = ROOT / "outputs"
EXCEL_DIR = OUTPUT_DIR / "excel"
PLOTS_DIR = OUTPUT_DIR / "plots" / FILEPATH.stem

EXCEL_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = EXCEL_DIR / f"{FILEPATH.stem}_Result.xlsx"

print("Output Excel file:", OUTPUT_FILE)
print("Plot folder:", PLOTS_DIR)


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
print("Controls:")
print("  - Click 4 points per pulse: ON_start, ON_end, OFF_start, OFF_end")
print("  - Press 'u' to UNDO")
print("  - SHIFT + click to FINISH current device\n")

for dev in device_list:
    print(f"\n--- Picking windows for {dev} ---")

    on_w, off_w = pick_windows_interactive_shift_undo(
        df_it,
        dev,
        time_col=TIME_COL,
    )

    if len(on_w) == 0 or len(off_w) == 0:
        print(f"[{dev}] No windows picked — skipping.")
        continue

    n = min(len(on_w), len(off_w))

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

    perpulse_dev = compute_pulse_metrics_per_device(
        df_it,
        dev,
        on_w,
        off_w,
        time_col=TIME_COL,
        use_median=USE_MEDIAN,
    )

    all_perpulse.append(perpulse_dev)

    safe_dev = safe_filename(dev)
    png_path = PLOTS_DIR / f"{safe_dev}_manual_windows.png"

    save_device_plot_png(
        df_it,
        dev,
        on_w,
        off_w,
        str(png_path),
        time_col=TIME_COL,
        dpi=PLOT_DPI,
    )

    device_plot_files[dev] = str(png_path)


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
    output_file=str(OUTPUT_FILE),
    windows_df=windows_df,
    perpulse_df=perpulse_df,
    summary_df=summary_df,
    device_plot_files=device_plot_files,
)

print(f"\nSaved results to: {OUTPUT_FILE}")
print(f"Plots saved in: {PLOTS_DIR}")