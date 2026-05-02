"""
The functions here allow the user to select the input .xlsx file,
and where to save the .xlsx output file. Also, a popup window will open to allow
the user to select the time column in the sheet, allowing generalization of input files.
"""

import os
from pathlib import Path
import pandas as pd
from openpyxl.drawing.image import Image as XLImage
from detector_analysis.utils import excel_safe_sheet_name
from tkinter import Tk, Toplevel, StringVar, OptionMenu, Button, Label, filedialog

def select_time_column(df: pd.DataFrame) -> str:
    """
    This function opens a dialog allowing the user to select the time column from available columns
    allowing gneralization and preventing naming issues (The user could name the time column as (t, Time, tIme ...))
    """

    columns = [str(c) for c in df.columns]

    if len(columns) == 0:
        raise ValueError("The dataframe has no columns.")

    root = Tk()
    root.withdraw()

    selected_col = StringVar(value=columns[0])
    result = {"value": None}

    window = Toplevel(root)
    window.title(" Select Time Column")
    window.geometry("350x140")
    window.resizable(False, False)

    Label(window, text="Please Select the time column:").pack(pady=10)

    dropdown = OptionMenu(window, selected_col, *columns)
    dropdown.pack(pady=5)

    def confirm():
        result["value"] = selected_col.get()
        window.destroy()
        root.quit()

    Button(window, text="OK", command=confirm).pack(pady=10)

    window.protocol("WM_DELETE_WINDOW", confirm)

    window.grab_set()
    window.focus_force()

    root.mainloop()
    root.destroy()

    if result["value"] is None:
        raise ValueError("You did not select a time coulmn")

    return result["value"]

def _create_hidden_root() -> Tk:
    """
    Create a hidden Tk root window that forces dialogs to appear in front.
    This avoids cases where file dialogs opens behind the users complier or other windows.
    """
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.update()
    return root


def select_input_file() -> Path:
    """
    This function opens a dialog for the user to select the input Excel file, more general than script based inputs.
    """
    root = _create_hidden_root()

    filepath = filedialog.askopenfilename(
        parent=root,
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


def select_output_file(default_name: str, input_file: Path | None = None) -> Path:
    """
    This function opens a file dialog for the user to choose where to save the output Excel file.
    If input_file is provided, prevent overwriting the original input workbook.
    """
    root = _create_hidden_root()

    filepath = filedialog.asksaveasfilename(
        parent=root,
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

    output_file = Path(filepath)

    if input_file is not None:
        input_resolved = Path(input_file).resolve()
        output_resolved = output_file.resolve()

        if output_resolved == input_resolved:
            raise ValueError(
                "Output file cannot be the same as the input file. "
                "Choose a different filename to avoid overwriting the original data."
            )

    return output_file

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