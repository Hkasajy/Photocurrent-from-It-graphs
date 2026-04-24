import pandas as pd
import pytest

from detector_analysis.io import resolve_device_list


def test_resolve_device_list_all_devices():
    df = pd.DataFrame({
        "t(ms)": [0, 1],
        "S1": [1, 2],
        "S2": [3, 4],
    })

    devices = resolve_device_list(df, time_col="t(ms)", devices_to_do="ALL")

    assert devices == ["S1", "S2"]


def test_resolve_device_list_selected_devices():
    df = pd.DataFrame({
        "t(ms)": [0, 1],
        "S1": [1, 2],
        "S2": [3, 4],
    })

    devices = resolve_device_list(df, time_col="t(ms)", devices_to_do=["S2"])

    assert devices == ["S2"]


def test_resolve_device_list_missing_time_column():
    df = pd.DataFrame({
        "time": [0, 1],
        "S1": [1, 2],
    })

    with pytest.raises(KeyError):
        resolve_device_list(df, time_col="t(ms)", devices_to_do="ALL")


def test_resolve_device_list_missing_device():
    df = pd.DataFrame({
        "t(ms)": [0, 1],
        "S1": [1, 2],
    })

    with pytest.raises(KeyError):
        resolve_device_list(df, time_col="t(ms)", devices_to_do=["S2"])