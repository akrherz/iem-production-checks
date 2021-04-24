"""Attempt to call each autoplot and whine about API calls that error"""
import os

import pytest
import requests

SERVICE = os.environ.get("SERVICE", "https://mesonet.agron.iastate.edu")


def get_formats(i):
    """Figure out which formats this script supports"""
    uri = "%s/plotting/auto/meta/%s.json" % (SERVICE, i)
    res = None
    try:
        res = requests.get(uri, timeout=20)
    except requests.exceptions.ReadTimeout:
        print("%s. %s -> Read Timeout" % (i, uri[16:]))
    if res is None:
        raise ValueError("Failed to fetch metadata, BUG.")
    if res.status_code == 404:
        print("scanning metadata got 404 at i=%s, proceeding" % (i, ))
        return False
    if res.status_code != 200:
        print("%s. %s -> HTTP: %s" % (i, uri, res.status_code))
        print(res.text)
    try:
        json = res.json()
    except Exception as exp:
        print("%s %s -> json failed\n%s" % (i, res.content, exp))
        return []
    fmts = ['png', ]
    if 'report' in json and json['report']:
        fmts.append('txt')
    if 'highcharts' in json and json['highcharts']:
        fmts.append('js')
    if 'mapbox' in json and json['mapbox']:
        fmts.append('mapbox')
    if json.get('data', False):
        fmts.append('csv')
        fmts.append('xlsx')
    return fmts


def get_all():
    """Figure out what we need to run for."""
    url = "%s/plotting/auto/meta/0.json" % (SERVICE, )
    j = requests.get(url).json()
    queue = []
    for lbl in j['plots']:
        for opt in lbl['options']:
            queue.append(opt['id'])
    return queue


@pytest.mark.parametrize("opts", get_all())
def test_autoplot(opts):
    """Run this plot"""
    i = opts
    res = requests.get(f"{SERVICE}/plotting/auto/?q={i}", timeout=20)
    assert res.status_code == 200
    for fmt in get_formats(i):
        uri = "%s/plotting/auto/plot/%s/dpi:100::_cb:1.%s" % (SERVICE, i, fmt)
        res = requests.get(uri, timeout=600)
        print(
            "i: %s fmt: %s status_code: %s len(response): %s uri: %s" % (
                i, fmt, res.status_code, len(res.content), uri))
        # Flakey website emits a flakey 500 sometimes due to known unknowns
        # just retry it once and see what happens.
        if res.status_code == 500:
            res = requests.get(uri, timeout=600)
            print(
                "i: %s fmt: %s status_code: %s len(response): %s uri: %s" % (
                    i, fmt, res.status_code, len(res.content), uri))

        # Known failures likely due to missing data
        assert res.status_code in [200, 400]
        assert res.content != ""
