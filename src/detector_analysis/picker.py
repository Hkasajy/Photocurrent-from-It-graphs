"""Interactive picker helpers for detector analysis."""
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import pandas as pd


def pick_windows_interactive_shift_undo(df, device, time_col: str):
    """
    Interactive manual picker for ON/OFF windows.

    Controls
    --------
    - Click 4 times per pulse:
        ON_start, ON_end, OFF_start, OFF_end
    - Press 'u' to undo:
        * removes last click (if mid-pulse)
        * removes last full pulse (if no active clicks)
    - SHIFT + click to finish (only when not mid-pulse)

    Returns
    -------
    on_windows, off_windows : list of tuples
        Lists of (start, end) windows for ON and OFF regions.
    """

    tt = pd.to_numeric(df[time_col], errors="coerce").to_numpy()
    yy = pd.to_numeric(df[device], errors="coerce").to_numpy()

    on_windows = []
    off_windows = []

    clicks = []
    click_markers = []
    pulse_spans = []

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(tt, yy, color="black", linewidth=1)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Current (A)")
    ax.set_title(
        f"DEVICE: {device}\n"
        "Click order: ON_start, ON_end, OFF_start, OFF_end\n"
        "UNDO: 'u' | FINISH: SHIFT + click"
    )
    ax.grid(True)
    plt.tight_layout()

    def redraw():
        fig.canvas.draw_idle()

    def add_marker(x):
        m = ax.axvline(x, color="tab:green", alpha=0.6, linewidth=1)
        click_markers.append(m)

    def clear_markers():
        while click_markers:
            m = click_markers.pop()
            try:
                m.remove()
            except Exception:
                pass

    def finalize_pulse():
        on0, on1 = sorted(clicks[:2])
        off0, off1 = sorted(clicks[2:])

        on_windows.append((float(on0), float(on1)))
        off_windows.append((float(off0), float(off1)))

        on_span = ax.axvspan(on0, on1, color="tab:red", alpha=0.25)
        off_span = ax.axvspan(off0, off1, color="tab:blue", alpha=0.20)
        pulse_spans.append((on_span, off_span))

        print(f"Saved pulse #{len(on_windows)}")
        print(f"  ON : ({on0:.1f}, {on1:.1f}) ms")
        print(f"  OFF: ({off0:.1f}, {off1:.1f}) ms")

    def undo_last_action():
        # Undo last click if in progress
        if len(clicks) > 0:
            x = clicks.pop()

            if click_markers:
                m = click_markers.pop()
                try:
                    m.remove()
                except Exception:
                    pass

            print(f"[{device}] Undo click at t={x:.1f} ms")
            redraw()
            return

        # Otherwise undo last saved pulse
        if len(on_windows) > 0:
            on_windows.pop()
            off_windows.pop()

            on_span, off_span = pulse_spans.pop()

            try:
                on_span.remove()
            except Exception:
                pass
            try:
                off_span.remove()
            except Exception:
                pass

            print(f"[{device}] Undo last pulse")
            redraw()
            return

        print(f"[{device}] Nothing to undo.")

    def is_shift(event):
        return (event.key is not None) and ("shift" in str(event.key).lower())

    def on_click(event):
        if event.inaxes != ax:
            return

        # Finish condition
        if is_shift(event):
            if len(clicks) != 0:
                print(
                    f"[{device}] Unfinished pulse ({len(clicks)} clicks). "
                    f"Undo or complete before finishing."
                )
                return

            print(f"[{device}] Finished. Total pulses: {len(on_windows)}")
            plt.close(fig)
            return

        if event.xdata is None:
            return

        x = float(event.xdata)
        clicks.append(x)
        add_marker(x)

        print(f"[{device}] Click {len(clicks)}/4 at t={x:.1f} ms")
        redraw()

        if len(clicks) == 4:
            finalize_pulse()
            clear_markers()
            clicks.clear()
            redraw()

    def on_key(event):
        if event.key == "u":
            undo_last_action()

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)

    plt.show(block=True)

    return on_windows, off_windows