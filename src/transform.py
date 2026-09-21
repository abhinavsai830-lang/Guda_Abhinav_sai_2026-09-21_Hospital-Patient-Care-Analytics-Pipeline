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