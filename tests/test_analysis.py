import pytest
from src.analysis import parse_geometry, get_epoch

# Test 1: Funktioniert das Parsen der Koordinaten?
def test_parse_geometry_valid():
    input_str = "POINT (2600.5 1200.1)"
    x, y = parse_geometry(input_str)
    assert x == 2600.5
    assert y == 1200.1

# Test 2: Was passiert bei Müll-Daten?
def test_parse_geometry_invalid():
    assert parse_geometry("KEIN PUNKT")[0] is None
    assert parse_geometry(None)[0] is None

# Test 3: Stimmen die Epochen?
def test_get_epoch():
    assert get_epoch(1950) == "Altbestand (< 1960)"
    assert get_epoch(2020) == "Modern (> 1990)"
