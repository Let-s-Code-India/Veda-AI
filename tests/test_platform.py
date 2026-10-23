import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import core


def test_platform_kind_handles_ipad_android_and_ish():
    assert core.platform_kind("Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)") == "ios"
    assert core.platform_kind("Mozilla/5.0 (Linux; Android 14; Pixel 8)") == "android"
    assert core.platform_kind("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) ish/1.0") == "ios"
    assert core.platform_kind("Mozilla/5.0 (X11; Linux x86_64)") == "linux"


def test_safe_url_blocks_private_and_local_addresses():
    assert core.safe_url("http://localhost:5000") is False
    assert core.safe_url("http://127.0.0.1:5000") is False
    assert core.safe_url("http://10.0.0.5") is False
    assert core.safe_url("https://example.com") is True
