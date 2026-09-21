import pandas as pd

from src.extract import (
    extract_lab_reports,
    extract_patients,
)

from src.transform import (
    transform_lab_reports,
)


def get_clean_labs():
    patients = extract_patients()
    labs = extract_lab_reports()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    return transform_lab_reports(
        labs,
        valid_patient_ids,
    )


def test_lab_results_are_numeric():

    clean = get_clean_labs()

    assert pd.api.types.is_numeric_dtype(
        clean["result_value"]
    )


def test_missing_lab_results_are_removed():

    clean = get_clean_labs()

    assert clean[
        "result_value"
    ].notna().all()


def test_lab_dates_are_datetime():

    clean = get_clean_labs()

    assert pd.api.types.is_datetime64_any_dtype(
        clean["report_date"]
    )


def test_reference_ranges_are_created():

    clean = get_clean_labs()

    assert "ref_low" in clean.columns
    assert "ref_high" in clean.columns

    assert clean[
        "ref_low"
    ].notna().all()

    assert clean[
        "ref_high"
    ].notna().all()


def test_result_status_is_valid():

    clean = get_clean_labs()

    valid_statuses = {
        "Low",
        "Normal",
        "High",
    }

    assert set(
        clean[
            "result_status"
        ].unique()
    ).issubset(
        valid_statuses
    )


def test_abnormal_flag_is_correct():

    clean = get_clean_labs()

    expected = (
        clean["result_status"] != "Normal"
    ).astype(int)

    pd.testing.assert_series_equal(
        clean[
            "is_abnormal"
        ].reset_index(drop=True),
        expected.reset_index(drop=True),
        check_names=False,
    )


def test_lab_patient_ids_are_valid():

    patients = extract_patients()
    clean = get_clean_labs()

    valid_patient_ids = set(
        patients["patient_id"]
    )

    assert clean[
        "patient_id"
    ].isin(
        valid_patient_ids
    ).all()


def test_lab_transformation_keeps_records():

    clean = get_clean_labs()

    assert len(clean) > 0