from __future__ import annotations

from typing import Any

import pandas as pd

from config import (
    ABNORMAL_VITALS,
    LAB_REFERENCE_RANGES,
    RISK_LEVELS,
    VALID_VITAL_RANGES,
)


# ============================================================
# VALIDATION EXCEPTION
# ============================================================

class DataQualityError(Exception):
    """
    Raised when one or more critical data-quality rules fail.
    """

    pass


# ============================================================
# GENERIC VALIDATION HELPERS
# ============================================================

def validate_required_columns(
    df: pd.DataFrame,
    required_columns: set[str],
    table_name: str,
) -> list[str]:
    """
    Validate that all required columns exist.
    """

    missing_columns = sorted(
        required_columns - set(df.columns)
    )

    if missing_columns:
        return [
            f"{table_name}: missing required columns "
            f"{missing_columns}"
        ]

    return []


def validate_not_empty(
    df: pd.DataFrame,
    table_name: str,
) -> list[str]:
    """
    Validate that a DataFrame contains at least one record.
    """

    if df.empty:
        return [
            f"{table_name}: table is empty"
        ]

    return []


def validate_patient_ids(
    df: pd.DataFrame,
    table_name: str,
) -> list[str]:
    """
    Validate patient_id values.
    """

    errors = []

    if "patient_id" not in df.columns:
        return [
            f"{table_name}: patient_id column missing"
        ]

    if df["patient_id"].isna().any():
        errors.append(
            f"{table_name}: null patient_id values found"
        )

    if (
        df["patient_id"]
        .astype(str)
        .str.strip()
        .eq("")
        .any()
    ):
        errors.append(
            f"{table_name}: empty patient_id values found"
        )

    return errors


def validate_unique_column(
    df: pd.DataFrame,
    column: str,
    table_name: str,
) -> list[str]:
    """
    Validate that a column contains unique values.
    """

    if column not in df.columns:
        return [
            f"{table_name}: column '{column}' missing"
        ]

    if not df[column].is_unique:
        duplicate_count = int(
            df[column].duplicated().sum()
        )

        return [
            f"{table_name}: {duplicate_count} duplicate "
            f"'{column}' values found"
        ]

    return []


def validate_non_negative(
    df: pd.DataFrame,
    column: str,
    table_name: str,
) -> list[str]:
    """
    Validate that values are not negative.
    """

    if column not in df.columns:
        return [
            f"{table_name}: column '{column}' missing"
        ]

    invalid_count = int(
        (df[column] < 0).sum()
    )

    if invalid_count > 0:
        return [
            f"{table_name}: {invalid_count} negative "
            f"values found in '{column}'"
        ]

    return []


def validate_range(
    df: pd.DataFrame,
    column: str,
    low: float,
    high: float,
    table_name: str,
) -> list[str]:
    """
    Validate that values are within an inclusive range.
    """

    if column not in df.columns:
        return [
            f"{table_name}: column '{column}' missing"
        ]

    invalid_count = int(
        (
            (df[column] < low)
            | (df[column] > high)
        ).sum()
    )

    if invalid_count > 0:
        return [
            (
                f"{table_name}: {invalid_count} values "
                f"outside valid range [{low}, {high}] "
                f"for '{column}'"
            )
        ]

    return []


def validate_allowed_values(
    df: pd.DataFrame,
    column: str,
    allowed_values: set[Any],
    table_name: str,
) -> list[str]:
    """
    Validate categorical values against an allowed set.
    """

    if column not in df.columns:
        return [
            f"{table_name}: column '{column}' missing"
        ]

    actual_values = set(
        df[column]
        .dropna()
        .unique()
    )

    invalid_values = sorted(
        actual_values - allowed_values
    )

    if invalid_values:
        return [
            (
                f"{table_name}: invalid values "
                f"{invalid_values} found in '{column}'"
            )
        ]

    return []


# ============================================================
# PATIENT VALIDATION
# ============================================================

def validate_patients(
    patients: pd.DataFrame,
) -> list[str]:

    errors: list[str] = []

    required_columns = {
        "patient_id",
        "name",
        "gender",
        "date_of_birth",
        "age",
        "age_group",
    }

    errors.extend(
        validate_required_columns(
            patients,
            required_columns,
            "patients",
        )
    )

    if errors:
        return errors

    errors.extend(
        validate_not_empty(
            patients,
            "patients",
        )
    )

    errors.extend(
        validate_patient_ids(
            patients,
            "patients",
        )
    )

    errors.extend(
        validate_unique_column(
            patients,
            "patient_id",
            "patients",
        )
    )

    errors.extend(
        validate_non_negative(
            patients,
            "age",
            "patients",
        )
    )

    errors.extend(
        validate_range(
            patients,
            "age",
            0,
            120,
            "patients",
        )
    )

    return errors


# ============================================================
# APPOINTMENT VALIDATION
# ============================================================

def validate_appointments(
    appointments: pd.DataFrame,
    patients: pd.DataFrame,
) -> list[str]:

    errors: list[str] = []

    required_columns = {
        "appointment_id",
        "patient_id",
        "status",
        "waiting_minutes",
        "appointment_date",
        "appointment_hour",
        "day_of_week",
        "is_no_show",
    }

    errors.extend(
        validate_required_columns(
            appointments,
            required_columns,
            "appointments",
        )
    )

    if errors:
        return errors

    errors.extend(
        validate_not_empty(
            appointments,
            "appointments",
        )
    )

    errors.extend(
        validate_patient_ids(
            appointments,
            "appointments",
        )
    )

    errors.extend(
        validate_unique_column(
            appointments,
            "appointment_id",
            "appointments",
        )
    )

    errors.extend(
        validate_non_negative(
            appointments,
            "waiting_minutes",
            "appointments",
        )
    )

    # IMPORTANT:
    # Actual transformed value is "No-Show".
    errors.extend(
        validate_allowed_values(
            appointments,
            "status",
            {
                "Completed",
                "No-Show",
                "Cancelled",
            },
            "appointments",
        )
    )

    errors.extend(
        validate_allowed_values(
            appointments,
            "is_no_show",
            {0, 1},
            "appointments",
        )
    )

    valid_patient_ids = set(
        patients["patient_id"]
    )

    invalid_patient_ids = (
        set(appointments["patient_id"])
        - valid_patient_ids
    )

    if invalid_patient_ids:
        errors.append(
            (
                f"appointments: "
                f"{len(invalid_patient_ids)} patient IDs "
                f"do not exist in patients table"
            )
        )

    return errors


# ============================================================
# LAB VALIDATION
# ============================================================

def validate_lab_results(
    labs: pd.DataFrame,
    patients: pd.DataFrame,
) -> list[str]:

    errors: list[str] = []

    # IMPORTANT:
    # Actual transformed columns are ref_low and ref_high.
    required_columns = {
        "report_id",
        "patient_id",
        "test_name",
        "result_value",
        "unit",
        "report_date",
        "ref_low",
        "ref_high",
        "result_status",
        "is_abnormal",
    }

    errors.extend(
        validate_required_columns(
            labs,
            required_columns,
            "lab_results",
        )
    )

    if errors:
        return errors

    errors.extend(
        validate_not_empty(
            labs,
            "lab_results",
        )
    )

    errors.extend(
        validate_patient_ids(
            labs,
            "lab_results",
        )
    )

    errors.extend(
        validate_unique_column(
            labs,
            "report_id",
            "lab_results",
        )
    )

    errors.extend(
        validate_non_negative(
            labs,
            "result_value",
            "lab_results",
        )
    )

    errors.extend(
        validate_allowed_values(
            labs,
            "result_status",
            {
                "Low",
                "Normal",
                "High",
            },
            "lab_results",
        )
    )

    errors.extend(
        validate_allowed_values(
            labs,
            "is_abnormal",
            {0, 1},
            "lab_results",
        )
    )

    valid_patient_ids = set(
        patients["patient_id"]
    )

    invalid_patient_ids = (
        set(labs["patient_id"])
        - valid_patient_ids
    )

    if invalid_patient_ids:
        errors.append(
            (
                f"lab_results: "
                f"{len(invalid_patient_ids)} patient IDs "
                f"do not exist in patients table"
            )
        )

    # --------------------------------------------------------
    # Reference range validation
    # --------------------------------------------------------

    for test_name, config in LAB_REFERENCE_RANGES.items():

        rows = labs[
            labs["test_name"] == test_name
        ]

        if rows.empty:
            continue

        invalid_low = (
            rows["ref_low"] != config["low"]
        ).sum()

        invalid_high = (
            rows["ref_high"] != config["high"]
        ).sum()

        if invalid_low > 0:
            errors.append(
                (
                    f"lab_results: incorrect ref_low "
                    f"for '{test_name}'"
                )
            )

        if invalid_high > 0:
            errors.append(
                (
                    f"lab_results: incorrect ref_high "
                    f"for '{test_name}'"
                )
            )

    return errors


# ============================================================
# WEARABLE VALIDATION
# ============================================================

def validate_vitals(
    vitals: pd.DataFrame,
    patients: pd.DataFrame,
) -> list[str]:

    errors: list[str] = []

    required_columns = {
        "device_id",
        "patient_id",
        "reading_time",
        "heart_rate",
        "spo2",
        "body_temp",
        "heart_rate_abnormal",
        "spo2_abnormal",
        "body_temp_abnormal",
        "is_abnormal",
    }

    errors.extend(
        validate_required_columns(
            vitals,
            required_columns,
            "vitals",
        )
    )

    if errors:
        return errors

    errors.extend(
        validate_not_empty(
            vitals,
            "vitals",
        )
    )

    errors.extend(
        validate_patient_ids(
            vitals,
            "vitals",
        )
    )

    errors.extend(
        validate_range(
            vitals,
            "heart_rate",
            VALID_VITAL_RANGES["heart_rate"]["low"],
            VALID_VITAL_RANGES["heart_rate"]["high"],
            "vitals",
        )
    )

    errors.extend(
        validate_range(
            vitals,
            "spo2",
            VALID_VITAL_RANGES["spo2"]["low"],
            VALID_VITAL_RANGES["spo2"]["high"],
            "vitals",
        )
    )

    errors.extend(
        validate_range(
            vitals,
            "body_temp",
            VALID_VITAL_RANGES["body_temp"]["low"],
            VALID_VITAL_RANGES["body_temp"]["high"],
            "vitals",
        )
    )

    for column in [
        "heart_rate_abnormal",
        "spo2_abnormal",
        "body_temp_abnormal",
        "is_abnormal",
    ]:
        errors.extend(
            validate_allowed_values(
                vitals,
                column,
                {0, 1},
                "vitals",
            )
        )

    # --------------------------------------------------------
    # Heart-rate flag validation
    # --------------------------------------------------------

    expected_hr_abnormal = (
        (vitals["heart_rate"] > ABNORMAL_VITALS["heart_rate_high"])
        | (vitals["heart_rate"] < ABNORMAL_VITALS["heart_rate_low"])
    ).astype(int)

    if not (
        vitals["heart_rate_abnormal"]
        == expected_hr_abnormal
    ).all():
        errors.append(
            "vitals: heart_rate_abnormal flag is inconsistent"
        )

    # --------------------------------------------------------
    # SpO2 flag validation
    # --------------------------------------------------------

    expected_spo2_abnormal = (
        vitals["spo2"]
        < ABNORMAL_VITALS["spo2_low"]
    ).astype(int)

    if not (
        vitals["spo2_abnormal"]
        == expected_spo2_abnormal
    ).all():
        errors.append(
            "vitals: spo2_abnormal flag is inconsistent"
        )

    # --------------------------------------------------------
    # Temperature flag validation
    # --------------------------------------------------------

    expected_temp_abnormal = (
        vitals["body_temp"]
        > ABNORMAL_VITALS["body_temp_high"]
    ).astype(int)

    if not (
        vitals["body_temp_abnormal"]
        == expected_temp_abnormal
    ).all():
        errors.append(
            "vitals: body_temp_abnormal flag is inconsistent"
        )

    # --------------------------------------------------------
    # Overall abnormal flag validation
    # --------------------------------------------------------

    expected_overall = (
        expected_hr_abnormal
        | expected_spo2_abnormal
        | expected_temp_abnormal
    ).astype(int)

    if not (
        vitals["is_abnormal"]
        == expected_overall
    ).all():
        errors.append(
            "vitals: is_abnormal flag is inconsistent"
        )

    valid_patient_ids = set(
        patients["patient_id"]
    )

    invalid_patient_ids = (
        set(vitals["patient_id"])
        - valid_patient_ids
    )

    if invalid_patient_ids:
        errors.append(
            (
                f"vitals: "
                f"{len(invalid_patient_ids)} patient IDs "
                f"do not exist in patients table"
            )
        )

    return errors


# ============================================================
# DOCTOR NOTES VALIDATION
# ============================================================

def validate_doctor_notes(
    notes: pd.DataFrame,
    patients: pd.DataFrame,
) -> list[str]:

    errors: list[str] = []

    required_columns = {
        "note_id",
        "patient_id",
        "note_text",
        "clean_note_text",
        "symptoms_found",
        "symptom_count",
        "critical_symptoms_found",
        "critical_symptom_count",
        "has_critical_symptom",
    }

    errors.extend(
        validate_required_columns(
            notes,
            required_columns,
            "doctor_notes",
        )
    )

    if errors:
        return errors

    errors.extend(
        validate_not_empty(
            notes,
            "doctor_notes",
        )
    )

    errors.extend(
        validate_patient_ids(
            notes,
            "doctor_notes",
        )
    )

    errors.extend(
        validate_unique_column(
            notes,
            "note_id",
            "doctor_notes",
        )
    )

    errors.extend(
        validate_non_negative(
            notes,
            "symptom_count",
            "doctor_notes",
        )
    )

    errors.extend(
        validate_non_negative(
            notes,
            "critical_symptom_count",
            "doctor_notes",
        )
    )

    errors.extend(
        validate_allowed_values(
            notes,
            "has_critical_symptom",
            {0, 1},
            "doctor_notes",
        )
    )

    valid_patient_ids = set(
        patients["patient_id"]
    )

    invalid_patient_ids = (
        set(notes["patient_id"])
        - valid_patient_ids
    )

    if invalid_patient_ids:
        errors.append(
            (
                f"doctor_notes: "
                f"{len(invalid_patient_ids)} patient IDs "
                f"do not exist in patients table"
            )
        )

    return errors


# ============================================================
# PATIENT RISK VALIDATION
# ============================================================

def validate_patient_risk(
    risk: pd.DataFrame,
    patients: pd.DataFrame,
) -> list[str]:

    errors: list[str] = []

    required_columns = {
        "patient_id",
        "age",
        "total_visits",
        "no_shows",
        "avg_waiting_minutes",
        "no_show_rate",
        "total_lab_results",
        "abnormal_lab_count",
        "avg_heart_rate",
        "min_spo2",
        "abnormal_vital_pct",
        "wearable_readings",
        "total_notes",
        "symptom_count",
        "critical_symptom_notes",
        "risk_score",
        "risk_level",
    }

    errors.extend(
        validate_required_columns(
            risk,
            required_columns,
            "patient_risk_scores",
        )
    )

    if errors:
        return errors

    errors.extend(
        validate_not_empty(
            risk,
            "patient_risk_scores",
        )
    )

    errors.extend(
        validate_patient_ids(
            risk,
            "patient_risk_scores",
        )
    )

    errors.extend(
        validate_unique_column(
            risk,
            "patient_id",
            "patient_risk_scores",
        )
    )

    # Exactly one risk record per patient.
    if len(risk) != len(patients):
        errors.append(
            (
                "patient_risk_scores: "
                "row count does not match patients table"
            )
        )

    valid_patient_ids = set(
        patients["patient_id"]
    )

    invalid_patient_ids = (
        set(risk["patient_id"])
        - valid_patient_ids
    )

    if invalid_patient_ids:
        errors.append(
            (
                f"patient_risk_scores: "
                f"{len(invalid_patient_ids)} invalid patient IDs"
            )
        )

    # --------------------------------------------------------
    # Count fields
    # --------------------------------------------------------

    count_columns = [
        "total_visits",
        "no_shows",
        "total_lab_results",
        "abnormal_lab_count",
        "wearable_readings",
        "total_notes",
        "symptom_count",
        "critical_symptom_notes",
        "risk_score",
    ]

    for column in count_columns:
        errors.extend(
            validate_non_negative(
                risk,
                column,
                "patient_risk_scores",
            )
        )

    # --------------------------------------------------------
    # Percentage fields
    # --------------------------------------------------------

    errors.extend(
        validate_range(
            risk,
            "no_show_rate",
            0,
            1,
            "patient_risk_scores",
        )
    )

    errors.extend(
        validate_range(
            risk,
            "abnormal_vital_pct",
            0,
            1,
            "patient_risk_scores",
        )
    )

    # --------------------------------------------------------
    # Risk levels
    # --------------------------------------------------------

    errors.extend(
        validate_allowed_values(
            risk,
            "risk_level",
            {
                "Low",
                "Medium",
                "High",
            },
            "patient_risk_scores",
        )
    )

    # Verify score → level mapping.
    for _, row in risk.iterrows():

        score = row["risk_score"]
        level = row["risk_level"]

        expected_level = None

        for low, high, configured_level in RISK_LEVELS:

            if low <= score <= high:
                expected_level = configured_level
                break

        if level != expected_level:
            errors.append(
                (
                    f"patient_risk_scores: patient "
                    f"{row['patient_id']} has risk_score={score} "
                    f"but risk_level='{level}'"
                )
            )

    return errors


# ============================================================
# FULL PIPELINE VALIDATION
# ============================================================

def validate_all(
    transformed_data: dict[str, pd.DataFrame],
    raise_on_error: bool = True,
) -> dict[str, Any]:
    """
    Run all validation checks for the transformed pipeline.
    """

    required_tables = {
        "patients",
        "appointments",
        "lab_results",
        "vitals",
        "doctor_notes",
        "patient_risk_scores",
    }

    missing_tables = (
        required_tables
        - set(transformed_data.keys())
    )

    if missing_tables:
        raise DataQualityError(
            f"Missing transformed tables: "
            f"{sorted(missing_tables)}"
        )

    patients = transformed_data["patients"]
    appointments = transformed_data["appointments"]
    labs = transformed_data["lab_results"]
    vitals = transformed_data["vitals"]
    notes = transformed_data["doctor_notes"]
    risk = transformed_data["patient_risk_scores"]

    validation_errors: list[str] = []

    validation_errors.extend(
        validate_patients(patients)
    )

    validation_errors.extend(
        validate_appointments(
            appointments,
            patients,
        )
    )

    validation_errors.extend(
        validate_lab_results(
            labs,
            patients,
        )
    )

    validation_errors.extend(
        validate_vitals(
            vitals,
            patients,
        )
    )

    validation_errors.extend(
        validate_doctor_notes(
            notes,
            patients,
        )
    )

    validation_errors.extend(
        validate_patient_risk(
            risk,
            patients,
        )
    )

    result = {
        "status": (
            "PASS"
            if not validation_errors
            else "FAIL"
        ),
        "error_count": len(validation_errors),
        "errors": validation_errors,
    }

    if validation_errors and raise_on_error:

        formatted_errors = "\n".join(
            f"- {error}"
            for error in validation_errors
        )

        raise DataQualityError(
            "Data quality validation failed:\n"
            f"{formatted_errors}"
        )

    return result