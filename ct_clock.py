""" Curses terminal digital clock"""
import argparse
import curses
from datetime import datetime

from typing import Generator
from typing import Optional
from typing import Sequence
from typing import Tuple

import time_machine

CURSES_COLORS = {"black": curses.COLOR_BLACK, "white": curses.COLOR_WHITE,
                 "red": curses.COLOR_RED, "green": curses.COLOR_GREEN,
                 "blue": curses.COLOR_BLUE, "magenta": curses.COLOR_MAGENTA,
                 "yellow": curses.COLOR_YELLOW, "cyan": curses.COLOR_CYAN}
CHAR_CODES_COLOR = {114: "red", 116: "green", 121: "blue", 117: "yellow",
                    105: "magenta", 111: "cyan", 112: "white", 91: "black"}
CHAR_CODES_COLOR_BG = {82: "red", 84: "green", 89: "blue", 85: "yellow",
                       73: "magenta", 79: "cyan", 80: "white", 123: "black"}
COLORS = ["red", "green", "blue", "yellow", "magenta", "cyan", "white", "black"]
DATE_FORMATS = ["%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%Y/%d/%m"]


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


class MyTime:
    # Use for test mode and for possible features.
    def __init__(self, test_mode: bool,
                 test_time: Optional[str] = "",
                 tick: Optional[bool] = True):
        self.test_mode = test_mode
        self.test_time = test_time
        self.tick = tick
        self.save_time = "00:00:00"
        self.paused = False
        if test_mode:
            self.time = self._time_generator()
        else:
            self.time = None

    def _time_generator(self) -> Generator:
        with time_machine.travel(self.test_time, tick=self.tick):
            while True:
                yield datetime.today()

    def get_time(self, time_format: str) -> str:
        if self.test_mode:
            if self.paused:
                return "".join(self.save_time[0:8].split(":"))
            return next(self.time).strftime(time_format)
        else:
            return datetime.today().strftime(time_format)

    def get_date(self, date_format: str) -> str:
        if self.test_mode:
            return next(self.time).date().strftime(date_format)
        else:
            return datetime.today().date().strftime(date_format)

    def reset_time(self) -> None:
        # used in the context manager in the test suite
        if self.test_mode:
            self.time.close()

    def pause(self):
        self.save_time = next(self.time).time().strftime("%H:%M:%S.%f")
        self.time.close()
        self.paused = True

    def unpause(self):
        self.test_time = self.save_time
        self.time = self._time_generator()
        self.paused = False

    def reset(self):
        self.time.close()
        self.save_time = self.test_time = "00:00:00"
        self.time = self._time_generator()
        self.paused = True


def get_segments(number: str, size: str) -> tuple:
    if size == "small":
        seg = SmSeg
    elif size == "medium":
        seg = MedSeg
    elif size == "large":
        seg = LrgSeg
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


def get_space_size(size: str, show_seconds: bool) -> Tuple[int, int]:
    h = w = 0
    if size == "small":
        h = 5
        w = 30 if show_seconds else 20
    elif size == "medium":
        h = 7
        w = 36 if show_seconds else 24
    elif size == "large":
        h = 18
        w = 84 if show_seconds else 56
    return h, w


def fill_background(screen, bg_color: str) -> None:
    curses.init_pair(3, CURSES_COLORS[bg_color], CURSES_COLORS[bg_color])
    height, width = screen.getmaxyx()
    for y in range(height - 1):
        for x in range(width):
            screen.addstr(y, x, " ", curses.color_pair(3))


def set_color(color: str, bg_color: str) -> None:
    curses.init_pair(1, CURSES_COLORS[color], CURSES_COLORS[color])
    curses.init_pair(2, CURSES_COLORS[color], CURSES_COLORS[bg_color])


def display(screen, time_string: str, size: str,
            size_x: int, size_y: int, color: str,
            show_seconds: bool, am_pm: str, show_date: bool,
            colon_on: bool, test_mode: bool, military_time: bool, date: str,
            bg_color: str, stop_watch: bool, stop_watch_state: str) -> None:
    time_segments = []
    for digit in time_string:
        time_segments.append(get_segments(digit, size))
    set_color(color, bg_color)
    size_offset = get_offset(size)
    height, width = get_space_size(size, show_seconds)
    hc = int((size_y - height) / 2)  # height/vertical center
    w_offset = int((size_x - width) / 2)  # width/horizontal center
    screen.clear()
    fill_background(screen, bg_color)
    if stop_watch:
        msg = f"Stop Watch  {stop_watch_state}"
        screen.addstr(hc - 2, int(size_x / 2) - 10, msg, curses.color_pair(2))
    if military_time or time_string[:1] == "1":
        d = "1" if not test_mode else time_string[:1]
        for seg in time_segments[0]:
            screen.addstr(seg[0] + hc, seg[1] + w_offset, d, curses.color_pair(1))
    w_offset += size_offset
    d = "2" if not test_mode else time_string[1:2]
    for seg in time_segments[1]:
        screen.addstr(seg[0] + hc, seg[1] + w_offset, d, curses.color_pair(1))
    if colon_on:
        for seg in get_segments(":", size):
            screen.addstr(seg[0] + hc, seg[1] + w_offset, ":", curses.color_pair(1))
    w_offset += size_offset + 1
    d = "3" if not test_mode else time_string[2:3]
    for seg in time_segments[2]:
        screen.addstr(seg[0] + hc, seg[1] + w_offset, d, curses.color_pair(1))
    w_offset += size_offset
    d = "4" if not test_mode else time_string[3:4]
    for seg in time_segments[3]:
        screen.addstr(seg[0] + hc, seg[1] + w_offset, d, curses.color_pair(1))
    if show_seconds:
        if colon_on:
            for seg in get_segments(":", size):
                screen.addstr(seg[0] + hc, seg[1] + w_offset, ":", curses.color_pair(1))
        w_offset += size_offset + 1
        d = "5" if not test_mode else time_string[4:5]
        for seg in time_segments[4]:
            screen.addstr(seg[0] + hc, seg[1] + w_offset, d, curses.color_pair(1))
        w_offset += size_offset
        d = "6" if not test_mode else time_string[5:]
        for seg in time_segments[5]:
            screen.addstr(seg[0] + hc, seg[1] + w_offset, d, curses.color_pair(1))
        w_offset += size_offset
    else:
        w_offset += size_offset
    if am_pm != "":
        screen.addstr(height + hc, w_offset, am_pm, curses.color_pair(2))
    if show_date:
        screen.addstr(height + hc, w_offset - 15, date, curses.color_pair(2))
    if test_mode:
        screen.addstr(0, 0, "test mode", curses.color_pair(2))
        screen.addstr(1, 0, color, curses.color_pair(2))
        screen.addstr(2, 0, f"bg={bg_color}", curses.color_pair(2))
    screen.refresh()


def main_stopwatch(screen, args: argparse.Namespace) -> None:
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch()
    bg_color = args.bg_color
    digit_color = args.color
    if args.auto_start:
        state = "Running"
        paused = False
    else:
        state = "Stopped"  # running, stopped, paused
        paused = True
    size_y, size_x = screen.getmaxyx()
    if size_x >= 90 and size_y >= 22:
        text_size = "large"
    elif size_x >= 46 and size_y >= 10:
        text_size = "medium"
    elif size_x >= 36 and size_y >= 9:
        text_size = "small"
    else:
        raise CTClockError("Error screen / window is to small")
    update_screen = True
    ct_clock = MyTime(True, "00:00:00", True)
    display_time = ct_clock.get_time("%H%M%S")
    while True:
        if curses.is_term_resized(size_y, size_x):
            size_y, size_x = screen.getmaxyx()
            if size_x >= 90 and size_y >= 22:
                text_size = "large"
            elif size_x >= 46 and size_y >= 12:
                text_size = "medium"
            elif size_x >= 36 and size_y >= 9:
                text_size = "small"
            else:
                raise CTClockError("Error screen / window is to small")
            display(screen, display_time, text_size, size_x, size_y, digit_color, True,
                    "", False, True, args.test_mode, True, "", bg_color, True, state)
        if update_screen or not paused and display_time != ct_clock.get_time("%H%M%S"):
            display_time = ct_clock.get_time("%H%M%S")
            display(screen, display_time, text_size, size_x, size_y, digit_color, True,
                    "", False, True, args.test_mode, True, "", bg_color, True, state)
            update_screen = False
        ch = screen.getch()
        if ch in [81, 113]:  # q, Q
            break
        elif ch == 103:  # g
            if paused:
                ct_clock.unpause()
                paused = False
                state = "Running"
                update_screen = True
            else:
                ct_clock.pause()
                paused = True
                state = "Paused"
                update_screen = True
        elif ch == 104:  # h
            update_screen = True
            paused = True
            state = "Stopped"
            display_time = ct_clock.get_time("%H%M%S")
            ct_clock.reset()
        if ch in CHAR_CODES_COLOR.keys():
            digit_color = CHAR_CODES_COLOR[ch]
            display(screen, display_time, text_size, size_x, size_y, digit_color, True,
                    "", False, True, args.test_mode, True, "", bg_color, True, state)


def main_clock(screen, args: argparse.Namespace) -> None:
    static_color = args.color
    show_seconds = args.no_seconds
    military_time = args.military_time
    mode = args.mode
    cycle_timing = args.cycle_timing
    show_date = args.show_date
    blink_colon = args.blink_colon
    no_colon = args.no_colon
    bg_color = args.bg_color
    curses.curs_set(0)  # Set the cursor to off.
    screen.timeout(0)  # Turn blocking off for screen.getch()
    ct_time = MyTime(args.test_mode, args.test_date + " " + args.test_time, True)
    update_screen = True
    size_y, size_x = screen.getmaxyx()
    if size_x >= 90 and size_y >= 20:
        text_size = "large"
    elif size_x >= 46 and size_y >= 10:
        text_size = "medium"
    elif size_x >= 36 and size_y >= 8:
        text_size = "small"
    else:
        raise CTClockError("Error screen / window is to small")

    time_format = "%H%M%S" if military_time else "%I%M%S"
    date_format_pointer = 0

    colon_on = False if no_colon else True
    cycle_count = 0
    displayed = ct_time.get_time(time_format)
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
        if update_screen or ct_time.get_time(time_format) != displayed:
            old_displayed = displayed
            displayed = ct_time.get_time(time_format)
            if blink_colon:
                colon_on = not colon_on
            if military_time:
                am_pm = ""
            else:
                am_pm = ct_time.get_time("%p")
            if mode == 0:
                color = static_color
            elif mode == 1:
                if cycle_timing == 1:
                    if cycle_count == 6:
                        cycle_count = 0
                    else:
                        cycle_count += 1
                elif cycle_timing == 2 and displayed[-2:] == "00":
                    if cycle_count == 6:
                        cycle_count = 0
                    else:
                        cycle_count += 1
                elif cycle_timing == 3 and old_displayed[0:2] != displayed[0:2]:
                    if cycle_count == 6:
                        cycle_count = 0
                    else:
                        cycle_count += 1
                color = COLORS[cycle_count]
            else:
                color = static_color
            date = ct_time.get_date(DATE_FORMATS[date_format_pointer])
            display(screen, displayed, text_size, size_x, size_y,
                    color, show_seconds, am_pm, show_date, colon_on,
                    args.test_mode, military_time, date, bg_color, False, "")
            update_screen = False
        ch = screen.getch()
        if args.screensaver and ch != -1:
            break
        if ch in [81, 113]:  # q, Q
            break
        if mode == 0 and ch in CHAR_CODES_COLOR.keys():
            static_color = CHAR_CODES_COLOR[ch]
            update_screen = True
        if ch in CHAR_CODES_COLOR_BG.keys():
            bg_color = CHAR_CODES_COLOR_BG[ch]
            update_screen = True
        if ch == 99:  # c
            if mode == 1:
                mode = 0
            else:
                mode += 1
            update_screen = True
        if ch == 115:  # s
            show_seconds = not show_seconds
            update_screen = True
        elif ch == 98:  # b
            if blink_colon:
                blink_colon = False
                colon_on = True
            else:
                blink_colon = True
        if ch == 109:  # m
            if military_time:
                time_format = "%I%M%S"
                military_time = False
            else:
                time_format = "%H%M%S"
                military_time = True
            update_screen = True
        elif ch == 101:  # e
            show_date = not show_date  # flips between True and False
            update_screen = True
        elif ch == 69 and show_date:  # E
            if date_format_pointer == len(DATE_FORMATS) - 1:
                date_format_pointer = 0
            else:
                date_format_pointer += 1
            update_screen = True
        elif ch == 100:  # d
            time_format = "%I%M%S"
            military_time = False
            show_date = False
            date_format_pointer = 0
            show_seconds = True
            mode = 0
            static_color = "white"
            blink_colon = False
            colon_on = True
            bg_color = "black"
            update_screen = True
        elif ch == 110:  # n
            colon_on = not colon_on
            blink_colon = False
            update_screen = True
        if ch == 49:  # 1
            cycle_timing = 1
        elif ch == 50:  # 2
            cycle_timing = 2
        elif ch == 51:  # 3
            cycle_timing = 3

    screen.erase()
    screen.refresh()


def display_running_commands() -> None:
    print("Commands available during run time:")
    print(" q  Q    Quit")
    print(" c       Change color mode")
    print(" s       Toggle show seconds")
    print(" e       Toggle show date")
    print(" E       Cycle date formats")
    print(" b       Toggle blink colon")
    print(" m       Toggle military time")
    print(" n       Toggle colon off and on")
    print(" d       Reset setting to defaults")
    print(" 1,2,3   Color cycle timing 1-every second, 2-every minute, 3-every hour")
    print(" r,t,y,u,i,o,p,[")
    print("         Select color: Red, Green, Blue, Yellow, Magenta, Cyan, White")
    print(" R,T,Y,U,I,O,P,{")
    print("         Change background colors: Red, Green, Blue, Yellow, Magenta, "
          "Cyan, White, Black")
    print()
    print()
    print("STOP WATCH Commands:")
    print(" q  Q    Quit")
    print(" g       Start or pause stop watch")
    print(" h       Reset stop watch to 00:00:00")
    print(" r,t,y,u,i,o,p,[")
    print("         Select color: Red, Green, Blue, Yellow, Magenta, Cyan, White")


def color_type(value: str) -> str:
    """
    Used with argparse to check if value is a valid color.
    """
    lower_value = value.lower()
    if lower_value in COLORS:
        return lower_value
    else:
        raise argparse.ArgumentTypeError(f"{value} is an invalid color name")


def argument_parser(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--color", type=color_type, default="white",
                        help="digit color")
    parser.add_argument("-s", "--no_seconds", action="store_false",
                        help="Do not show seconds")
    parser.add_argument("-m", "--military_time", action="store_true",
                        help="Military time (24 hour clock)")
    parser.add_argument("-S", "--screensaver", action="store_true",
                        help="Screen saver mode.  Any key will exit")
    parser.add_argument("-b", "--blink_colon", action="store_true",
                        help="Blinking colon")
    parser.add_argument("-n", "--no_colon", action="store_true",
                        help="No colon")
    parser.add_argument("--mode", type=int, choices=[0, 1], default=0,
                        help="Mode: 0-normal, 1-cycle whole")
    parser.add_argument("--cycle_timing", type=int, choices=[1, 2, 3], default=2,
                        help="Cycle timing (1 every sec, 2 every min, 3 every hour)")
    parser.add_argument("--show_date", action="store_true",
                        help="Show date")
    parser.add_argument("--bg_color", type=color_type, default="black",
                        help="Back ground color")
    parser.add_argument("--list_commands", action="store_true",
                        help="List commands available during run time.")
    parser.add_argument("--test_mode", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--test_time", type=str, default="00:00:00",
                        help=argparse.SUPPRESS)
    parser.add_argument("--test_date", type=str, default="1970-1-2",
                        help=argparse.SUPPRESS)

    sub_parser = parser.add_subparsers(dest="command")
    stop_watch_parser = sub_parser.add_parser("stop_watch")
    stop_watch_parser.add_argument("--auto_start", action="store_true",
                                   help="Auto start stop watch")
    stop_watch_parser.add_argument("-c", "--color", type=color_type, default="white",
                                   help="digit color")
    stop_watch_parser.add_argument("--list_commands", action="store_true",
                                   help="List commands available during run time.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = argument_parser(argv)
    if args.list_commands:
        display_running_commands()
        return 0
    elif args.command == "stop_watch":
        try:
            curses.wrapper(main_stopwatch, args)
        except CTClockError as e:
            print(e)
            return 1
        return 0
    try:
        curses.wrapper(main_clock, args)
    except CTClockError as e:
        print(e)
        return 1

    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    exit(main())
