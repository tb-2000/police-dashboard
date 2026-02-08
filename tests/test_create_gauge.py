import pytest
from src.dashboard import create_gauge
import plotly.graph_objects as go


@pytest.mark.parametrize("value,title,color", [
    (42, "Test", "blue"),
    (0, "Empty", "gray"),
    (150, "Big", "red"),
])
def test_create_gauge_structure(value, title, color):
    fig = create_gauge(value, title, color)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].mode == "gauge+number"
    assert fig.data[0].value == value
    assert fig.data[0].title.text == title  