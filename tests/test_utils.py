from detector_analysis.utils import excel_safe_sheet_name, safe_filename


def test_excel_safe_sheet_name_replaces_invalid_characters():
    result = excel_safe_sheet_name("B1/S1:sample[1]")

    assert result == "Plot_B1_S1_sample_1_"


def test_excel_safe_sheet_name_truncates_to_31_characters():
    result = excel_safe_sheet_name("very_long_device_name_that_exceeds_excel_limit")

    assert len(result) <= 31


def test_safe_filename_replaces_invalid_characters():
    result = safe_filename("B1/S1:sample #1")

    assert result == "B1_S1_sample_1"