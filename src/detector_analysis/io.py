"""I/O helpers for detector analysis."""
import os

import pandas as pd
from openpyxl.drawing.image import Image as XLImage

from detector_analysis.utils import excel_safe_sheet_name


def load_it_data(filepath, sheet_name=0) -> pd.DataFrame:
    """
    Load I-t data from an Excel file.

    Parameters
    ----------
    filepath : str
        Path to the Excel file.
    sheet_name : int or str
        Sheet index or sheet name.

    Returns
    -------
    pandas.DataFrame
        Loaded I-t data.
    """
    return pd.read_excel(filepath, sheet_name=sheet_name)


def resolve_device_list(df: pd.DataFrame, time_col: str, devices_to_do="ALL"):
    """
    Determine which device columns should be analyzed.

    Parameters
    ----------
    df : pandas.DataFrame
        Input I-t dataframe.
    time_col : str
        Name of the time column.
    devices_to_do : str or list[str]
        Either "ALL" or a list of selected device names.

    Returns
    -------
    list[str]
        Device columns to analyze.
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

    Parameters
    ----------
    output_file : str
        Output Excel file path.
    windows_df : pandas.DataFrame
        DataFrame containing selected ON/OFF window bounds.
    perpulse_df : pandas.DataFrame
        DataFrame containing per-pulse extracted metrics.
    summary_df : pandas.DataFrame
        DataFrame containing per-device summary metrics.
    device_plot_files : dict
        Dictionary mapping device names to saved PNG plot paths.
    sheet_windows : str
        Name of the manual-window sheet.
    sheet_perpulse : str
        Name of the per-pulse sheet.
    sheet_summary : str
        Name of the summary sheet.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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