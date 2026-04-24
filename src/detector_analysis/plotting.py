"""Plotting helpers for detector analysis."""
import matplotlib.pyplot as plt
import pandas as pd


def plot_all_devices_overlay(df, device_list, time_col: str):
    """
    Plot all selected device current traces on one overview figure.
    """
    t = pd.to_numeric(df[time_col], errors="coerce")

    plt.figure(figsize=(9, 4))

    for dev in device_list:
        y = pd.to_numeric(df[dev], errors="coerce")
        plt.plot(t, y, label=dev)

    plt.xlabel("Time (ms)")
    plt.ylabel("Current (A)")
    plt.title("Current vs Time (selected devices)")
    plt.grid(True)
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.show()


def save_device_plot_png(
    df,
    device,
    on_windows,
    off_windows,
    out_png,
    time_col: str,
    dpi: int = 200,
):
    """
    Save a per-device current trace with selected ON/OFF windows shaded.
    """
    tt = pd.to_numeric(df[time_col], errors="coerce")
    yy = pd.to_numeric(df[device], errors="coerce")

    plt.figure(figsize=(10, 4))
    plt.plot(tt, yy, color="black", linewidth=1)

    for t0, t1 in on_windows:
        plt.axvspan(t0, t1, color="tab:red", alpha=0.25)

    for t0, t1 in off_windows:
        plt.axvspan(t0, t1, color="tab:blue", alpha=0.20)

    plt.xlabel("Time (ms)")
    plt.ylabel("Current (A)")
    plt.title(f"{device}: Manual ON/OFF windows")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_png, dpi=dpi)
    plt.close()