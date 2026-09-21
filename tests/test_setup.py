import os

from config import (
    BASE_DIR,
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    REPORTS_DIR,
    LOG_DIR,
)


def test_project_directories_exist():
    assert os.path.isdir(BASE_DIR)
    assert os.path.isdir(DATA_DIR)
    assert os.path.isdir(RAW_DIR)
    assert os.path.isdir(PROCESSED_DIR)
    assert os.path.isdir(REPORTS_DIR)
    assert os.path.isdir(LOG_DIR)