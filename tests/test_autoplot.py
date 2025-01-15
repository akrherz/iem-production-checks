"""Attempt to call each autoplot and whine about API calls that error"""

import os

import httpx
import pytest

SERVICE = os.environ.get("SERVICE", "https://mesonet.agron.iastate.edu")


def get_formats(i):
    """Figure out which formats this script supports"""
    uri = f"{SERVICE}/plotting/auto/meta/{i}.json"
    res = None
    try:
        res = httpx.get(uri, timeout=20)
    except httpx.ReadTimeout:
        print(f"{i}. {uri[16:]} -> Read Timeout")
    if res is None:
        raise ValueError("Failed to fetch metadata, BUG.")
    if res.status_code == 404:
        print(f"scanning metadata got 404 at i={i}, proceeding")
        return False
    if res.status_code != 200:
        print(f"{i}. {uri} -> HTTP: {res.status_code}")
        print(res.text)
    try:
        json = res.json()
    except Exception as exp:
        print(f"{i} {res.content} -> json failed\n{exp}")
        return []
    fmts = [
        "png",
    ]
    if "report" in json and json["report"]:
        fmts.append("txt")
    if "highcharts" in json and json["highcharts"]:
        fmts.append("js")
    if "mapbox" in json and json["mapbox"]:
        fmts.append("mapbox")
    if json.get("data", False):
        fmts.append("csv")
        fmts.append("xlsx")
    return fmts


def get_all():
    """Figure out what we need to run for."""
    url = f"{SERVICE}/plotting/auto/meta/0.json"
    j = httpx.get(url, timeout=60).json()
    queue = []
    for lbl in j["plots"]:
        for opt in lbl["options"]:
            queue.append(opt["id"])
    return queue


@pytest.mark.parametrize("opts", get_all())
def test_autoplot(opts):
    """Run this plot"""
    i = opts
    # The 600 timeout may seem lax, but in Github Actions, I have found some
    # stales whereby a lower timeout leads to false positives
    res = httpx.get(f"{SERVICE}/plotting/auto/?q={i}", timeout=600)
    assert res.status_code == 200
    for fmt in get_formats(i):
        uri = f"{SERVICE}/plotting/auto/plot/{i}/dpi:100::_cb:1.{fmt}"
        res = httpx.get(uri, timeout=600)
        print(
            f"i: {i} fmt: {fmt} status_code: {res.status_code} "
            f"len(response): {len(res.content)} uri: {uri}"
        )
        # Flakey website emits a flakey 500 sometimes due to known unknowns
        # just retry it once and see what happens.
        if res.status_code == 500:
            res = httpx.get(uri, timeout=600)
            print(
                f"i: {i} fmt: {fmt} status_code: {res.status_code} "
                f"len(response): {len(res.content)} uri: {uri}"
            )

        # Known failures likely due to missing data
        assert res.status_code in [200, 400]
        assert res.content != ""
