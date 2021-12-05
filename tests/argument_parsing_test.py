import pytest

import ct_clock


@pytest.mark.parametrize("test_value, expected", [
    ([], False), (["--show_date"], True),
])
def test_argument_parser_show_date(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.show_date == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], 2),
    (["--cycle_timing", "1"], 1),
    (["--cycle_timing", "2"], 2),
    (["--cycle_timing", "3"], 3),
])
def test_argument_parser_cycle_timing(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.cycle_timing == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], 0), (["--mode", "0"], 0), (["--mode", "1"], 1)
])
def test_argument_parser_mode(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.mode == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], False), (["-b"], True), (["--blink_colon"], True)
])
def test_argument_parser_blink_colon(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.blink_colon == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], False), (["-S"], True), (["--screensaver"], True)
])
def test_argument_parser_screensaver_mode(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.screensaver == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], False), (["-m"], True), (["--military_time"], True)
])
def test_argument_parser_military_time(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.military_time == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], True), (["-s"], False), (["--no_seconds"], False)
])
def test_argument_parser_no_seconds(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.no_seconds == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], "white"), (["--color", "red"], "red"), (["--color", "green"], "green"),
    (["--color", "blue"], "blue"), (["-c", "yellow"], "yellow"),
    (["-c", "magenta"], "magenta"), (["-c", "cyan"], "cyan"),
    (["-c", "white"], "white"),
])
def test_argument_parser_color(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.color == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], False), (["--test_mode"], True),
])
def test_argument_parser_test_mode(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.test_mode == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], "00:00:00"), (["--test_time", "00:00:00"], "00:00:00"),
])
def test_argument_parser_test_time(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.test_time == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], False), (["--list_commands"], True)
])
def test_argument_parser_list_commands(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.list_commands == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], False), (["-n"], True)
])
def test_argument_parser_no_colon(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.no_colon == expected


@pytest.mark.parametrize("test_value, expected", [
    ([], "1970-1-2"), (["--test_date", "1975-5-4"], "1975-5-4"),
])
def test_argument_parses_test_date(test_value, expected):
    result = ct_clock.argument_parser(test_value)
    assert result.test_date == expected


@pytest.mark.parametrize("test_value, expected", [
    ("blue", "blue"), ("Yellow", "yellow"), ("GREEN", "green")
])
def test_color_type_valid_color(test_value, expected):
    result = ct_clock.color_type(test_value)
    assert result == expected


@pytest.mark.parametrize("test_value", [
    "gray", "gold", "2837492", "redgreen", "Blue+Green", "Blue!!!"
])
def test_color_type_invalid_color(test_value):
    with pytest.raises(ct_clock.argparse.ArgumentTypeError):
        ct_clock.color_type(test_value)
