import numpy as np
import pandas as pd

from detector_analysis.metrics import (
    stat_in_window,
    compute_pulse_metrics_per_device,
    summarize_per_device,
)


def test_stat_in_window_median():
    t = pd.Series([0, 1, 2, 3, 4])
    y = pd.Series([10, 20, 30, 40, 50])

    result = stat_in_window(t, y, 1, 3, use_median=True)

    assert result == 30.0


def test_stat_in_window_mean():
    t = pd.Series([0, 1, 2, 3, 4])
    y = pd.Series([10, 20, 30, 40, 50])

    result = stat_in_window(t, y, 1, 3, use_median=False)

    assert result == 30.0


def test_stat_in_window_returns_nan_for_too_few_points():
    t = pd.Series([0, 1, 2])
    y = pd.Series([10, 20, 30])

    result = stat_in_window(t, y, 2, 2, use_median=True)

    assert np.isnan(result)


def test_compute_pulse_metrics_per_device_basic_case():
    df = pd.DataFrame(
        {
            "t(ms)": [0, 1, 2, 3, 4, 5],
            "B1S1": [1, 1, 5, 5, 2, 2],
        }
    )

    on_windows = [(2, 3)]
    off_windows = [(0, 1)]

    result = compute_pulse_metrics_per_device(
        df=df,
        device="B1S1",
        on_windows=on_windows,
        off_windows=off_windows,
        time_col="t(ms)",
        use_median=True,
    )

    assert len(result) == 1
    assert result.loc[0, "Device"] == "B1S1"
    assert result.loc[0, "Pulse"] == 1
    assert result.loc[0, "I_on_A"] == 5.0
    assert result.loc[0, "I_off_A"] == 1.0
    assert result.loc[0, "I_ph_A"] == 4.0
    assert result.loc[0, "Abs_I_ph_A"] == 4.0
    assert result.loc[0, "OnOff"] == 4.0
    assert result.loc[0, "Method"] == "median"


def test_compute_pulse_metrics_per_device_returns_nan_ratio_if_ioff_zero():
    df = pd.DataFrame(
        {
            "t(ms)": [0, 1, 2, 3],
            "B1S1": [0, 0, 5, 5],
        }
    )

    on_windows = [(2, 3)]
    off_windows = [(0, 1)]

    result = compute_pulse_metrics_per_device(
        df=df,
        device="B1S1",
        on_windows=on_windows,
        off_windows=off_windows,
        time_col="t(ms)",
        use_median=True,
    )

    assert result.loc[0, "I_on_A"] == 5.0
    assert result.loc[0, "I_off_A"] == 0.0
    assert result.loc[0, "I_ph_A"] == 5.0
    assert np.isnan(result.loc[0, "OnOff"])


def test_summarize_per_device():
    perpulse_df = pd.DataFrame(
        {
            "Device": ["B1S1", "B1S1", "B2S1"],
            "Pulse": [1, 2, 1],
            "I_on_A": [5.0, 7.0, 10.0],
            "I_off_A": [1.0, 2.0, 5.0],
            "I_ph_A": [4.0, 5.0, 5.0],
            "Abs_I_ph_A": [4.0, 5.0, 5.0],
            "OnOff": [4.0, 2.5, 1.0],
        }
    )

    summary = summarize_per_device(perpulse_df)

    row_b1s1 = summary[summary["Device"] == "B1S1"].iloc[0]
    row_b2s1 = summary[summary["Device"] == "B2S1"].iloc[0]

    assert row_b1s1["n_pulses"] == 2
    assert row_b1s1["Iph_median"] == 4.5
    assert row_b1s1["Iph_mean"] == 4.5
    assert row_b1s1["Ion_median"] == 6.0
    assert row_b1s1["Ioff_median"] == 1.5

    assert row_b2s1["n_pulses"] == 1
    assert row_b2s1["Iph_median"] == 5.0