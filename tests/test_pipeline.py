import pandas as pd

from detector_analysis.io import (
    load_it_data,
    resolve_device_list,
    write_results_excel,
)
from detector_analysis.metrics import (
    compute_pulse_metrics_per_device,
    summarize_per_device,
)


def test_full_non_interactive_pipeline(tmp_path):
    """
    Validates the non-interactive analysis pipeline.

    This test checks:
    - Excel input can be loaded
    - device columns can be resolved
    - predefined ON/OFF windows produce correct photocurrent metrics
    - per-device summary is generated
    - results can be written to an Excel output file

    This test does NOT validate the interactive manual picker.
    """

    # -----------------------------
    # Create controlled sample input
    # -----------------------------
    input_df = pd.DataFrame(
        {
            "t(ms)": [0, 1, 2, 3, 4, 5],
            "S1": [1, 1, 5, 5, 1, 1],
            "S2": [2, 2, 8, 8, 2, 2],
        }
    )

    input_file = tmp_path / "Test Data.xlsx"
    input_df.to_excel(input_file, index=False)

    # -----------------------------
    # Load Excel input
    # -----------------------------
    df_it = load_it_data(input_file, sheet_name=0)

    assert "t(ms)" in df_it.columns
    assert "S1" in df_it.columns
    assert "S2" in df_it.columns

    # -----------------------------
    # Resolve devices
    # -----------------------------
    device_list = resolve_device_list(df_it, time_col="t(ms)", devices_to_do="ALL")

    assert device_list == ["S1", "S2"]

    # -----------------------------
    # Use predefined windows
    # -----------------------------
    on_windows = [(2, 3)]
    off_windows = [(0, 1)]

    all_perpulse = []
    all_windows_rows = []

    for dev in device_list:
        perpulse_dev = compute_pulse_metrics_per_device(
            df=df_it,
            device=dev,
            on_windows=on_windows,
            off_windows=off_windows,
            time_col="t(ms)",
            use_median=True,
        )

        all_perpulse.append(perpulse_dev)

        all_windows_rows.append(
            {
                "Device": dev,
                "Pulse": 1,
                "t_on_start_ms": 2,
                "t_on_end_ms": 3,
                "t_off_start_ms": 0,
                "t_off_end_ms": 1,
            }
        )

    perpulse_df = pd.concat(all_perpulse, ignore_index=True)
    windows_df = pd.DataFrame(all_windows_rows)
    summary_df = summarize_per_device(perpulse_df)

    # -----------------------------
    # Validate numerical results
    # -----------------------------
    row_s1 = perpulse_df[perpulse_df["Device"] == "S1"].iloc[0]
    row_s2 = perpulse_df[perpulse_df["Device"] == "S2"].iloc[0]

    assert row_s1["I_on_A"] == 5
    assert row_s1["I_off_A"] == 1
    assert row_s1["I_ph_A"] == 4
    assert row_s1["OnOff"] == 4

    assert row_s2["I_on_A"] == 8
    assert row_s2["I_off_A"] == 2
    assert row_s2["I_ph_A"] == 6
    assert row_s2["OnOff"] == 3

    # -----------------------------
    # Write output Excel file
    # -----------------------------
    output_file = tmp_path / "Test Data Results.xlsx"

    write_results_excel(
        output_file=output_file,
        windows_df=windows_df,
        perpulse_df=perpulse_df,
        summary_df=summary_df,
        device_plot_files={},  # no plots needed for this test
    )

    assert output_file.exists()

    # -----------------------------
    # Verify output workbook sheets
    # -----------------------------
    sheets = pd.ExcelFile(output_file).sheet_names

    assert "Manual_Windows" in sheets
    assert "PerPulse" in sheets
    assert "PerDeviceSummary" in sheets