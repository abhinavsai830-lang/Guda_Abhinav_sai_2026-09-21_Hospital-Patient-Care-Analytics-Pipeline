import os

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "hospital_db"),
}


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

RAW_DIR = os.path.join(DATA_DIR, "raw")

PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

REPORTS_DIR = os.path.join(BASE_DIR, "reports")

LOG_DIR = os.path.join(BASE_DIR, "logs")


# ============================================================
# SOURCE FILES
# ============================================================

SOURCE_FILES = {
    "patients": os.path.join(
        RAW_DIR,
        "patients.csv"
    ),

    "appointments": os.path.join(
        RAW_DIR,
        "appointments.csv"
    ),

    "lab_reports": os.path.join(
        RAW_DIR,
        "lab_reports.json"
    ),

    "wearables": os.path.join(
        RAW_DIR,
        "wearables.csv"
    ),

    "doctor_notes": os.path.join(
        RAW_DIR,
        "doctor_notes.csv"
    ),
}
# ============================================================
# LABORATORY REFERENCE RANGES
# ============================================================

LAB_REFERENCE_RANGES = {
    "Hemoglobin": {
        "low": 12.0,
        "high": 17.5,
        "unit": "g/dL",
    },
    "Fasting Blood Sugar": {
        "low": 70.0,
        "high": 100.0,
        "unit": "mg/dL",
    },
    "Total Cholesterol": {
        "low": 0.0,
        "high": 200.0,
        "unit": "mg/dL",
    },
    "Creatinine": {
        "low": 0.6,
        "high": 1.3,
        "unit": "mg/dL",
    },
    "WBC Count": {
        "low": 4.0,
        "high": 11.0,
        "unit": "10^3/uL",
    },
}