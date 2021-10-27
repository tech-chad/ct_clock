import pytest
from time import sleep

from hecate import Runner

import ct_clock


def ct_clock_run(*args):
    options = [a for a in args]
    return ["python3", "ct_clock.py"] + options


@pytest.mark.parametrize("test_value, expected", [
    ("small", 5), ("medium", 6), ("large", 14),
])
def test_get_offset(test_value, expected):
    result = ct_clock.get_offset(test_value)
    assert result == expected


@pytest.mark.parametrize("test_size, test_show, expected", [
    ("small", False, (5, 20)), ("small", True, (5, 30)),
    ("medium", False, (7, 24)), ("medium", True, (7, 36)),
    ("large", False, (18, 56)), ("large", True, (18, 84)),
])
def test_get_space_size(test_size, test_show, expected):
    result = ct_clock.get_space_size(test_size, test_show)
    assert result == expected


@pytest.mark.parametrize("test_number, test_size, expected", [
    ("2", "small", ((0, 0), (0, 1), (0, 2), (0, 2), (1, 2),
                    (2, 2), (2, 0), (2, 1), (2, 2), (2, 0), (3, 0), (4, 0),
                    (4, 0), (4, 1), (4, 2))),
    (":", "small", ((1, 4), (3, 4))),
    ("1", "medium", ((0, 3), (1, 3), (2, 3), (3, 3), (3, 3), (4, 3), (5, 3), (6, 3))),
    (":", "large", ((5, 12), (12, 12))),
])
def test_get_segments(test_number, test_size, expected):
    result = ct_clock.get_segments(test_number, test_size)
    assert result == expected


@pytest.mark.parametrize("test_key", ["Q", "q"])
def test_ct_clock_quit(test_key):
    with Runner(*ct_clock_run(), width=120, height=50) as h:
        h.await_text("M")
        h.write(test_key)
        h.press("Enter")
        h.await_exit()


def test_ct_clock_am_pm_normal_time():
    with Runner(*ct_clock_run()) as h:
        h.await_text("M")


@pytest.mark.parametrize("test_key", ["u", "d", "c", "m", "p", "2", "0", " ", "]"])
def test_ct_clock_screensaver_mode(test_key):
    with Runner(*ct_clock_run("-S")) as h:
        h.await_text("M")
        h.write(test_key)
        h.press("Enter")
        h.await_exit()


def test_ct_clock_cli_show_date():
    with Runner(*ct_clock_run("--show_date")) as h:
        h.await_text("M")
        h.await_text("/")


def test_ct_clock_cli_military_time():
    with Runner(*ct_clock_run("-m"), width=100, height=50) as h:
        h.default_timeout = 2
        sleep(1)
        sc = h.screenshot()
        assert "M" not in sc


def test_ct_clock_running_show_date():
    with Runner(*ct_clock_run()) as h:
        h.default_timeout = 2
        h.await_text("M")
        sc = h.screenshot()
        assert "/" not in sc
        h.write("e")
        h.press("Enter")
        h.await_text("/")
        h.write("e")
        h.press("Enter")
        sleep(1)
        h.await_text("M")
        sc = h.screenshot()
        assert "/" not in sc


def test_ct_clock_running_military_time():
    with Runner(*ct_clock_run()) as h:
        h.default_timeout = 2
        h.await_text("M")
        h.write("m")
        h.press("Enter")
        h.await_text(" ")
        sleep(1)
        sc = h.screenshot()
        assert "M" not in sc
        h.write("m")
        h.press("Enter")
        h.await_text("M")
