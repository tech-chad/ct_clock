import datetime
import types
import contextlib

import pytest
from time import sleep

import time_machine
from hecate import Runner

import ct_clock


@contextlib.contextmanager
def my_time_context_manager(*args, **kwargs):
    r = ct_clock.MyTime(*args, **kwargs)
    try:
        yield r
    finally:
        r.reset_time()


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


def test_my_time_class_no_test():
    with my_time_context_manager(False) as test_class:
        assert test_class.test_mode is False
        assert test_class.test_time == ""
        assert test_class.tick is True
        assert test_class.time is None


def test_my_time_class_test_mode_tick():
    with my_time_context_manager(True, "02:02:02") as test_class:
        assert test_class.test_mode is True
        assert test_class.test_time == "02:02:02"
        assert test_class.tick is True
        assert isinstance(test_class.time, types.GeneratorType)


def test_my_time_class_test_mode_no_tick():
    with my_time_context_manager(True, "02:02:02", False) as test_class:
        assert test_class.test_mode is True
        assert test_class.test_time == "02:02:02"
        assert test_class.tick is False
        assert isinstance(test_class.time, types.GeneratorType)


@pytest.mark.parametrize("test_time, test_format, expected", [
    ("2:00:00", "%H%M%S", "020000"), ("14:00:00", "%H%M%S", "140000"),
    ("2:00:00", "%I%M%S", "020000"), ("14:00:00", "%I%M%S", "020000"),
    ("2:00:00", "%p", "AM"), ("14:00:00", "%p", "PM")
])
def test_my_time_get_time_no_test(test_time, test_format, expected):
    with time_machine.travel(test_time):
        t = ct_clock.MyTime(False)
        result = t.get_time(test_format)
        assert result == expected


def test_my_time_get_time_test_mode_tick_on():
    with my_time_context_manager(True, "02:00:00", True) as t:
        assert t.get_time("%I%M%S") == "020000"
        sleep(1)
        assert t.get_time("%I%M%S") == "020001"
        sleep(1)
        assert t.get_time("%I%M%S") == "020002"


def test_my_time_get_time_test_mode_military_time_tick_on():
    with my_time_context_manager(True, "16:00:00", True) as t:
        assert t.get_time("%H%M%S") == "160000"
        sleep(1)
        assert t.get_time("%H%M%S") == "160001"
        sleep(1)
        assert t.get_time("%H%M%S") == "160002"


def test_my_time_get_time_test_mode_switch_military_time_tick_on():
    with my_time_context_manager(True, "16:00:00", True) as t:
        assert t.get_time("%H%M%S") == "160000"
        sleep(1)
        assert t.get_time("%I%M%S") == "040001"
        sleep(1)
        assert t.get_time("%H%M%S") == "160002"
        sleep(1)
        assert t.get_time("%I%M%S") == "040003"


def test_my_time_get_time_test_mode_tick_off():
    with my_time_context_manager(True, "02:00:00", False) as t:
        assert t.get_time("%I%M%S") == "020000"
        sleep(1)
        assert t.get_time("%I%M%S") == "020000"
        sleep(1)
        assert t.get_time("%I%M%S") == "020000"


def test_my_time_get_time_test_mode_reset_time():
    with pytest.raises(StopIteration):
        with my_time_context_manager(True, "16:00:00", True) as t:
            assert t.get_time("%I%M%S") == "040000"
            sleep(1)
            assert t.get_time("%I%M%S") == "040001"
            sleep(1)
            t.reset_time()
            a = t.get_time("%I%M%S") == "013002"


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


def test_ct_clock_digits():
    with Runner(*ct_clock_run()) as h:
        h.await_text("M")
        sc = h.screenshot()
        assert "1" in sc
        assert "2" in sc
        assert "3" in sc
        assert "4" in sc
        assert "5" in sc
        assert "6" in sc


def test_ct_clock_no_seconds():
    with Runner(*ct_clock_run("--no_seconds")) as h:
        h.default_timeout = 2
        h.await_text("M")
        sc = h.screenshot()
        assert "5" not in sc
        assert "6" not in sc
        h.write("s")
        h.press("Enter")
        h.await_text("5")
        h.await_text("6")
        h.write("s")
        h.press("Enter")
        sleep(1)
        sc = h.screenshot()
        assert "5" not in sc
        assert "6" not in sc


def test_ct_clock_testing_test_mode():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "10:10:10")) as h:
        h.await_text("test mode")


def test_ct_clock_testing_test_mode_time():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "12:34:56")) as h:
        h.await_text("test mode")
        sc = h.screenshot()
        assert "1" in sc
        assert "2" in sc
        assert "3" in sc
        assert "4" in sc
        assert "5" in sc
        assert "6" in sc
        assert "7" not in sc
        assert "8" not in sc
        assert "9" not in sc
        assert "0" not in sc


def test_help_test_mode_test_time_suppressed():
    with Runner(*ct_clock_run("--help")) as h:
        h.await_text("usage")
        sc = h.screenshot()
        assert "test_mode" not in sc
        assert "test_time" not in sc
