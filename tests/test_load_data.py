import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from src.dashboard import load_data  

@pytest.fixture
def sample_df():
    data = {
        "INCIDENT_NUMBER": ["I1", "I2", "I3"],
        "OFFENSE_CODE": [101, 102, 103],
        "OFFENSE_CODE_GROUP": ["Robbery", "Assault", "Other"],
        "OFFENSE_DESCRIPTION": ["Robbery Description", "Assault Description", "Other Description"],
        "DISTRICT": ["A1", "", "C11"],           # eine leere → soll droppen
        "REPORTING_AREA": [101, 802, 120],
        "SHOOTING": ["Y", "N", ""],
        "OCCURRED_ON_DATE": ["2025-01-15 14:30", "2025-02-03 09:15", "2025-03-10 23:45"],
        "YEAR": [2025, 2025, 2025],
        "MONTH": [1, 2, 3],
        "DAY_OF_WEEK": ["Monday", "Tuesday", "Wednesday"],
        "HOUR": [14, 9, 23],
        "UCR_PART": ["Part One", "Part Two", ""],  # eine leere → droppen
        "STREET": ["Main St", "2nd Ave", "3rd Blvd"],
        "Lat": [42.3, -1.0, 42.35],
        "Long": [-71.1, -1.0, -71.05],
        "Location": ["(42.3, -71.1)", "(NaN, NaN)", "(42.35, -71.05)"]
    }
    return pd.DataFrame(data)


def test_load_data_normal_case(tmp_path, sample_df):
    csv_path = tmp_path / "test.csv"
    sample_df.to_csv(csv_path, index=False)

    with open(csv_path, "rb") as f:
        result = load_data(f)

    assert result is not None
    assert len(result) == 1               # nur 1 Zeile bleibt nach dropna
    assert result["DISTRICT"].iloc[0] == "A1"
    assert pd.api.types.is_datetime64_any_dtype(result["OCCURRED_ON_DATE"])
    assert result["Lat"].isna().sum() == 0   # -1 → NaN → drop


def test_load_data_missing_file():
    assert load_data(None) is None


def test_load_data_invalid_types(tmp_path):
    df = pd.DataFrame({
        "INCIDENT_NUMBER": [123],           # sollte str werden
        "OFFENSE_CODE": ["abc"],            # sollte int werden → Fehler?
        "DISTRICT": ["D4"],
    })
    path = tmp_path / "bad.csv"
    df.to_csv(path, index=False)

    with pytest.raises((ValueError, TypeError)):   # je nach pd.read_csv Verhalten
        load_data(open(path, "rb"))