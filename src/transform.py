"""
src/transform.py

Transformation layer for the hospital ETL pipeline.

Responsibilities:
    - Clean raw patient data
    - Standardize fields
    - Create derived attributes
    - Return a clean DataFrame

Important:
    Transformation should not read files directly.
    It receives DataFrames produced by the Extract stage.
"""

from __future__ import annotations

import logging

import pandas as pd


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURATION
# ============================================================

# The date we use to calculate patient age.
# Keep this fixed for reproducible results.
REFERENCE_DATE = pd.Timestamp("2026-09-21")


# ============================================================
# PATIENT TRANSFORMATION
# ============================================================

def transform_patients(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean and standardize patient-registration data.

    Parameters
    ----------
    df:
        Raw patient DataFrame from the Extract stage.

    Returns
    -------
    pd.DataFrame
        Clean patient DataFrame.
    """

    logger.info(
        "Starting patient transformation"
    )

    # --------------------------------------------------------
    # Never modify the extracted DataFrame directly.
    #
    # Creating a copy prevents accidental side effects.
    # --------------------------------------------------------

    df = df.copy()

    before_rows = len(df)

    # ========================================================
    # 1. Remove duplicate patient registrations
    # ========================================================

    df = df.drop_duplicates(
        subset=["patient_id"]
    )

    duplicates_removed = (
        before_rows - len(df)
    )

    logger.info(
        "Removed %d duplicate patient records",
        duplicates_removed,
    )

    # ========================================================
    # 2. Clean patient names
    # ========================================================

    df["name"] = (
        df["name"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    # ========================================================
    # 3. Standardize gender
    # ========================================================

    df["gender"] = (
        df["gender"]
        .astype("string")
        .str.strip()
        .str.lower()
        .map(
            {
                "m": "Male",
                "male": "Male",
                "f": "Female",
                "female": "Female",
            }
        )
    )

    # ========================================================
    # 4. Convert date columns
    # ========================================================

    df["date_of_birth"] = pd.to_datetime(
        df["date_of_birth"],
        errors="coerce",
    )

    df["registration_date"] = pd.to_datetime(
        df["registration_date"],
        errors="coerce",
    )

    # ========================================================
    # 5. Calculate patient age
    # ========================================================

    df["age"] = (
        (
            REFERENCE_DATE
            - df["date_of_birth"]
        ).dt.days // 365
    ).astype("Int64")

    # ========================================================
    # 6. Create age groups
    # ========================================================

    df["age_group"] = pd.cut(
        df["age"].astype(float),
        bins=[
            0,
            12,
            25,
            45,
            60,
            120,
        ],
        labels=[
            "Child",
            "Young Adult",
            "Adult",
            "Middle Aged",
            "Senior",
        ],
        include_lowest=True,
    ).astype("string")

    # ========================================================
    # 7. Handle missing city
    # ========================================================

    df["city"] = (
        df["city"]
        .fillna("Unknown")
        .astype("string")
        .str.strip()
        .str.title()
    )

    # ========================================================
    # 8. Handle missing blood group
    # ========================================================

    df["blood_group"] = (
        df["blood_group"]
        .fillna("Unknown")
        .astype("string")
        .str.strip()
        .str.upper()
    )

    # ========================================================
    # 9. Handle missing chronic condition
    # ========================================================

    df["chronic_condition"] = (
        df["chronic_condition"]
        .fillna("None")
        .astype("string")
        .str.strip()
    )

    logger.info(
        "Patient transformation completed: %d rows",
        len(df),
    )

    return df
# ============================================================
# APPOINTMENT TRANSFORMATION
# ============================================================

def transform_appointments(
        
    df: pd.DataFrame,
    valid_patient_ids: set[str],
) -> pd.DataFrame:
    """
    Clean and transform appointment data.

    Transformations:
        1. Convert timestamp columns
        2. Remove appointments for unknown patients
        3. Calculate waiting time
        4. Remove invalid negative waiting times
        5. Create appointment date
        6. Create appointment hour
        7. Create day of week
        8. Create no-show indicator
    """

    logger.info(
        "Starting appointment transformation"
    )

    df = df.copy()

    before_rows = len(df)

    # ========================================================
    # 1. Convert timestamp columns
    # ========================================================

    datetime_columns = [
        "scheduled_time",
        "checkin_time",
        "consultation_start_time",
    ]

    for column in datetime_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    # ========================================================
    # 2. Referential integrity
    #
    # Every appointment must reference a valid patient.
    # ========================================================

    df = df[
        df["patient_id"].isin(valid_patient_ids)
    ].copy()

    unknown_patients_removed = (
        before_rows - len(df)
    )

    logger.info(
        "Removed %d appointments with unknown patients",
        unknown_patients_removed,
    )

    # ========================================================
    # 3. Calculate waiting time
    #
    # Only completed appointments have meaningful
    # check-in and consultation timestamps.
    # ========================================================

    df["waiting_minutes"] = pd.NA

    completed_mask = (
        df["status"] == "Completed"
    )

    df.loc[
        completed_mask,
        "waiting_minutes",
    ] = (
        (
            df.loc[
                completed_mask,
                "consultation_start_time",
            ]
            - df.loc[
                completed_mask,
                "checkin_time",
            ]
        )
        .dt.total_seconds()
        / 60
    )

    # ========================================================
    # 4. Remove invalid negative waiting times
    #
    # Example:
    #
    # check-in       = 10:30
    # consultation   = 10:00
    #
    # waiting = -30 minutes
    # ========================================================

    invalid_wait_mask = (
        completed_mask
        & (
            pd.to_numeric(
                df["waiting_minutes"],
                errors="coerce",
            )
            < 0
        )
    )

    invalid_wait_count = (
        invalid_wait_mask.sum()
    )

    df = df[
        ~invalid_wait_mask
    ].copy()

    logger.info(
        "Removed %d appointments with invalid waiting times",
        invalid_wait_count,
    )

    # ========================================================
    # 5. Create appointment date
    # ========================================================

    df["appointment_date"] = (
        df["scheduled_time"].dt.date
    )

    # ========================================================
    # 6. Create appointment hour
    # ========================================================

    df["appointment_hour"] = (
        df["scheduled_time"].dt.hour
    )

    # ========================================================
    # 7. Create day of week
    # ========================================================

    df["day_of_week"] = (
        df["scheduled_time"].dt.day_name()
    )

    # ========================================================
    # 8. Create no-show indicator
    # ========================================================

    df["is_no_show"] = (
        df["status"] == "No-Show"
    ).astype(int)

    # ========================================================
    # Final cleanup
    # ========================================================

    df["waiting_minutes"] = pd.to_numeric(
        df["waiting_minutes"],
        errors="coerce",
    )

    logger.info(
        "Appointment transformation completed: %d rows",
        len(df),
    )

    return df

# ============================================================
# LABORATORY TRANSFORMATION
# ============================================================

def transform_lab_reports(
    df: pd.DataFrame,
    valid_patient_ids: set[str],
) -> pd.DataFrame:
    """
    Clean and transform laboratory reports.

    Transformations:
        1. Convert result values to numeric
        2. Remove missing/invalid results
        3. Remove records for unknown patients
        4. Convert report dates
        5. Add reference ranges
        6. Classify results as Low / Normal / High
        7. Create abnormal-result indicator
    """

    from config import LAB_REFERENCE_RANGES

    logger.info(
        "Starting laboratory transformation"
    )

    df = df.copy()

    # ========================================================
    # 1. Convert result values to numeric
    # ========================================================

    df["result_value"] = pd.to_numeric(
        df["result_value"],
        errors="coerce",
    )

    # ========================================================
    # 2. Remove missing/invalid results
    # ========================================================

    before_result_filter = len(df)

    df = df[
        df["result_value"].notna()
    ].copy()

    removed_invalid_results = (
        before_result_filter - len(df)
    )

    logger.info(
        "Removed %d lab records with missing/invalid results",
        removed_invalid_results,
    )

    # ========================================================
    # 3. Referential integrity
    # ========================================================

    before_patient_filter = len(df)

    df = df[
        df["patient_id"].isin(
            valid_patient_ids
        )
    ].copy()

    removed_unknown_patients = (
        before_patient_filter - len(df)
    )

    logger.info(
        "Removed %d lab records with unknown patients",
        removed_unknown_patients,
    )

    # ========================================================
    # 4. Convert report date
    # ========================================================

    df["report_date"] = pd.to_datetime(
        df["report_date"],
        errors="coerce",
    )

    # ========================================================
    # 5. Add reference ranges
    # ========================================================

    df["ref_low"] = (
        df["test_name"]
        .map(
            lambda test_name:
                LAB_REFERENCE_RANGES[
                    test_name
                ]["low"]
        )
    )

    df["ref_high"] = (
        df["test_name"]
        .map(
            lambda test_name:
                LAB_REFERENCE_RANGES[
                    test_name
                ]["high"]
        )
    )

    # ========================================================
    # 6. Classify the result
    # ========================================================

    df["result_status"] = "Normal"

    df.loc[
        df["result_value"] < df["ref_low"],
        "result_status",
    ] = "Low"

    df.loc[
        df["result_value"] > df["ref_high"],
        "result_status",
    ] = "High"

    # ========================================================
    # 7. Create abnormal flag
    # ========================================================

    df["is_abnormal"] = (
        df["result_status"] != "Normal"
    ).astype(int)

    logger.info(
        "Laboratory transformation completed: %d rows",
        len(df),
    )

    return df

# ============================================================
# WEARABLE TRANSFORMATION
# ============================================================

def transform_wearables(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean and transform wearable-device time-series data.

    Transformations:
        1. Convert reading time
        2. Convert vital columns to numeric
        3. Remove duplicate device readings
        4. Remove physically impossible readings
        5. Remove incomplete vital rows
        6. Create abnormal-vital indicators
    """

    from config import (
        VALID_VITAL_RANGES,
        ABNORMAL_VITALS,
    )

    logger.info(
        "Starting wearable-data transformation"
    )

    df = df.copy()

    before_rows = len(df)

    # ========================================================
    # 1. Convert timestamp
    # ========================================================

    df["reading_time"] = pd.to_datetime(
        df["reading_time"],
        errors="coerce",
    )

    # ========================================================
    # 2. Convert vital columns to numeric
    #
    # This also protects us if the source later contains
    # values such as "98.5" instead of 98.5.
    # ========================================================

    vital_columns = [
        "heart_rate",
        "spo2",
        "body_temp",
    ]

    for column in vital_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # ========================================================
    # 3. Remove duplicate sensor transmissions
    #
    # A device should have at most one reading for a given
    # timestamp.
    # ========================================================

    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=[
            "device_id",
            "reading_time",
        ]
    ).copy()

    duplicates_removed = (
        before_duplicates - len(df)
    )

    logger.info(
        "Removed %d duplicate wearable readings",
        duplicates_removed,
    )

    # ========================================================
    # 4. Remove physically impossible readings
    #
    # These are sensor/data-quality problems, not necessarily
    # patient-health problems.
    # ========================================================

    valid_mask = pd.Series(
        True,
        index=df.index,
    )

    for column, limits in VALID_VITAL_RANGES.items():

        valid_mask &= (
            df[column].between(
                limits["low"],
                limits["high"],
                inclusive="both",
            )
        )

    invalid_physical_count = (
        (~valid_mask).sum()
    )

    df = df[
        valid_mask
    ].copy()

    logger.info(
        "Removed %d physically impossible wearable readings",
        invalid_physical_count,
    )

    # ========================================================
    # 5. Remove rows with missing vital measurements
    # ========================================================

    before_missing_filter = len(df)

    df = df.dropna(
        subset=vital_columns
    ).copy()

    missing_vitals_removed = (
        before_missing_filter - len(df)
    )

    logger.info(
        "Removed %d wearable rows with missing vital values",
        missing_vitals_removed,
    )

    # ========================================================
    # 6. Create abnormal heart-rate indicator
    # ========================================================

    df["heart_rate_abnormal"] = (
        (
            df["heart_rate"]
            > ABNORMAL_VITALS[
                "heart_rate_high"
            ]
        )
        |
        (
            df["heart_rate"]
            < ABNORMAL_VITALS[
                "heart_rate_low"
            ]
        )
    ).astype(int)

    # ========================================================
    # 7. Create abnormal SpO2 indicator
    # ========================================================

    df["spo2_abnormal"] = (
        df["spo2"]
        < ABNORMAL_VITALS[
            "spo2_low"
        ]
    ).astype(int)

    # ========================================================
    # 8. Create abnormal temperature indicator
    # ========================================================

    df["body_temp_abnormal"] = (
        df["body_temp"]
        > ABNORMAL_VITALS[
            "body_temp_high"
        ]
    ).astype(int)

    # ========================================================
    # 9. Overall abnormal-vitals flag
    # ========================================================

    df["is_abnormal"] = (
        (
            df["heart_rate_abnormal"]
            == 1
        )
        |
        (
            df["spo2_abnormal"]
            == 1
        )
        |
        (
            df["body_temp_abnormal"]
            == 1
        )
    ).astype(int)

    logger.info(
        "Wearable transformation completed: %d rows",
        len(df),
    )

    logger.info(
        "Removed %d total rows",
        before_rows - len(df),
    )

    return df

# ============================================================
# DOCTOR NOTE TRANSFORMATION
# ============================================================

def extract_note_symptoms(
    text: str,
    symptom_keywords: list[str],
) -> list[str]:
    """
    Extract known symptom keywords from a consultation note.

    Matching is case-insensitive.

    Parameters
    ----------
    text:
        Cleaned consultation-note text.

    symptom_keywords:
        List of symptoms to search for.

    Returns
    -------
    list[str]
        Symptoms found in the note.
    """

    text_lower = text.lower()

    found = []

    for symptom in symptom_keywords:

        if symptom.lower() in text_lower:
            found.append(symptom)

    return found


def transform_doctor_notes(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean and transform doctor consultation notes.

    Transformations:
        1. Remove notes with missing text
        2. Normalize note text
        3. Convert visit date
        4. Extract symptom keywords
        5. Count symptoms
        6. Identify critical symptoms
        7. Create critical-symptom flag
    """

    from config import (
        SYMPTOM_KEYWORDS,
        CRITICAL_SYMPTOMS,
    )

    logger.info(
        "Starting doctor-note transformation"
    )

    df = df.copy()

    before_rows = len(df)

    # ========================================================
    # 1. Remove rows without note text
    # ========================================================

    df = df.dropna(
        subset=["note_text"]
    ).copy()

    df = df[
        df["note_text"]
        .astype(str)
        .str.strip()
        .ne("")
    ].copy()

    removed_empty_notes = (
        before_rows - len(df)
    )

    logger.info(
        "Removed %d empty doctor notes",
        removed_empty_notes,
    )

    # ========================================================
    # 2. Clean the note text
    # ========================================================

    df["clean_note_text"] = (
        df["note_text"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    # ========================================================
    # 3. Convert visit date
    # ========================================================

    df["visit_date"] = pd.to_datetime(
        df["visit_date"],
        errors="coerce",
    )

    # ========================================================
    # 4. Extract symptoms
    # ========================================================

    df["symptoms_found"] = (
        df["clean_note_text"]
        .apply(
            lambda text:
                extract_note_symptoms(
                    text,
                    SYMPTOM_KEYWORDS,
                )
        )
    )

    # ========================================================
    # 5. Count symptoms
    # ========================================================

    df["symptom_count"] = (
        df["symptoms_found"]
        .apply(len)
    )

    # ========================================================
    # 6. Extract critical symptoms
    # ========================================================

    df["critical_symptoms_found"] = (
        df["clean_note_text"]
        .apply(
            lambda text:
                extract_note_symptoms(
                    text,
                    CRITICAL_SYMPTOMS,
                )
        )
    )

    # ========================================================
    # 7. Count critical symptoms
    # ========================================================

    df["critical_symptom_count"] = (
        df["critical_symptoms_found"]
        .apply(len)
    )

    # ========================================================
    # 8. Create critical-symptom flag
    # ========================================================

    df["has_critical_symptom"] = (
        df["critical_symptom_count"] > 0
    ).astype(int)

    logger.info(
        "Doctor-note transformation completed: %d rows",
        len(df),
    )

    return df