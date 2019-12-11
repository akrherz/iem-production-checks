"""Run Tests."""

import requests
import pytest
from bs4 import BeautifulSoup


def get_jsonlinks():
    """Figure out what we need to run for."""
    content = requests.get("https://mesonet.agron.iastate.edu/json/").content
    soup = BeautifulSoup(content, 'lxml')
    queue = []
    for tag in soup.find_all('a'):
        if tag.text != 'Example JSON':
            continue
        queue.append(tag.attrs['href'])
    return queue


@pytest.mark.parametrize("opts", get_jsonlinks())
def test_json_documentation_page_links(opts):
    """Test example URLs shown on the /json/ page."""
    res = requests.get(opts, timeout=60)
    assert res.status_code == 200
    assert res.json()


def test_urls():
    """Test that we can download stuff."""
    req = requests.get("https://mesonet.agron.iastate.edu")
    assert req.status_code == 200
