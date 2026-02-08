import pandas as pd
import pytest
from src.dashboard import load_data  # falls nötig

@pytest.fixture
def filtered_df_example():
    data = {
        "UCR_PART": ["Part One", "Part Two", "Part One", "Part Three"],
        "SHOOTING": ["Y", "N", "Y", "N"],
        "DISTRICT": ["A1", "B2", "A1", "C11"],
        "OCCURRED_ON_DATE": pd.date_range("2025-01-01", periods=4),
    }
    return pd.DataFrame(data)


def test_metrics_calculation(filtered_df_example):
    df = filtered_df_example

    total = len(df)
    part_one = len(df[df["UCR_PART"] == "Part One"])
    shootings = len(df[df["SHOOTING"] == "Y"])

    assert total == 4
    assert part_one == 2
    assert shootings == 2


def test_date_filter_behavior():
    df = pd.DataFrame({
        "OCCURRED_ON_DATE": pd.to_datetime(["2025-01-05", "2025-02-10", "2025-03-20"])
    })
    start = pd.to_datetime("2025-02-01")
    end   = pd.to_datetime("2025-02-28")

    filtered = df[(df["OCCURRED_ON_DATE"] >= start) & (df["OCCURRED_ON_DATE"] <= end)]
    assert len(filtered) == 1