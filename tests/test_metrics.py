import numpy as np
import pandas as pd
import pytest

from detector_analysis.metrics import (
    stat_in_window,
    compute_pulse_metrics_per_device,
    summarize_per_device,
)


def test_stat_in_window_returns_median_value_inside_selected_window():
    """
    Validate that stat_in_window returns the median signal value
    from points whose time values fall inside the selected window.
    """
    t = pd.Series([0, 1, 2, 3, 4])
    y = pd.Series([10, 20, 30, 40, 50])

    result = stat_in_window(t, y, 1, 3, use_median=True)

    assert result == pytest.approx(30.0)


def test_stat_in_window_returns_mean_value_inside_selected_window():
    """
    Validate that stat_in_window returns the mean signal value
    when use_median=False.
    """
    t = pd.Series([0, 1, 2, 3, 4])
    y = pd.Series([10, 20, 30, 40, 50])

    result = stat_in_window(t, y, 1, 3, use_median=False)

    assert result == pytest.approx(30.0)


def test_stat_in_window_returns_nan_for_too_few_points():
    """
    Validate that windows containing fewer than two valid sampled points
    are treated as invalid and return NaN.
    """
    t = pd.Series([0, 1, 2])
    y = pd.Series([10, 20, 30])

    result = stat_in_window(t, y, 2, 2, use_median=True)

    assert np.isnan(result)


def test_compute_pulse_metrics_per_device_basic_case():
    """
    Validate per-pulse metric extraction for a simple deterministic trace.

    The selected OFF window has current 1 A and the selected ON window
    has current 5 A, so the expected photocurrent is 4 A and the
    on/off ratio is 4.
    """
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
    assert result.loc[0, "I_on_A"] == pytest.approx(5.0)
    assert result.loc[0, "I_off_A"] == pytest.approx(1.0)
    assert result.loc[0, "I_ph_A"] == pytest.approx(4.0)
    assert result.loc[0, "Abs_I_ph_A"] == pytest.approx(4.0)
    assert result.loc[0, "OnOff"] == pytest.approx(4.0)
    assert result.loc[0, "Method"] == "median"


def test_compute_pulse_metrics_per_device_returns_nan_ratio_if_ioff_zero():
    """
    Validate that the on/off ratio is set to NaN when the OFF current is zero.

    This avoids returning an infinite or misleading ratio caused by division
    by zero.
    """
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

    assert result.loc[0, "I_on_A"] == pytest.approx(5.0)
    assert result.loc[0, "I_off_A"] == pytest.approx(0.0)
    assert result.loc[0, "I_ph_A"] == pytest.approx(5.0)
    assert np.isnan(result.loc[0, "OnOff"])


def test_summarize_per_device_aggregates_per_pulse_results():
    """
    Validate that summarize_per_device groups per-pulse results by device
    and computes the expected summary statistics.
    """
    per_pulse_df = pd.DataFrame(
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

    summary = summarize_per_device(per_pulse_df)

    row_b1s1 = summary[summary["Device"] == "B1S1"].iloc[0]
    row_b2s1 = summary[summary["Device"] == "B2S1"].iloc[0]

    assert row_b1s1["n_pulses"] == 2
    assert row_b1s1["Iph_median"] == pytest.approx(4.5)
    assert row_b1s1["Iph_mean"] == pytest.approx(4.5)
    assert row_b1s1["Ion_median"] == pytest.approx(6.0)
    assert row_b1s1["Ioff_median"] == pytest.approx(1.5)

    assert row_b2s1["n_pulses"] == 1
    assert row_b2s1["Iph_median"] == pytest.approx(5.0)