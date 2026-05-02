# ============================================================
# METRICS MODULE
#
# This module contains the core numerical analysis functions
# for extracting photocurrent-related quantities from I–t data.
#
# The workflow implemented here is:
#   1. Select ON/OFF time windows on the signal.
#   2. Compute representative current values inside each window
#      (median or mean).
#   3. Extract per-pulse quantities:
#        - I_on_A  : current during illumination
#        - I_off_A : dark current
#        - I_ph_A  : photocurrent = I_on_A - I_off_A
#        - OnOff   : (I_on_A - I_off_A) / I_off_A
#   4. Aggregate results per device (for QC / quick inspection).
#
# IMPORTANT:
# - The accuracy of all extracted quantities depends critically
#   on correct window selection (steady-state vs transient).
# - Returned np.nan values indicate insufficient or invalid data
#   within a selected window and should be handled downstream.
#
# This module is independent of:
#   - user interaction (manual picking)
#   - file I/O (Excel reading/writing)
#   - plotting
#
# It is intended to be fully testable and reusable.
# ============================================================
