import pandas as pd
from detector_analysis.metrics import compute_pulse_metrics_per_device


def test_pipeline_simple_case():
    df = pd.DataFrame({
        "t(ms)": [0, 1, 2, 3, 4, 5],
        "S1": [1, 1, 5, 5, 1, 1],
    })

    on_w = [(2, 3)]
    off_w = [(0, 1)]

    result = compute_pulse_metrics_per_device(
        df, "S1", on_w, off_w, time_col="t(ms)"
    )

    row = result.iloc[0]

    assert row["I_on_A"] == 5
    assert row["I_off_A"] == 1
    assert row["I_ph_A"] == 4
    assert row["OnOff"] == 4