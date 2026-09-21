from src.extract import extract_doctor_notes
from src.transform import transform_doctor_notes


def get_clean_notes():

    raw = extract_doctor_notes()

    return transform_doctor_notes(
        raw
    )


def test_note_text_is_not_empty():

    clean = get_clean_notes()

    assert clean[
        "clean_note_text"
    ].notna().all()

    assert (
        clean[
            "clean_note_text"
        ]
        .str.strip()
        .ne("")
    ).all()


def test_note_dates_are_converted():

    clean = get_clean_notes()

    assert (
        clean["visit_date"]
        .dtype.name.startswith(
            "datetime"
        )
    )


def test_symptom_columns_are_created():

    clean = get_clean_notes()

    expected_columns = {
        "symptoms_found",
        "symptom_count",
        "critical_symptoms_found",
        "critical_symptom_count",
        "has_critical_symptom",
    }

    assert expected_columns.issubset(
        clean.columns
    )


def test_symptom_counts_are_non_negative():

    clean = get_clean_notes()

    assert (
        clean["symptom_count"] >= 0
    ).all()

    assert (
        clean[
            "critical_symptom_count"
        ] >= 0
    ).all()


def test_critical_flag_is_binary():

    clean = get_clean_notes()

    assert set(
        clean[
            "has_critical_symptom"
        ].unique()
    ).issubset(
        {0, 1}
    )


def test_critical_flag_is_correct():

    clean = get_clean_notes()

    expected = (
        clean[
            "critical_symptom_count"
        ] > 0
    ).astype(int)

    assert (
        clean[
            "has_critical_symptom"
        ]
        .reset_index(drop=True)
        .equals(
            expected.reset_index(
                drop=True
            )
        )
    )


def test_critical_symptoms_are_detected():

    clean = get_clean_notes()

    assert (
        clean[
            "has_critical_symptom"
        ].sum()
        > 0
    )


def test_uppercase_notes_are_normalized():

    raw = extract_doctor_notes()

    clean = transform_doctor_notes(
        raw
    )

    assert (
        clean[
            "clean_note_text"
        ]
        == clean[
            "clean_note_text"
        ].str.lower()
    ).all()


def test_transformation_preserves_notes():

    raw = extract_doctor_notes()

    clean = transform_doctor_notes(
        raw
    )

    assert len(clean) > 0

    assert len(clean) <= len(raw)