"""Run Tests."""
import os

import pytest
import requests
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
        href = tag.attrs["href"]
        if href.startswith("http") and href.find("/api/") < 0:
            queue.append(tag.attrs["href"])
    return queue


@pytest.mark.parametrize("opts", get_jsonlinks())
def test_json_documentation_page_links(opts):
    """Test example URLs shown on the /json/ page."""
    if opts.startswith("/"):
        opts = f"{SERVICE}{opts}"
    res = requests.get(opts, timeout=60)
    assert res.status_code == 200
    res.json()


# Load a list of uris provided by a local uris.txt file and test them
# against the SERVICE
def get_uris():
    """Figure out what we need to run for."""
    # Locate the uris.txt file relative to the tests directory
    dirname = os.path.dirname(__file__)
    with open(f"{dirname}/uris.txt", encoding="ascii") as fh:
        for line in fh.readlines():
            if line.startswith("#"):
                continue
            yield line.strip()


@pytest.mark.parametrize("uri", get_uris())
def test_uri(uri):
    """Test a URI."""
    # We can't test API server on localhost, so skip those
    if uri.startswith("/api/") and SERVICE.find("iem.local") > 0:
        return
    res = requests.get(f"{SERVICE}{uri}", timeout=60)
    # HTTP 400 should be known failures being gracefully handled
    assert res.status_code in [200, 400]
