"""Run Tests."""

import requests


def test_urls():
    """Test that we can download stuff."""
    req = requests.get("https://mesonet.agron.iastate.edu")
    assert req.status_code == 200
