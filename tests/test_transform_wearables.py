import pandas as pd

from src.extract import extract_wearables
from src.transform import transform_wearables


def get_clean_wearables():

    raw = extract_wearables()

    return transform_wearables(
        raw
    )


def test_duplicate_readings_are_removed():

    clean = get_clean_wearables()

    assert not clean.duplicated(
        [
            "device_id",
            "reading_time",
        ]
    ).any()


def test_reading_time_is_datetime():

    clean = get_clean_wearables()

    assert pd.api.types.is_datetime64_any_dtype(
        clean["reading_time"]
    )


def test_vital_columns_are_numeric():

    clean = get_clean_wearables()

    for column in [
        "heart_rate",
        "spo2",
        "body_temp",
    ]:

        assert pd.api.types.is_numeric_dtype(
            clean[column]
        )


def test_no_physically_invalid_heart_rates():

    clean = get_clean_wearables()

    assert clean[
        "heart_rate"
    ].between(
        30,
        220,
    ).all()


def test_no_physically_invalid_spo2():

    clean = get_clean_wearables()

    assert clean[
        "spo2"
    ].between(
        50,
        100,
    ).all()


def test_no_physically_invalid_temperature():

    clean = get_clean_wearables()

    assert clean[
        "body_temp"
    ].between(
        34.0,
        43.0,
    ).all()


def test_missing_vitals_are_removed():

    clean = get_clean_wearables()

    assert clean[
        [
            "heart_rate",
            "spo2",
            "body_temp",
        ]
    ].notna().all().all()


def test_abnormal_flags_are_created():

    clean = get_clean_wearables()

    expected_columns = {
        "heart_rate_abnormal",
        "spo2_abnormal",
        "body_temp_abnormal",
        "is_abnormal",
    }

    assert expected_columns.issubset(
        clean.columns
    )


def test_abnormal_flag_values_are_binary():

    clean = get_clean_wearables()

    for column in [
        "heart_rate_abnormal",
        "spo2_abnormal",
        "body_temp_abnormal",
        "is_abnormal",
    ]:

        assert set(
            clean[column].unique()
        ).issubset(
            {0, 1}
        )


def test_overall_abnormal_flag_is_correct():

    clean = get_clean_wearables()

    expected = (
        (
            clean["heart_rate_abnormal"]
            == 1
        )
        |
        (
            clean["spo2_abnormal"]
            == 1
        )
        |
        (
            clean["body_temp_abnormal"]
            == 1
        )
    ).astype(int)

    pd.testing.assert_series_equal(
        clean[
            "is_abnormal"
        ].reset_index(drop=True),
        expected.reset_index(drop=True),
        check_names=False,
    )


def test_transformation_removes_bad_source_rows():

    raw = extract_wearables()

    clean = get_clean_wearables()

    assert len(clean) < len(raw)