"""
src/extract.py

Extraction layer of the hospital ETL pipeline.

Responsibilities:
    1. Read raw hospital source files.
    2. Convert each source into a pandas DataFrame.
    3. Preserve the raw values exactly as much as practical.
    4. Return all extracted datasets to the next ETL stage.

Important:
    This module does NOT perform business cleaning or validation.

    Cleaning belongs to the Transform stage.
    Data-quality checks belong to the Validation stage.
"""

from __future__ import annotations

import json
import logging
from typing import Dict

import pandas as pd

from config import SOURCE_FILES


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# PATIENT EXTRACTION
# ============================================================

def extract_patients() -> pd.DataFrame:
    """
    Extract patient-registration data from CSV.

    Returns
    -------
    pd.DataFrame
        Raw patient registration records.
    """

    file_path = SOURCE_FILES["patients"]

    logger.info(
        "Reading patient data from %s",
        file_path,
    )

    df = pd.read_csv(
        file_path
    )

    logger.info(
        "Extracted %d patient rows",
        len(df),
    )

    return df


# ============================================================
# APPOINTMENT EXTRACTION
# ============================================================

def extract_appointments() -> pd.DataFrame:
    """
    Extract appointment data from CSV.

    Returns
    -------
    pd.DataFrame
        Raw appointment records.
    """

    file_path = SOURCE_FILES["appointments"]

    logger.info(
        "Reading appointment data from %s",
        file_path,
    )

    df = pd.read_csv(
        file_path
    )

    logger.info(
        "Extracted %d appointment rows",
        len(df),
    )

    return df


# ============================================================
# LAB REPORT EXTRACTION
# ============================================================

def extract_lab_reports() -> pd.DataFrame:
    """
    Extract laboratory reports from nested JSON.

    The JSON structure looks like:

        {
            "source": "...",
            "generated_at": "...",
            "reports": [
                {...},
                {...}
            ]
        }

    The 'reports' list is flattened into a DataFrame.

    Returns
    -------
    pd.DataFrame
        Raw laboratory report records.
    """

    file_path = SOURCE_FILES["lab_reports"]

    logger.info(
        "Reading laboratory data from %s",
        file_path,
    )

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    reports = data.get(
        "reports",
        [],
    )

    df = pd.json_normalize(
        reports
    )

    logger.info(
        "Extracted %d laboratory report rows",
        len(df),
    )

    return df


# ============================================================
# WEARABLE EXTRACTION
# ============================================================

def extract_wearables() -> pd.DataFrame:
    """
    Extract wearable-device readings from CSV.

    Returns
    -------
    pd.DataFrame
        Raw time-series wearable readings.
    """

    file_path = SOURCE_FILES["wearables"]

    logger.info(
        "Reading wearable data from %s",
        file_path,
    )

    df = pd.read_csv(
        file_path
    )

    logger.info(
        "Extracted %d wearable rows",
        len(df),
    )

    return df


# ============================================================
# DOCTOR NOTE EXTRACTION
# ============================================================

def extract_doctor_notes() -> pd.DataFrame:
    """
    Extract doctor consultation notes from CSV.

    Returns
    -------
    pd.DataFrame
        Raw consultation notes.
    """

    file_path = SOURCE_FILES["doctor_notes"]

    logger.info(
        "Reading doctor notes from %s",
        file_path,
    )

    df = pd.read_csv(
        file_path
    )

    logger.info(
        "Extracted %d doctor-note rows",
        len(df),
    )

    return df


# ============================================================
# EXTRACT ALL SOURCES
# ============================================================

def extract() -> Dict[str, pd.DataFrame]:
    """
    Extract all hospital source datasets.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary containing one DataFrame for each
        hospital source system.
    """

    logger.info(
        "Starting extraction of all hospital sources"
    )

    raw_data = {
        "patients": extract_patients(),

        "appointments": extract_appointments(),

        "lab_reports": extract_lab_reports(),

        "wearables": extract_wearables(),

        "doctor_notes": extract_doctor_notes(),
    }

    logger.info(
        "Extraction completed successfully"
    )

    for name, df in raw_data.items():

        logger.info(
            "%-15s : %6d rows | %2d columns",
            name,
            len(df),
            len(df.columns),
        )

    return raw_data