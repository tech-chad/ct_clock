""" Curses terminal digital clock"""
import curses
import time
from datetime import datetime


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


def display(screen, time_string: str, size: str) -> None:
    time_segments = []
    for digit in time_string:
        time_segments.append(get_segments(digit, size))
    offset = 0

    for seg in time_segments[0]:
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    offset += get_offset(size)
    for seg in time_segments[1]:
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    for seg in get_segments(":", size):
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    offset += get_offset(size) + 1
    for seg in time_segments[2]:
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    offset += get_offset(size)
    for seg in time_segments[3]:
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    for seg in get_segments(":", size):
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    offset += get_offset(size) + 1
    for seg in time_segments[4]:
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    offset += get_offset(size)
    for seg in time_segments[5]:
        screen.addstr(seg[0], seg[1] + offset, " ", curses.color_pair(1))
    offset += get_offset(size)


def main_clock(screen) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_CYAN)
    size_y, size_x = screen.getmaxyx()
    if size_x >= 86 and size_y >= 20:
        text_size = "large"
    elif size_x >= 44 and size_y >= 10:
        text_size = "medium"
    elif size_x >= 34 and size_y >= 8:
        text_size = "small"
    else:
        raise CTClockError("Error screen / window is to small")
    displayed = datetime.now().strftime("%H%M%S")
    while True:
        if curses.is_term_resized(size_y, size_x):
            size_y, size_x = screen.getmaxyx()
            if size_x >= 86 and size_y >= 20:
                text_size = "large"
            elif size_x >= 44 and size_y >= 10:
                text_size = "medium"
            elif size_x >= 34 and size_y >= 8:
                text_size = "small"
            else:
                raise CTClockError("Error screen / window is to small")
        screen.clear()
        if datetime.now().strftime("%H%M%S") != displayed:
            displayed = datetime.today().strftime("%H%M%S")
        display(screen, displayed, text_size)
        screen.refresh()
        ch = screen.getch()
        if ch in [81, 113]:  # q, Q
            break
        time.sleep(0.1)

    screen.erase()
    screen.refresh()


def main() -> int:
    try:
        curses.wrapper(main_clock)
    except CTClockError as e:
        print(e)
        return 1


if __name__ == "__main__":
    exit(main())