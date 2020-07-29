""" Curses terminal digital clock"""
import argparse
import curses
import time
from datetime import datetime

from typing import Optional
from typing import Sequence


# might not need color black
CURSES_COLORS = {"black": curses.COLOR_BLACK, "white": curses.COLOR_WHITE,
                 "red": curses.COLOR_RED, "green": curses.COLOR_GREEN,
                 "blue": curses.COLOR_BLUE, "magenta": curses.COLOR_MAGENTA,
                 "yellow": curses.COLOR_YELLOW, "cyan": curses.COLOR_CYAN}
CHAR_CODES_COLOR = {114: "red", 116: "green", 121: "blue", 117: "yellow",
                    105: "magenta", 111: "cyan", 112: "white"}


class CTClockError(Exception):
    pass


class SmSeg:
    seg1 = (0, 0), (0, 1), (0, 2)
    seg2 = (0, 2), (1, 2), (2, 2)
    seg3 = (2, 2), (3, 2), (4, 2)
    seg4 = (4, 0), (4, 1), (4, 2)
    seg5 = (2, 0), (3, 0), (4, 0)
    seg6 = (0, 0), (1, 0), (2, 0)
    seg7 = (2, 0), (2, 1), (2, 2)
    colon = (1, 4), (3, 4)


class MedSeg:
    seg1 = (0, 0), (0, 1), (0, 2), (0, 3)
    seg2 = (0, 3), (1, 3), (2, 3), (3, 3)
    seg3 = (3, 3), (4, 3), (5, 3), (6, 3)
    seg4 = (6, 0), (6, 1), (6, 2), (6, 3)
    seg5 = (3, 0), (4, 0), (5, 0), (6, 0)
    seg6 = (0, 0), (1, 0), (2, 0), (3, 0)
    seg7 = (3, 0), (3, 1), (3, 2), (3, 3)
    colon = (2, 5), (4, 5)


class LrgSeg:
    seg1 = (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), \
           (0, 8), (0, 9), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), \
           (1, 6), (1, 7), (1, 8), (1, 9)
    seg2 = (0, 8), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), \
           (8, 8), (9, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), \
           (6, 9), (7, 9), (8, 9), (9, 9)
    seg3 = (8, 8), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8), \
           (15, 8), (16, 8), (17, 8), (8, 9), (9, 9), (10, 9), (11, 9), \
           (12, 9), (13, 9), (14, 9), (15, 9), (16, 9), (17, 9)
    seg4 = (16, 0), (16, 1), (16, 2), (16, 3), (16, 4), (16, 5), (16, 6), \
           (16, 7), (16, 8), (16, 9), (17, 0), (17, 1), (17, 2), (17, 3), \
           (17, 4), (17, 5), (17, 6), (17, 7), (17, 8), (17, 9)
    seg5 = (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), \
           (15, 0), (16, 0), (17, 0), (8, 1), (9, 1), (10, 1), (11, 1), \
           (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1)
    seg6 = (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), \
           (8, 0), (9, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), \
           (6, 1), (7, 1), (8, 1), (9, 1)
    seg7 = (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), \
           (8, 8), (8, 9), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), \
           (9, 6), (9, 7), (9, 8), (9, 9)
    colon = (5, 12), (12, 12)


def get_segments(number: str, size: str) -> tuple:
    if size == "small":
        seg = SmSeg
    elif size == "medium":
        seg = MedSeg
    elif size == "large":
        seg = LrgSeg()
    else:
        seg = SmSeg
    if number == "0":
        return seg.seg1 + seg.seg2 + seg.seg3 + seg.seg4 + seg.seg5 + seg.seg6
    elif number == "1":
        return seg.seg2 + seg.seg3
    elif number == "2":
        return seg.seg1 + seg.seg2 + seg.seg7 + seg.seg5 + seg.seg4
    elif number == "3":
        return seg.seg1 + seg.seg2 + seg.seg7 + seg.seg3 + seg.seg4
    elif number == "4":
        return seg.seg6 + seg.seg7 + seg.seg2 + seg.seg3
    elif number == "5":
        return seg.seg1 + seg.seg6 + seg.seg7 + seg.seg3 + seg.seg4
    elif number == "6":
        return seg.seg6 + seg.seg5 + seg.seg4 + seg.seg3 + seg.seg7
    elif number == "7":
        return seg.seg1 + seg.seg2 + seg.seg3
    elif number == "8":
        return seg.seg1 + seg.seg2 + seg.seg3 + seg.seg4 + seg.seg5 + \
               seg.seg6 + seg.seg7
    elif number == "9":
        return seg.seg1 + seg.seg2 + seg.seg3 + seg.seg4 + seg.seg6 + seg.seg7
    elif number == ":":
        return seg.colon


def get_offset(size: str) -> int:
    if size == "small":
        return 5
    elif size == "medium":
        return 6
    elif size == "large":
        return 14


def get_space_size(size: str, show_seconds: bool) -> tuple:
    h = w = 0
    if size == "small":
        if show_seconds:
            h = 5
            w = 30
        else:
            h = 5
            w = 20
    elif size == "medium":
        if show_seconds:
            h = 7
            w = 36
        else:
            h = 7
            w = 24
    elif size == "large":
        if show_seconds:
            h = 18
            w = 84
        else:
            h = 18
            w = 56
    return h, w


def set_color(color: str) -> None:
    curses.init_pair(1, CURSES_COLORS[color], CURSES_COLORS[color])
    curses.init_pair(2, CURSES_COLORS[color], curses.COLOR_BLACK)
    # curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_CYAN)


def display(screen, time_string: str, size: str,
            size_x: int, size_y: int, color: str,
            show_seconds: bool, am_pm: str) -> None:
    time_segments = []
    for digit in time_string:
        time_segments.append(get_segments(digit, size))
    set_color(color)
    size_offset = get_offset(size)
    height, width = get_space_size(size, show_seconds)
    hc = int((size_y - height) / 2)  # height/vertical center
    w_offset = int((size_x - width) / 2)  # width/horizontal center

    for seg in time_segments[0]:
        screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
    w_offset += size_offset
    for seg in time_segments[1]:
        screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
    for seg in get_segments(":", size):
        screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
    w_offset += size_offset + 1
    for seg in time_segments[2]:
        screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
    w_offset += size_offset
    for seg in time_segments[3]:
        screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
    if show_seconds:
        for seg in get_segments(":", size):
            screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
        w_offset += size_offset + 1
        for seg in time_segments[4]:
            screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
        w_offset += size_offset
        for seg in time_segments[5]:
            screen.addstr(seg[0] + hc, seg[1] + w_offset, " ", curses.color_pair(1))
        w_offset += size_offset
    else:
        w_offset += size_offset
    if am_pm != "":
        screen.addstr(height + hc, w_offset, am_pm, curses.color_pair(2))


def main_clock(screen, color: str, show_seconds: bool,
               military_time: bool, screen_saver_mode: bool) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch()
    update_screen = True
    size_y, size_x = screen.getmaxyx()
    if size_x >= 86 and size_y >= 20:
        text_size = "large"
    elif size_x >= 44 and size_y >= 10:
        text_size = "medium"
    elif size_x >= 34 and size_y >= 8:
        text_size = "small"
    else:
        raise CTClockError("Error screen / window is to small")

    if military_time:
        time_format = "%H%M%S"
    else:
        time_format = "%I%M%S"

    displayed = datetime.now().strftime(time_format)
    while True:
        if curses.is_term_resized(size_y, size_x):
            size_y, size_x = screen.getmaxyx()
            update_screen = True
            if size_x >= 90 and size_y >= 20:
                text_size = "large"
            elif size_x >= 46 and size_y >= 10:
                text_size = "medium"
            elif size_x >= 36 and size_y >= 8:
                text_size = "small"
            else:
                raise CTClockError("Error screen / window is to small")
        if datetime.now().strftime(time_format) != displayed or update_screen:
            screen.clear()
            displayed = datetime.today().strftime(time_format)
            if military_time:
                am_pm = ""
            else:
                am_pm = datetime.today().strftime("%p")
            display(screen, displayed, text_size, size_x, size_y,
                    color, show_seconds, am_pm)
            screen.refresh()
            update_screen = False
        ch = screen.getch()
        if screen_saver_mode and ch != -1:
            break
        if ch in [81, 113]:  # q, Q
            break
        if ch in CHAR_CODES_COLOR.keys():
            color = CHAR_CODES_COLOR[ch]
            update_screen = True
        if ch == 115:  # s
            show_seconds = not show_seconds
            update_screen = True
        if ch == 109:  # m
            if military_time:
                time_format = "%I%M%S"
                military_time = False
            else:
                time_format = "%H%M%S"
                military_time = True
            update_screen = True
        time.sleep(0.1)

    screen.erase()
    screen.refresh()


def argument_parser(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--color", default="white", help="digit color")
    parser.add_argument("-s", "--no_seconds", action="store_false",
                        help="Do not show seconds")
    parser.add_argument("-m", "--military_time", action="store_true",
                        help="Military time (24 hour clock)")
    parser.add_argument("-S", "--screensaver", action="store_true",
                        help="Screen saver mode.  Any key will exit")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = argument_parser(argv)
    try:
        curses.wrapper(main_clock, args.color, args.no_seconds,
                       args.military_time, args.screensaver)
    except CTClockError as e:
        print(e)
        return 1


if __name__ == "__main__":
    exit(main())
