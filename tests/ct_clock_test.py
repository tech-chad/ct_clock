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
            assert t.get_time("%I%M%S") == "013002"


def test_my_time_test_date():
    with my_time_context_manager(True, "1970-1-2 07:00:00") as t:
        assert t.get_date("%d/%m/%Y") == "02/01/1970"


def test_my_time_date_no_test():
    with time_machine.travel("1980-8-21 11:00:00"):
        t = ct_clock.MyTime(False)
        assert t.get_date("%d/%m/%Y") == "21/08/1980"


@pytest.mark.parametrize("test_key", ["Q", "q"])
def test_ct_clock_quit(test_key):
    with Runner(*ct_clock_run("--test_mode"), width=50, height=50) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.write(test_key)
        h.press("Enter")
        h.await_exit()


def test_ct_clock_am_pm_normal_time():
    # Test can be flaky
    with Runner(*ct_clock_run()) as h:
        h.await_text("M", timeout=2)


@pytest.mark.parametrize("test_key", ["u", "d", "c", "m", "p", "2", "0", " ", "]"])
def test_ct_clock_screensaver_mode(test_key):
    # Test can be flaky
    with Runner(*ct_clock_run("-S")) as h:
        h.await_text("M", timeout=2)
        h.write(test_key)
        h.press("Enter")
        h.await_exit()


def test_ct_clock_cli_show_date():
    with Runner(*ct_clock_run("--show_date")) as h:
        h.default_timeout = 2
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


def test_ct_clock_digits_military():
    with Runner(*ct_clock_run("-m")) as h:
        h.default_timeout = 1
        h.await_text("1", timeout=2)
        sc = h.screenshot()
        assert "1" in sc
        assert "2" in sc
        assert "3" in sc
        assert "4" in sc
        assert "5" in sc
        assert "6" in sc


def test_ct_clock_digits_normal():
    with Runner(*ct_clock_run()) as h:
        h.default_timeout = 1
        h.await_text("M", timeout=2)
        sc = h.screenshot()
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
        h.await_text("test mode", timeout=2)


def test_ct_clock_testing_test_mode_default_time():
    with Runner(*ct_clock_run("--test_mode")) as h:
        h.await_text("test mode", timeout=2)
        h.await_text("0", timeout=2)


def test_ct_clock_testing_test_mode_time():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "12:34:56")) as h:
        # h.default_timeout = 2
        h.await_text("test mode", timeout=3)
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


def test_ct_clock_testing_test_mode_date():
    with Runner(*ct_clock_run("--show_date",
                              "--test_mode",
                              "--test_date",
                              "1980-1-2")) as h:
        h.await_text("test mode", timeout=3)
        h.await_text("02/01/1980")


def test_help_test_mode_test_time_suppressed():
    with Runner(*ct_clock_run("--help")) as h:
        h.await_text("usage", timeout=2)
        sc = h.screenshot()
        assert "test_mode" not in sc
        assert "test_time" not in sc


def test_ct_clock_cli_military_time_time():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "14:00:00", "-m")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.await_text("4")
        h.await_text("1")
        sc = h.screenshot()
        assert "2" not in sc


def test_ct_clock_running_military_time_time():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "14:00:00")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.await_text("2")
        sc = h.screenshot()
        assert "4" not in sc
        assert "1" not in sc
        h.write("m")
        h.press("Enter")
        h.await_text("4")
        h.await_text("1")
        sc = h.screenshot()
        assert "2" not in sc
        h.write("m")
        h.press("Enter")
        h.await_text("2")
        sc = h.screenshot()
        assert "4" not in sc
        assert "1" not in sc


def test_ct_clock_running_military_time_time_am():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "02:00:05")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.await_text("2")
        sc = h.screenshot()
        assert "4" not in sc
        assert "1" not in sc
        h.write("m")
        h.press("Enter")
        h.await_text("2")
        sc = h.screenshot()
        assert "4" not in sc
        assert "1" not in sc
        h.write("m")
        h.press("Enter")
        h.await_text("2")
        sc = h.screenshot()
        assert "4" not in sc
        assert "1" not in sc


def test_ct_clock_colon_on_screen():
    with Runner(*ct_clock_run()) as h:
        h.default_timeout = 2
        h.await_text(":")


def test_ct_clock_colon_blinking():
    with Runner(*ct_clock_run("-b")) as h:
        h.default_timeout = 2
        h.await_text(":")
        sleep(1)
        sc = h.screenshot()
        assert ":" not in sc
        sleep(1)
        h.await_text(":")
        h.write("b")
        h.press("Enter")
        h.await_text(":")
        sleep(1)
        h.await_text(":")


def test_ct_clock_color_default():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "14:00:00")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.await_text("white")


@pytest.mark.parametrize("color", [
    "white", "blue", "green", "red", "yellow", "cyan", "magenta"
])
def test_ct_clock_color_cli(color):
    # Test can be flaky.
    with Runner(*ct_clock_run("--test_mode", "-c", color)) as h:
        h.default_timeout = 2
        h.await_text("test mode", timeout=3)
        h.await_text(color)


@pytest.mark.parametrize("command, color", [
    ("r", "red"), ("t", "green"), ("y", "blue"), ("u", "yellow"),
    ("i", "magenta"), ("o", "cyan"), ("p", "white")
])
def test_ct_clock_color_running(command, color):
    # Test could be flaky.
    with Runner(*ct_clock_run("--test_mode")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.write(command)
        h.press("Enter")
        h.await_text(color)


def test_ct_clock_cycle_color_every_sec():
    # test can be flaky
    with Runner(*ct_clock_run("--test_mode", "--mode", "1", "--cycle_timing", "1")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.await_text("green")
        sleep(1)
        h.await_text("blue")
        sleep(1)
        h.await_text("yellow")


def test_ct_clock_cycle_color_every_min():
    with Runner(*ct_clock_run("--test_mode", "--mode", "1",
                              "--cycle_timing", "2", "--test_time", "01:01:59")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.await_text("red")
        h.await_text("green", timeout=2)


def test_ct_clock_cycle_color_top_hour():
    with Runner(*ct_clock_run("--test_mode", "--mode", "1",
                              "--cycle_timing", "3", "--test_time", "01:59:59")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        h.await_text("red")
        h.await_text("green")


def test_ct_clock_cycle_color_timing_change_min_sec():
    # this test can be flaky
    with Runner(*ct_clock_run("--test_mode", "--mode", "1",
                              "--cycle_timing", "2", "--test_time", "07:02:57")) as h:
        h.default_timeout = 3
        h.await_text("test mode")
        h.await_text("red")
        sleep(2)
        h.await_text("red")
        h.await_text("green")
        sc = h.screenshot()
        assert "3" in sc
        assert "5" not in sc
        assert "9" not in sc
        h.write("1")
        h.press("Enter")
        h.default_timeout = 1
        h.await_text("blue")
        sc = h.screenshot()
        assert "1" in sc


def test_ct_clock_screen_resize_width_running():
    with Runner(*ct_clock_run("--test_mode"), width=100, height=100) as h:
        h.default_timeout = 3
        h.await_text("test mode")
        h.tmux.execute_command('split-window', '-ht0', '-l', 30)
        h.await_text("test mode")
        h.tmux.execute_command('resize-pane', '-L', 30)
        h.await_text("test mode")


def test_ct_clock_screen_resize_height_running():
    with Runner(*ct_clock_run("--test_mode"), width=100, height=60) as h:
        h.default_timeout = 3
        h.await_text("test mode")
        h.tmux.execute_command('split-window', '-vt0', '-l', 45)
        h.await_text("test mode")
        h.tmux.execute_command('resize-pane', '-U', 6)
        h.await_text("test mode")


@pytest.mark.parametrize("size_width, size_height, expected", [
    (100, 100, "test mode"), (50, 100, "test mode"), (37, 100, "test mode"),
    (36, 100, "test mode"), (100, 50, "test mode"), (100, 9, "test mode"),
    (100, 8, "test mode"),
])
def test_ct_clock_screen_start_size(size_width, size_height, expected):
    with Runner(*ct_clock_run("--test_mode"), width=size_width, height=size_height) as h:
        h.await_text(expected, timeout=3)


@pytest.mark.parametrize("size_width, size_height, expected", [
    (35, 100, "Error screen"),
    (100, 7, "Error screen / window is to small"),
    (35, 7, "Error screen")
])
def test_ct_clock_screen_start_size_to_small(size_width, size_height, expected):
    with Runner("bash", width=size_width, height=size_height) as h:
        h.default_timeout = 2
        h.await_text("$")
        h.write("python3 ct_clock.py --test_mode")
        h.press("Enter")
        h.await_text(expected, timeout=3)


def test_ct_clock_screen_resize_to_small_width():
    with Runner("bash", width=100, height=60) as h:
        h.default_timeout = 2
        h.await_text("$")
        h.write("python3 ct_clock.py --test_mode")
        h.press("Enter")
        h.await_text("test mode")
        h.tmux.execute_command('split-window', '-vt0', '-l', 45)
        h.await_text("test mode")
        h.tmux.execute_command('resize-pane', '-U', 7)
        h.await_text("Error screen / window is to small")


def test_ct_clock_screen_resize_to_small_height():
    with Runner("bash", width=100, height=60) as h:
        h.default_timeout = 2
        h.await_text("$")
        h.write("python3 ct_clock.py --test_mode")
        h.press("Enter")
        h.await_text("test mode")
        h.tmux.execute_command('split-window', '-ht0', '-l', 30)
        h.await_text("test mode")
        h.tmux.execute_command('resize-pane', '-L', 38)
        h.await_text("Error screen")


def test_ct_clock_handle_ctrl_c():
    with Runner("bash", width=100, height=60) as h:
        h.default_timeout = 2
        h.await_text("$")
        h.write("python3 ct_clock.py --test_mode")
        h.press("Enter")
        h.await_text("test mode")
        h.press("C-c")
        h.await_text("$")
        sc = h.screenshot()
        assert "Traceback" not in sc


def test_ct_clock_first_digit():
    with Runner(*ct_clock_run("--test_mode", "--test_time", "14:56:38")) as h:
        h.default_timeout = 2
        h.await_text("test mode")
        sc = h.screenshot()
        assert "2" in sc
        assert "5" in sc
        assert "6" in sc
        assert "3" in sc
        assert "8" in sc
        assert "0" not in sc
        assert "1" not in sc
        assert "4" not in sc
        h.write("m")
        h.press("Enter")
        h.await_text("test mode")
        sc = h.screenshot()
        assert "1" in sc
        assert "4" in sc
        assert "5" in sc
        assert "6" in sc
        assert "3" in sc
        assert "8" in sc
        assert "0" not in sc
        assert "2" not in sc


def test_display_running_commands(capsys):
    ct_clock.display_running_commands()
    sc = capsys.readouterr().out
    assert "Commands available during run time" in sc


def test_ct_clock_list_running_commands():
    with Runner("bash", width=100, height=60) as h:
        h.default_timeout = 3
        h.await_text("$")
        h.write("python3 ct_clock.py --list_commands")
        h.press("Enter")
        h.await_text("Commands available during run time")


def test_ct_clock_default_command():
    with Runner(*ct_clock_run("--test_mode",
                              "--test_time", "14:00:05",
                              "-m",
                              "--show_date",
                              "-c", "red",
                              "-b"
                              )) as h:
        h.default_timeout = 3
        h.await_text("test mode")
        sleep(1)
        h.write("d")
        h.press("Enter")
        sleep(2)
        h.await_text("test mode")
        sc = h.screenshot()
        assert "PM" in sc
        assert "2" in sc
        assert "4" not in sc
        assert "/" not in sc
        assert "white" in sc
        assert ":" in sc


def test_default_key_in_display_running_commands(capsys):
    ct_clock.display_running_commands()
    sc = capsys.readouterr().out
    assert "Reset setting to defaults" in sc


def test_ct_clock_no_colon_mode_cli():
    with Runner(*ct_clock_run("--test_mode", "-n")) as h:
        h.default_timeout = 3
        h.await_text("test mode")
        sc = h.screenshot()
        assert ":" not in sc


def test_ct_clock_no_colon_mode_running():
    with Runner(*ct_clock_run("--test_mode")) as h:
        h.default_timeout = 3
        h.await_text("test mode")
        h.await_text(":")
        h.write("n")
        h.press("Enter")
        sleep(0.5)
        h.await_text("test mode")
        sc = h.screenshot()
        assert ":" not in sc
        h.write("n")
        h.press("Enter")
        h.await_text(":")


def test_ct_clock_no_colon_mode_reset_to_default():
    with Runner(*ct_clock_run("--test_mode", "-n")) as h:
        h.default_timeout = 3
        h.await_text("test mode")
        sc = h.screenshot()
        assert ":" not in sc
        h.write("d")
        h.press("Enter")
        h.await_text(":")


def test_no_colon_in_display_running_commands(capsys):
    ct_clock.display_running_commands()
    sc = capsys.readouterr().out
    assert "Toggle colon off and on" in sc


def test_ct_clock_date_format_change():
    with Runner(*ct_clock_run("--test_mode", "--test_date", "2021-12-15")) as h:
        h.await_text("test mode")
        h.write("e")
        h.await_text("15/12/2021")
        h.write("E")
        h.await_text("12/15/2021")
        h.write("E")
        h.await_text("2021/12/15")
        h.write("E")
        h.await_text("2021/15/12")
        h.write("E")
        h.await_text("15/12/2021")


def test_ct_clock_date_format_no_change_when_show_date_is_false():
    with Runner(*ct_clock_run("--test_mode", "--test_date", "2021-12-15")) as h:
        h.await_text("test mode")
        h.write("E")
        h.await_text("test mode")
        h.write("e")
        h.await_text("15/12/2021")


def test_ct_clock_date_format_keep_format():
    with Runner(*ct_clock_run("--test_mode", "--test_date", "2021-12-15")) as h:
        h.await_text("test mode")
        h.write("e")
        h.await_text("15/12/2021")
        h.write("E")
        h.await_text("12/15/2021")
        h.write("E")
        h.await_text("2021/12/15")
        h.write("e")
        h.await_text("test mode")
        h.write("e")
        h.await_text("2021/12/15")


def test_ct_clock_reset_date_format_with_d():
    with Runner(*ct_clock_run("--test_mode", "--test_date", "2021-12-15")) as h:
        h.await_text("test mode")
        h.write("e")
        h.await_text("15/12/2021")
        h.write("E")
        h.await_text("12/15/2021")
        h.write("e")
        h.write("d")
        h.write("e")
        h.await_text("15/12/2021")


def test_ct_clock_bg_color_default():
    with Runner(*ct_clock_run("--test_mode")) as h:
        h.await_text("test mode")
        h.await_text("bg=black")


def test_ct_clock_bg_color_cli_color():
    with Runner(*ct_clock_run("--test_mode", "--bg_color", "green")) as h:
        h.await_text("test mode")
        h.await_text("bg=green")


def test_ct_clock_bg_color_change():
    with Runner(*ct_clock_run("--test_mode")) as h:
        h.await_text("test mode")
        h.await_text("bg=black")
        h.press("R")
        h.await_text("bg=red")
        h.press("T")
        h.await_text("bg=green")
        h.press("O")
        h.await_text("bg=cyan")


def test_ct_clock_bg_color_reset_default():
    with Runner(*ct_clock_run("--test_mode")) as h:
        h.await_text("test mode")
        h.await_text("bg=black")
        h.write("I")
        h.await_text("bg=magenta")
        h.write("d")
        h.await_text("bg=black")