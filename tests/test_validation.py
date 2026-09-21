import pandas as pd
import pytest

from src.extract import extract
from src.transform import transform
from src.validation import (
    DataQualityError,
    validate_all,
    validate_patients,
    validate_appointments,
    validate_lab_results,
    validate_vitals,
    validate_doctor_notes,
    validate_patient_risk,
)


@pytest.fixture
def transformed_data():
    """
    Generate the complete clean dataset once per test.
    """
    raw_data = extract()

    return transform(raw_data)


# ============================================================
# FULL PIPELINE VALIDATION
# ============================================================

def test_full_validation_passes(transformed_data):

    result = validate_all(
        transformed_data,
        raise_on_error=False,
    )

    assert result["status"] == "PASS"
    assert result["error_count"] == 0
    assert result["errors"] == []


# ============================================================
# PATIENT VALIDATION
# ============================================================

def test_patient_ids_are_unique(transformed_data):

    patients = transformed_data["patients"]

    errors = validate_patients(patients)

    assert errors == []


def test_duplicate_patient_ids_are_detected(transformed_data):

    patients = transformed_data["patients"].copy()

    duplicate_row = patients.iloc[[0]].copy()

    patients = pd.concat(
        [patients, duplicate_row],
        ignore_index=True,
    )

    errors = validate_patients(patients)

    assert any(
        "duplicate" in error.lower()
        for error in errors
    )


# ============================================================
# APPOINTMENT VALIDATION
# ============================================================

def test_appointments_have_valid_waiting_times(
    transformed_data,
):

    appointments = transformed_data["appointments"]
    patients = transformed_data["patients"]

    errors = validate_appointments(
        appointments,
        patients,
    )

    assert errors == []


def test_negative_waiting_time_is_detected(
    transformed_data,
):

    appointments = (
        transformed_data["appointments"]
        .copy()
    )

    appointments.loc[
        appointments.index[0],
        "waiting_minutes",
    ] = -10

    patients = transformed_data["patients"]

    errors = validate_appointments(
        appointments,
        patients,
    )

    assert any(
        "negative" in error.lower()
        for error in errors
    )


# ============================================================
# LAB VALIDATION
# ============================================================

def test_lab_results_are_valid(
    transformed_data,
):

    labs = transformed_data["lab_results"]
    patients = transformed_data["patients"]

    errors = validate_lab_results(
        labs,
        patients,
    )

    assert errors == []


def test_invalid_lab_status_is_detected(
    transformed_data,
):

    labs = transformed_data["lab_results"].copy()
    patients = transformed_data["patients"]

    labs.loc[
        labs.index[0],
        "result_status",
    ] = "UNKNOWN"

    errors = validate_lab_results(
        labs,
        patients,
    )

    assert any(
        "invalid values" in error.lower()
        for error in errors
    )


# ============================================================
# VITAL VALIDATION
# ============================================================

def test_vitals_are_within_valid_ranges(
    transformed_data,
):

    vitals = transformed_data["vitals"]
    patients = transformed_data["patients"]

    errors = validate_vitals(
        vitals,
        patients,
    )

    assert errors == []


def test_invalid_heart_rate_is_detected(
    transformed_data,
):

    vitals = transformed_data["vitals"].copy()
    patients = transformed_data["patients"]

    vitals.loc[
        vitals.index[0],
        "heart_rate",
    ] = 500

    errors = validate_vitals(
        vitals,
        patients,
    )

    assert any(
        "outside valid range" in error.lower()
        for error in errors
    )


# ============================================================
# DOCTOR NOTE VALIDATION
# ============================================================

def test_doctor_notes_are_valid(
    transformed_data,
):

    notes = transformed_data["doctor_notes"]
    patients = transformed_data["patients"]

    errors = validate_doctor_notes(
        notes,
        patients,
    )

    assert errors == []


# ============================================================
# RISK VALIDATION
# ============================================================

def test_patient_risk_data_is_valid(
    transformed_data,
):

    risk = transformed_data["patient_risk_scores"]
    patients = transformed_data["patients"]

    errors = validate_patient_risk(
        risk,
        patients,
    )

    assert errors == []


def test_invalid_risk_level_is_detected(
    transformed_data,
):

    risk = (
        transformed_data["patient_risk_scores"]
        .copy()
    )

    patients = transformed_data["patients"]

    risk.loc[
        risk.index[0],
        "risk_level",
    ] = "Unknown"

    errors = validate_patient_risk(
        risk,
        patients,
    )

    assert any(
        "invalid values" in error.lower()
        for error in errors
    )


def test_risk_score_level_mismatch_is_detected(
    transformed_data,
):

    risk = (
        transformed_data["patient_risk_scores"]
        .copy()
    )

    patients = transformed_data["patients"]

    risk.loc[
        risk.index[0],
        "risk_score",
    ] = 1

    risk.loc[
        risk.index[0],
        "risk_level",
    ] = "High"

    errors = validate_patient_risk(
        risk,
        patients,
    )

    assert any(
        "risk_score" in error
        and "risk_level" in error
        for error in errors
    )


# ============================================================
# FAIL-FAST BEHAVIOR
# ============================================================

def test_validation_can_raise_error(
    transformed_data,
):

    risk = (
        transformed_data["patient_risk_scores"]
        .copy()
    )

    risk.loc[
        risk.index[0],
        "risk_level",
    ] = "INVALID"

    modified_data = transformed_data.copy()
    modified_data["patient_risk_scores"] = risk

    with pytest.raises(DataQualityError):

        validate_all(
            modified_data,
            raise_on_error=True,
        )