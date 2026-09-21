import json
from pathlib import Path

from config import SOURCE_FILES


def test_lab_dataset_exists():
    path = Path(
        SOURCE_FILES["lab_reports"]
    )

    assert path.exists()


def test_lab_dataset_is_valid_json():

    with open(
        SOURCE_FILES["lab_reports"],
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    assert isinstance(
        data,
        dict,
    )


def test_lab_dataset_has_reports():

    with open(
        SOURCE_FILES["lab_reports"],
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    assert "reports" in data

    assert isinstance(
        data["reports"],
        list,
    )

    assert len(
        data["reports"]
    ) > 0


def test_lab_reports_have_required_fields():

    with open(
        SOURCE_FILES["lab_reports"],
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    required_fields = {
        "report_id",
        "patient_id",
        "test_name",
        "result_value",
        "unit",
        "report_date",
    }

    for report in data["reports"]:

        assert required_fields.issubset(
            report.keys()
        )


def test_lab_data_contains_missing_or_string_values():

    with open(
        SOURCE_FILES["lab_reports"],
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    reports = data["reports"]

    has_missing = any(
        report["result_value"] is None
        for report in reports
    )

    has_string_value = any(
        isinstance(
            report["result_value"],
            str,
        )
        for report in reports
    )

    assert has_missing or has_string_value