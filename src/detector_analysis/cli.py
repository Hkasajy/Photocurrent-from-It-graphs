from pathlib import Path
import pandas as pd

from .io import select_input_file, select_output_file, select_time_column, load_it_data, resolve_device_list, \
    write_results_excel
from .metrics import compute_pulse_metrics_per_device, summarize_per_device
from .picker import pick_windows_interactive_shift_undo
from .plotting import plot_all_devices_overlay, save_device_plot_png
from .utils import safe_filename

# CONFIGURATION DEFAULTS (You may need to edit these, although full operation can be completed without)

SHEET_IT = 0     #Assuming data is in 1st sheet.
DEVICES_TO_DO = "ALL" #Use "ALL" to process all device columns, or a list such as ["S1","S2"]
PLOT_ALL_DEVICES_OVERLAY = True #Shows an overview plot before manual window selection.
USE_MEDIAN = True #Median is more robust against spikes, transients, and outliers inside the selected window.
PLOT_DPI = 200

def validate_window_pairs(device: str, on_windows, off_windows) -> None:
    """
    This function makes sure that the number of ON and OFF windows is the same, this goes back to the definition of photocurrent,
    as there must be a dark current to calculate it per pulse.
    """
    if len(on_windows) != len(off_windows):
        raise ValueError(
            f"Mismatch between ON and OFF windows for device '{device}': "
            f"{len(on_windows)} ON windows and {len(off_windows)} OFF windows."
        )


def build_window_rows(device: str, on_windows, off_windows) -> list[dict]:

    #This function numbers each peak to allow easier tracking in output files.

    validate_window_pairs(device, on_windows, off_windows)

    rows = []
    for pulse_index, (on_window, off_window) in enumerate(
        zip(on_windows, off_windows),
        start=1,
    ):
        on_start, on_end = on_window
        off_start, off_end = off_window

        rows.append(
            {
                "Device": device,
                "Pulse": pulse_index,
                "t_on_start_ms": on_start,
                "t_on_end_ms": on_end,
                "t_off_start_ms": off_start,
                "t_off_end_ms": off_end,
            }
        )

    return rows

def main() -> None:
    """
    This function runs the manual ON/OFF window selection workflow, as follows:
    1. The select_input_file function select the input Excel file, while the select_output_file
    selects the output file adding _Result to the input files name.
    2. The load_it_data function loads the I-t data, and the select_time_column function allows the user
    to select the time column.
    5. Select ON/OFF windows manually for each device.
    6. Compute photocurrent metrics.
    7. Save result tables and plots.
    """

    input_file = select_input_file()
    print(f"Data taken from: {input_file}")
    default_output_name = f"{input_file.stem}_Result.xlsx"
    output_file = select_output_file(default_output_name, input_file=input_file)
    print(f"Output Excel file: {output_file}")

    # Save plot PNGs next to the selected output workbook.
    plots_dir = output_file.parent / f"{output_file.stem}_plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    print(f"Plot folder: {plots_dir}")
    # Load the It data and select the time column
    df_it = load_it_data(input_file, sheet_name=SHEET_IT)

    time_col = select_time_column(df_it)
    print(f"Selected time column: {time_col}")
    #List the devices and rise an error if no data is loaded
    device_list = resolve_device_list(df_it, time_col, DEVICES_TO_DO)

    if len(device_list) == 0:
        raise ValueError("No device columns found after excluding the selected time column.")

    print(f"Devices to process: {device_list}")

    # Optional overview plot
    if PLOT_ALL_DEVICES_OVERLAY:
        plot_all_devices_overlay(df_it, device_list, time_col)

    # Manual time window selection and computations

    all_per_pulse = []
    all_window_rows = []
    device_plot_files = {}

    for device in device_list:
        print(f"\n--- Processing device {device} ---")

        on_windows, off_windows = pick_windows_interactive_shift_undo(
            df_it,
            device,
            time_col=time_col,
        )

        if len(on_windows) == 0 and len(off_windows) == 0:
            print(f"[{device}] No windows were selected — skipping.")
            continue

        validate_window_pairs(device, on_windows, off_windows)

        all_window_rows.extend(
            build_window_rows(device, on_windows, off_windows)
        )

        per_pulse_device = compute_pulse_metrics_per_device(
            df=df_it,
            device=device,
            on_windows=on_windows,
            off_windows=off_windows,
            time_col=time_col,
            use_median=USE_MEDIAN,
        )

        all_per_pulse.append(per_pulse_device)

        safe_device_name = safe_filename(device)
        png_path = plots_dir / f"{safe_device_name}_manual_windows.png"

        save_device_plot_png(
            df=df_it,
            device=device,
            on_windows=on_windows,
            off_windows=off_windows,
            out_png=str(png_path),
            time_col=time_col,
            dpi=PLOT_DPI,
        )

        device_plot_files[device] = str(png_path)

    if len(all_per_pulse) == 0:
        raise ValueError("No results: no valid windows were selected for any device.")


    # Output tables are built here

    per_pulse_df = pd.concat(all_per_pulse, ignore_index=True)
    windows_df = pd.DataFrame(all_window_rows)
    summary_df = summarize_per_device(per_pulse_df)

    print("\nPer-device summary:")
    print(summary_df)

    # Write output sheet

    write_results_excel(
        output_file=str(output_file),
        windows_df=windows_df,
        perpulse_df=per_pulse_df,
        summary_df=summary_df,
        device_plot_files=device_plot_files,
    )

    print(f"\nDone, results saved to: {output_file}")
    print(f"Plots were also saved here: {plots_dir}")

if __name__ == "__main__":
    main()