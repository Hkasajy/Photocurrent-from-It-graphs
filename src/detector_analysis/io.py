import os
from pathlib import Path
from tkinter import Tk, filedialog

import pandas as pd
from openpyxl.drawing.image import Image as XLImage

from detector_analysis.utils import excel_safe_sheet_name


def select_input_file() -> Path:
    """
    Open a file dialog for the user to select the input Excel file.
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


def select_output_file(default_name: str) -> Path:
    """
    Open a file dialog for the user to choose where to save the output Excel file.
    """
    root = Tk()
    root.withdraw()

    filepath = filedialog.asksaveasfilename(
        title="Save results Excel file as",
        defaultextension=".xlsx",
        initialfile=default_name,
        filetypes=[
            ("Excel files", "*.xlsx"),
            ("All files", "*.*"),
        ],
    )

    root.destroy()

    if not filepath:
        raise FileNotFoundError("No output file location was selected.")

    return Path(filepath)


def load_it_data(filepath, sheet_name=0) -> pd.DataFrame:
    """
    Load I-t data from an Excel file.
    """
    return pd.read_excel(filepath, sheet_name=sheet_name)


def resolve_device_list(df: pd.DataFrame, time_col: str, devices_to_do="ALL"):
    """
    Determine which device columns should be analyzed.
    """
    if time_col not in df.columns:
        raise KeyError(
            f"Time column '{time_col}' not found. Available columns: {list(df.columns)}"
        )

    all_devices = [c for c in df.columns if c != time_col]

    if devices_to_do == "ALL":
        return all_devices

    device_list = list(devices_to_do)

    missing = [d for d in device_list if d not in all_devices]
    if missing:
        raise KeyError(
            f"Devices not found in file: {missing}. Available devices: {all_devices}"
        )

    return device_list


def write_results_excel(
    output_file,
    windows_df: pd.DataFrame,
    perpulse_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    device_plot_files: dict,
    sheet_windows: str = "Manual_Windows",
    sheet_perpulse: str = "PerPulse",
    sheet_summary: str = "PerDeviceSummary",
):
    """
    Write analysis results to an Excel workbook and embed per-device plots.
    """
    output_file = Path(output_file)

    output_dir = output_file.parent
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        windows_df.to_excel(writer, sheet_name=sheet_windows, index=False)
        perpulse_df.to_excel(writer, sheet_name=sheet_perpulse, index=False)
        summary_df.to_excel(writer, sheet_name=sheet_summary, index=False)

        wb = writer.book

        for dev, png_path in device_plot_files.items():
            if not os.path.exists(png_path):
                continue

            sheet_name = excel_safe_sheet_name(dev, prefix="Plot_")

            if sheet_name in wb.sheetnames:
                ws_old = wb[sheet_name]
                wb.remove(ws_old)

            ws = wb.create_sheet(sheet_name)
            img = XLImage(png_path)
            ws.add_image(img, "A1")