"""Run Tests."""
import os

import requests
import pytest
from bs4 import BeautifulSoup

SERVICE = os.environ.get("SERVICE", "https://mesonet.agron.iastate.edu")


def get_jsonlinks():
    """Figure out what we need to run for."""
    content = requests.get(f"{SERVICE}/json/", timeout=60).content
    soup = BeautifulSoup(content, "lxml")
    queue = []
    for tag in soup.find_all("a"):
        if tag.text != "Example JSON":
            continue
        queue.append(tag.attrs["href"])
    return queue


@pytest.mark.parametrize("opts", get_jsonlinks())
def test_json_documentation_page_links(opts):
    """Test example URLs shown on the /json/ page."""
    res = requests.get(opts, timeout=60)
    assert res.status_code == 200
    assert res.json()


def test_urls():
    """Test that we can download stuff."""
    req = requests.get(SERVICE, timeout=60)
    assert req.status_code == 200
