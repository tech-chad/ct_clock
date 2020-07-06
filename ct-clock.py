""" Curses terminal digital clock"""
import curses
from time import sleep


class SmSeg:
    seg1 = (0, 0), (0, 1), (0, 2)
    seg2 = (0, 2), (1, 2), (2, 2)
    seg3 = (2, 2), (3, 2), (4, 2)
    seg4 = (4, 0), (4, 1), (4, 2)
    seg5 = (2, 0), (3, 0), (4, 0)
    seg6 = (0, 0), (1, 0), (2, 0)
    seg7 = (2, 0), (2, 1), (2, 2)
    colon1 = (1, 4), (3, 4)
    offset = 6


class MedSeg:
    seg1 = (0, 0), (0, 1), (0, 2), (0, 3)
    seg2 = (0, 3), (1, 3), (2, 3), (3, 3)
    seg3 = (3, 3), (4, 3), (5, 3), (6, 3)
    seg4 = (6, 0), (6, 1), (6, 2), (6, 3)
    seg5 = (3, 0), (4, 0), (5, 0), (6, 0)
    seg6 = (0, 0), (1, 0), (2, 0), (3, 0)
    seg7 = (3, 0), (3, 1), (3, 2), (3, 3)
    offset = 8


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


def get_segments(number: int, size: str) -> tuple:
    if size == "small":
        seg = SmSeg
    elif size == "medium":
        seg = MedSeg
    elif size == "large":
        seg = LrgSeg()
    else:
        seg = SmSeg
    if number == 0:
        return seg.seg1 + seg.seg2 + seg.seg3 + seg.seg4 + seg.seg5 + seg.seg6
    elif number == 1:
        return seg.seg2 + seg.seg3
    elif number == 2:
        return seg.seg1 + seg.seg2 + seg.seg7 + seg.seg5 + seg.seg4
    elif number == 3:
        return seg.seg1 + seg.seg2 + seg.seg7 + seg.seg3 + seg.seg4
    elif number == 4:
        return seg.seg6 + seg.seg7 + seg.seg2 + seg.seg3
    elif number == 5:
        return seg.seg1 + seg.seg6 + seg.seg7 + seg.seg3 + seg.seg4
    elif number == 6:
        return seg.seg6 + seg.seg5 + seg.seg4 + seg.seg3 + seg.seg7
    elif number == 7:
        return seg.seg1 + seg.seg2 + seg.seg3
    elif number == 8:
        return seg.seg1 + seg.seg2 + seg.seg3 + seg.seg4 + seg.seg5 + \
               seg.seg6 + seg.seg7
    elif number == 9:
        return seg.seg1 + seg.seg2 + seg.seg3 + seg.seg4 + seg.seg6 + seg.seg7


def display(screen, number: int) -> None:
    segment_list = get_segments(number, "large")
    for seg in segment_list:
        screen.addstr(seg[0], seg[1], " ", curses.color_pair(1))
        screen.addstr(seg[0], seg[1] + 14, " ", curses.color_pair(2))


def main_clock(screen) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_CYAN)
    i = 0
    while True:
        screen.clear()
        display(screen, i)
        i += 1
        if i > 9:
            i = 0
        screen.refresh()
        ch = screen.getch()
        if ch in [81, 113]:  # q, Q
            break
        sleep(1)

    screen.erase()
    screen.refresh()


def main() -> None:
    curses.wrapper(main_clock)


if __name__ == "__main__":
    main()
