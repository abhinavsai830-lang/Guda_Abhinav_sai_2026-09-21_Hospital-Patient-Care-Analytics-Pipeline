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
# ============================================================
# WEARABLE VALIDATION RULES
# ============================================================

VALID_VITAL_RANGES = {
    "heart_rate": {
        "low": 30,
        "high": 220,
    },
    "spo2": {
        "low": 50,
        "high": 100,
    },
    "body_temp": {
        "low": 34.0,
        "high": 43.0,
    },
}


# ============================================================
# WEARABLE ABNORMALITY THRESHOLDS
# ============================================================

ABNORMAL_VITALS = {
    "heart_rate_high": 100,
    "heart_rate_low": 50,
    "spo2_low": 92,
    "body_temp_high": 38.0,
}

# ============================================================
# DOCTOR-NOTE SYMPTOM RULES
# ============================================================

SYMPTOM_KEYWORDS = [
    "chest pain",
    "shortness of breath",
    "dizziness",
    "fever",
    "fatigue",
    "headache",
    "cough",
    "palpitations",
    "swelling",
    "joint pain",
]

CRITICAL_SYMPTOMS = [
    "chest pain",
    "shortness of breath",
    "palpitations",
]