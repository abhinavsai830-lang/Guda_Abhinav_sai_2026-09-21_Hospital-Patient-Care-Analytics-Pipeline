import pandas as pd

from src.extract import (
    extract,
    extract_appointments,
    extract_doctor_notes,
    extract_lab_reports,
    extract_patients,
    extract_wearables,
)


def test_extract_patients():

    df = extract_patients()

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert len(df) == 206


def test_extract_appointments():

    df = extract_appointments()

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert len(df) == 1200


def test_extract_lab_reports():

    df = extract_lab_reports()

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert len(df) > 0

    assert {
        "report_id",
        "patient_id",
        "test_name",
        "result_value",
        "unit",
        "report_date",
    }.issubset(
        df.columns
    )


def test_extract_wearables():

    df = extract_wearables()

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert len(df) == 4360


def test_extract_doctor_notes():

    df = extract_doctor_notes()

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert len(df) == 450


def test_extract_all_sources():

    raw_data = extract()

    expected_sources = {
        "patients",
        "appointments",
        "lab_reports",
        "wearables",
        "doctor_notes",
    }

    assert set(
        raw_data.keys()
    ) == expected_sources

    for name, df in raw_data.items():

        assert isinstance(
            df,
            pd.DataFrame,
        )

        assert len(df) > 0