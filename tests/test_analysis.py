import pytest
import pandas as pd
from src.analysis import parse_geometry, get_epoch

# --- Tests for Geometry Parsing ---

def test_parse_geometry_csv_string():
    """Test standard CSV format (WKT String)."""
    input_str = "POINT (2683000.5 1248000.1)"
    expected = (2683000.5, 1248000.1)
    assert parse_geometry(input_str) == expected

def test_parse_geometry_geojson_list():
    """Test GeoJSON format (List of floats)."""
    input_list = [2683000.5, 1248000.1]
    expected = (2683000.5, 1248000.1)
    assert parse_geometry(input_list) == expected

def test_parse_geometry_invalid():
    """Test edge cases and invalid inputs."""
    assert parse_geometry(None) == (None, None)
    assert parse_geometry([]) == (None, None)       # Empty list
    assert parse_geometry("Invalid") == (None, None) # Bad string
    assert parse_geometry([123]) == (None, None)    # Incomplete list

# --- Tests for Epoch Categorization ---

def test_get_epoch_categories():
    """Test correct categorization of years."""
    assert get_epoch(1950) == "Heritage (< 1960)"
    assert get_epoch(1975) == "Expansion (1960-1990)"
    assert get_epoch(2000) == "Modern (> 1990)"

def test_get_epoch_edge_cases():
    """Test boundary years and invalid input."""
    assert get_epoch(1960) == "Expansion (1960-1990)" # Boundary check
    assert get_epoch(1990) == "Modern (> 1990)"       # Boundary check
    assert get_epoch(pd.NA) == "Unknown"
    assert get_epoch("Not a number") == "Unknown"
