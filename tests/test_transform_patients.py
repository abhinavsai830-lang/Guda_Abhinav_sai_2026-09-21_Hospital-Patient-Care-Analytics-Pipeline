import pandas as pd

from src.extract import extract_patients
from src.transform import transform_patients


def test_patient_duplicates_are_removed():

    raw = extract_patients()

    clean = transform_patients(
        raw
    )

    assert len(clean) == 200

    assert clean[
        "patient_id"
    ].is_unique


def test_names_are_cleaned():

    raw = extract_patients()

    clean = transform_patients(
        raw
    )

    assert (
        clean["name"]
        == clean["name"].str.strip()
    ).all()


def test_gender_is_standardized():

    raw = extract_patients()

    clean = transform_patients(
        raw
    )

    valid_genders = {
        "Male",
        "Female",
    }

    assert set(
        clean["gender"].dropna().unique()
    ).issubset(
        valid_genders
    )


def test_dates_are_datetime():

    raw = extract_patients()

    clean = transform_patients(
        raw
    )

    assert pd.api.types.is_datetime64_any_dtype(
        clean["date_of_birth"]
    )

    assert pd.api.types.is_datetime64_any_dtype(
        clean["registration_date"]
    )


def test_age_is_created():

    raw = extract_patients()

    clean = transform_patients(
        raw
    )

    assert "age" in clean.columns

    assert clean["age"].notna().all()

    assert clean["age"].between(
        0,
        120,
    ).all()


def test_age_group_is_created():

    raw = extract_patients()

    clean = transform_patients(
        raw
    )

    assert "age_group" in clean.columns

    valid_groups = {
        "Child",
        "Young Adult",
        "Adult",
        "Middle Aged",
        "Senior",
    }

    assert set(
        clean["age_group"].dropna().unique()
    ).issubset(
        valid_groups
    )


def test_missing_values_are_handled():

    raw = extract_patients()

    clean = transform_patients(
        raw
    )

    assert (
        clean["city"]
        .notna()
        .all()
    )

    assert (
        clean["blood_group"]
        .notna()
        .all()
    )

    assert (
        clean["chronic_condition"]
        .notna()
        .all()
    )