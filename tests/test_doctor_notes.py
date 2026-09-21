from pathlib import Path

import pandas as pd

from config import SOURCE_FILES


EXPECTED_COLUMNS = {
    "note_id",
    "patient_id",
    "doctor_id",
    "visit_date",
    "note_text",
}


def test_doctor_notes_dataset_exists():

    path = Path(
        SOURCE_FILES["doctor_notes"]
    )

    assert path.exists()


def test_doctor_notes_has_expected_columns():

    df = pd.read_csv(
        SOURCE_FILES["doctor_notes"]
    )

    assert EXPECTED_COLUMNS.issubset(
        set(df.columns)
    )


def test_doctor_notes_has_expected_number_of_records():

    df = pd.read_csv(
        SOURCE_FILES["doctor_notes"]
    )

    assert len(df) == 450


def test_doctor_note_ids_are_unique():

    df = pd.read_csv(
        SOURCE_FILES["doctor_notes"]
    )

    assert df["note_id"].is_unique


def test_doctor_notes_have_text():

    df = pd.read_csv(
        SOURCE_FILES["doctor_notes"]
    )

    assert df["note_text"].notna().all()

    assert (
        df["note_text"].str.len() > 0
    ).all()


def test_doctor_notes_contain_critical_symptoms():

    df = pd.read_csv(
        SOURCE_FILES["doctor_notes"]
    )

    text = (
        df["note_text"]
        .str.lower()
    )

    critical_notes = text.str.contains(
        "chest pain|shortness of breath|palpitations",
        regex=True,
    )

    assert critical_notes.any()


def test_doctor_notes_contain_uppercase_variation():

    df = pd.read_csv(
        SOURCE_FILES["doctor_notes"]
    )

    uppercase_notes = (
        df["note_text"]
        == df["note_text"].str.upper()
    )

    assert uppercase_notes.any()