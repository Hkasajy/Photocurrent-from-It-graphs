import numpy as np
import pandas as pd


def stat_in_window(t_series, y_series, t0, t1, use_median: bool = True) -> float:

    """
    This function finds the signal value from the user defined time window.
    The parameters are as follows:
    t_series-> the time vector. (pandas.Series)
    y_series-> current value/signal vector (pandas.Series)
    t0, and t1-> the user defined time window start and end time. (float)
    use_median -> if True-> median value in the window will be returned, if False-> mean value will be returned.

    The function will return a float of the signal value per window.
    If the user selects less than 2 time points, np.nan will be returned.
     """

    t_num = pd.to_numeric(t_series, errors="coerce")
    y_num = pd.to_numeric(y_series, errors="coerce")

    m = (t_num >= t0) & (t_num <= t1) & np.isfinite(t_num) & np.isfinite(y_num)

    if m.sum() < 2:
        return np.nan

    if use_median:
        return float(np.median(y_num[m]))
    return float(np.mean(y_num[m]))


def compute_pulse_metrics_per_device(
    df: pd.DataFrame,
    device: str,
    on_windows,
    off_windows,
    time_col: str,
    use_median: bool = True,
) -> pd.DataFrame:
    """
    This functino finds the per pulse photocurrent for one device.

    It outputs the following qauntities:
    I_on_A -> current in the on window (photoinduced current !not photocurrent!),
    I_off_A-> current in the off window (dark current),
    I_ph ->  I_on_A - I_off_A (photocurrent),
    Abs_I_ph_A -> Abs_I_ph_A (photocurrent),
    OnOff -> the on off ratio, here defined as  I_ph_A / I_off_A.

    It takes the following parameters:

    df -> Input table with time column and device current column (pandas.DataFrame),
    device -> device label/ assumed to contain current values (str),
    on_windows -> list of on windows (list[tuple[float, float]]),
    off_windows -> list of off windows (list[tuple[float, float]]),
    time_col -> time column name (str),
    use_median -> if True-> median value in the window will be returned, otherwise mean.

    The returns are Per-pulse results table (pandas.DataFrame).

    """
    if time_col not in df.columns:
        raise KeyError(f"Time column '{time_col}' not found in dataframe.")

    if device not in df.columns:
        raise KeyError(f"Device column '{device}' not found in dataframe.")

    t_series = df[time_col]
    n = min(len(on_windows), len(off_windows))

    rows = []
    for k in range(n):
        on0, on1 = on_windows[k]
        off0, off1 = off_windows[k]

        ion = stat_in_window(t_series, df[device], on0, on1, use_median=use_median)
        ioff = stat_in_window(t_series, df[device], off0, off1, use_median=use_median)

        if np.isnan(ion) or np.isnan(ioff):
            iph = np.nan
        else:
            iph = ion - ioff

        # OnOff = (Iphoto - Idark) / Idark = (Ion - Ioff) / Ioff = Iph / Ioff (on off defintion)

        if np.isnan(iph) or np.isnan(ioff) or ioff == 0:
            ratio = np.nan
        else:
            ratio = iph / ioff

        rows.append(
            {
                "Device": device,
                "Pulse": k + 1,
                "I_on_A": ion,
                "I_off_A": ioff,
                "I_ph_A": iph,
                "Abs_I_ph_A": np.abs(iph) if np.isfinite(iph) else np.nan,
                "OnOff": ratio,
                "t_on_start_ms": on0,
                "t_on_end_ms": on1,
                "t_off_start_ms": off0,
                "t_off_end_ms": off1,
                "Method": "median" if use_median else "mean",
            }
        )

    return pd.DataFrame(rows)


def summarize_per_device(perpulse_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a per-device summary table from the per-pulse table.
    !!!! This summary should only be used to detect broken devices, there is no physics here. !!!!
    """
    if perpulse_df.empty:
        return pd.DataFrame(
            columns=[
                "Device",
                "n_pulses",
                "Iph_median",
                "Iph_mean",
                "Abs_Iph_median",
                "Ion_median",
                "Ioff_median",
                "OnOff_median",
                "OnOff_mean",
            ]
        )

    summary_df = (
        perpulse_df
        .groupby("Device", as_index=False)
        .agg(
            n_pulses=("Pulse", "max"),
            Iph_median=("I_ph_A", "median"),
            Iph_mean=("I_ph_A", "mean"),
            Abs_Iph_median=("Abs_I_ph_A", "median"),
            Ion_median=("I_on_A", "median"),
            Ioff_median=("I_off_A", "median"),
            OnOff_median=("OnOff", "median"),
            OnOff_mean=("OnOff", "mean"),
        )
        .sort_values("Iph_median", ascending=False)
    )

    return summary_df

__all__ = [
    "stat_in_window",
    "compute_pulse_metrics_per_device",
    "summarize_per_device",
]
