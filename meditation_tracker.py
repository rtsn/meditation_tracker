#! /usr/bin/env python3
"""
A simple meditation time tracker
"""
# make -a and -s mutually exlusive
# assume date is today else check if -date is present
# file = db_file
# requirements
# stats mutually exclusive with everything else
# fix output printing twice when -a adding
# update help thingy text with small description
# default db location fix
# center text above buddha
# remove set option or change it to stats

import os.path
import argparse
import datetime
import sqlite3
import statistics
from sqlite3 import Error
from uniplot import plot


def create_connection(db_file):
    """create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as sqlite_er:
        print(sqlite_er)
    return None


def create_table(conn):
    """create a table from the createTable_sql statement
    :param conn: Connection object
    :return:
    """
    sql = """CREATE TABLE IF NOT EXISTS meditation_sessions(
            id integer PRIMARY KEY,
            duration integer NOT NULL,
            [date] timestamp NOT NULL
            ); """
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except Error as sqlite_er:
        print(sqlite_er)
        return None
    return 0


def add_session_to_db(conn, session):
    """add meditation session to s
    :param conn:
    :param duration in minutes >= 1
    :param date:
    :return: ???
    """

    sql = """INSERT INTO meditation_sessions(duration, date)
              VALUES(?,?)"""
    try:
        cur = conn.cursor()
        cur.execute(sql, session)
        return cur.lastrowid
    except Error as sqlite_er:
        print(sqlite_er)
        return None


def get_all_sessions(conn):
    """Get session table from db"""

    sql = """SELECT * FROM meditation_sessions"""
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    except Error as sqlite_er:
        print(sqlite_er)
        return None


def get_sum_of_durations(conn):
    """Get a sum total of duration entries in db"""
    sql = "SELECT SUM(duration) FROM meditation_sessions;"
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchone()[0]
    except Error as sqlite_er:
        print(sqlite_er)
        return None


def get_max_duration(conn):
    """Get the maximum duration from entries in db"""
    sql = "SELECT MAX(duration) FROM meditation_sessions;"
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchone()[0]
    except Error as sqlite_er:
        print(sqlite_er)
        return None


def get_min_duration(conn):
    """Get the minimum duration from entries in db"""
    sql = "SELECT MIN(duration) FROM meditation_sessions;"
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchone()[0]
    except Error as sqlite_er:
        print(sqlite_er)
        return None


def get_avg_duration(conn):
    """Get the avg duration from entries in db"""
    sql = "SELECT AVG(duration) FROM meditation_sessions;"
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return round(cur.fetchone()[0], 1)
    except Error as sqlite_er:
        print(sqlite_er)
        return None


def get_median_duration(conn):
    sql = "SELECT duration FROM meditation_sessions;"
    try:
        cur = conn.cursor()
        cur.execute(sql)
        durations = [item[0] for item in cur.fetchall()]
        return statistics.median(durations)
    except Error as sqlite_er:
        print(sqlite_er)
        return None


def get_longest_streak(sessions):
    session_dates = [
        datetime.datetime.strptime(session[2], "%Y-%m-%d") for session in sessions
    ]
    session_dates = list(set(session_dates))
    session_dates.sort()
    number_of_sessions = len(session_dates)
    longest_streak = 0

    if number_of_sessions == 0:
        longest_streak = [0]
    elif number_of_sessions == 1:
        longest_streak = [1]
    else:
        longest_streak = [0]
        streak_days = 1
        first_date = session_dates[0]
        last_date = first_date
        previous_date = first_date
        for date in session_dates[1:]:
            if date == previous_date:
                continue
            if date == previous_date + datetime.timedelta(days=1):
                streak_days += 1
                previous_date = date
                last_date = date
                streak = (streak_days, first_date, last_date)
            else:
                if streak_days > longest_streak[0]:
                    longest_streak = [streak_days, first_date, last_date]
                streak_days = 1
                first_date = date
                previous_date = date
                last_date = date
        if streak[0] > longest_streak[0]:
            longest_streak = streak

    if longest_streak[0] == 0:
        output = "0 days"
    elif longest_streak[0] == 1:
        output = "1 day"
    else:
        days = str(longest_streak[0])
        first_date = longest_streak[1].strftime("%Y-%m-%d")
        last_date = longest_streak[2].strftime("%Y-%m-%d")
        output = str(days) + first_date + " " + last_date
        output = "%s days (%s → %s)" % (days, first_date, last_date)
    return output


def get_longest_gap(sessions):
    session_dates = [
        datetime.datetime.strptime(session[2], "%Y-%m-%d") for session in sessions
    ]
    session_dates = list(set(session_dates))
    session_dates.sort()
    number_of_sessions = len(session_dates)

    if number_of_sessions < 2:
        return "0 days"

    longest_gap = 0
    previous_date = session_dates[0]

    for date in session_dates[1:]:
        if date == previous_date:
            print("yeah")
            continue
        gap = (date - previous_date).days - 1
        if gap > 0 and gap > longest_gap:
            longest_gap = gap
        previous_date = date

    return str(longest_gap) + " days"


def print_stats(conn):
    sessions = get_all_sessions(conn)
    total_duration = get_sum_of_durations(conn)
    print_graph_sessions(sessions)

    print(get_output(total_duration))
    print("Number of sessions: " + str(len(sessions)))
    print(
        "Min: "
        + str(get_min_duration(conn))
        + "min, Max: "
        + str(get_max_duration(conn))
        + "min"
    )
    print(
        "Average: "
        + str(get_avg_duration(conn))
        + "min, Median: "
        + str(get_median_duration(conn))
        + "min."
    )
    print("Longest streak: " + get_longest_streak(sessions))
    print("Longest gap: " + get_longest_gap(sessions))


def get_output(minutes):
    """Get a user friendly output of time in the format days, hours and
    minutes."""
    output = "You have spent "

    if minutes == 0:
        output += "no time in meditation."
        return output

    days = minutes // ((24 * 60))
    minutes = minutes - (days * 24 * 60)
    hours = minutes // 60
    minutes = minutes - hours * 60

    if days > 0:
        output += str(days) + " day"
        if days > 1:
            output += "s"
        if hours > 0 or minutes > 0:
            output += ", "
    if hours > 0:
        output += str(hours) + " hour"
        if hours > 1:
            output += "s"
        if minutes > 0:
            output += ", "
    if minutes > 0:
        output += str(minutes) + " minute"
        if minutes > 1:
            output += "s"

    output += " in meditation."

    return output


def get_compact_output(minutes):
    """Get a compact output in the form days:hours:minutes."""
    days = minutes // ((24 * 60))
    minutes = minutes - (days * 24 * 60)
    hours = minutes // 60
    minutes = minutes - hours * 60

    output = ""
    if days > 0:
        output += str(days) + "d"
    if hours > 0:
        if output != "":
            output += ":"
        output += str(hours) + "h"
    if minutes > 0:
        if output != "":
            output += ":"
        output += str(minutes) + "m"
    return output


def print_graph_time(sessions):
    """Print a graph with sessions over time including days with no
    sessions"""

    dates = [el[2] for el in sessions]
    values = [el[1] for el in sessions]

    new_dates = []
    new_values = []
    previous_date = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
    new_dates.append(dates[0])
    new_values.append(values[0])

    for count, date in enumerate(dates[1:]):
        next_date = previous_date + datetime.timedelta(days=1)
        date_datetime = datetime.datetime.strptime(date, "%Y-%m-%d")

        if date_datetime == next_date:
            new_dates.append(date)
            new_values.append(values[count + 1])
            previous_date = date_datetime
        else:
            while date_datetime != next_date:
                new_dates.append(next_date.strftime("%Y/%m/%d"))
                new_values.append(0)
                next_date += datetime.timedelta(days=1)
            new_dates.append(date)
            new_values.append(values[count + 1])
            previous_date = next_date

    x_axis = list(range(1, len(new_dates) + 1))
    title_str = "Sessions from %s to %s including gaps" % (new_dates[0], new_dates[-1])
    plot(xs=x_axis, ys=new_values, lines=True, title=title_str, y_unit=" min")


def print_graph_sessions(sessions):
    """Plots a graph of length of sessions over time"""
    dates = [el[0] for el in sessions]
    values = [el[1] for el in sessions]
    plot(xs=dates, ys=values, lines=True, title="Sessions", y_unit=" min")


def buddha():
    buddha_str = r"""
_      `-._     `-.     `.   \      :      /   .'     .-'     _.-'      _
 `--._     `-._    `-.    `.  `.    :    .'  .'    .-'    _.-'     _.--'
      `--._    `-._   `-.   `.  \   :   /  .'   .-'   _.-'    _.--'
`--.__     `--._   `-._  `-.  `. `. : .' .'  .-'  _.-'   _.--'     __.--'
__    `--.__    `--._  `-._ `-. `. \:/ .' .-' _.-'  _.--'    __.--'    __
  `--..__   `--.__   `--._ `-._`-.`_=_'.-'_.-' _.--'   __.--'   __..--'
--..__   `--..__  `--.__  `--._`-q(-_-)p-'_.--'  __.--'  __..--'   __..--
      ``--..__  `--..__ `--.__ `-'_) (_`-' __.--' __..--'  __..--''
...___        ``--..__ `--..__`--/__/  \--'__..--' __..--''        ___...
      ```---...___    ``--..__`_(<_   _/)_'__..--''    ___...---'''
```-----....._____```---...___(__\_\_|_/__)___...---'''_____.....-----'''
"""
    return buddha_str


def main():
    # Construct the argument parser and parse the arguments
    arg_desc = (
        """\
            A very simple meditation time tracker!
            --------------------------------
                This program loads an image
                with OpenCV and Python argparse!
            %s"""
        % buddha()
    )
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter, description=arg_desc
    )

    parser.add_argument("-f", "--file", metavar="FILE", help="Path to database file.")
    parser.add_argument(
        "-a",
        "--add",
        metavar="ADD",
        help="Add an interger number of minutes to the total",
    )
    parser.add_argument(
        "-d", "--date", metavar="DATE", help="Specify date of session (YYYY-MM-DD)"
    )
    parser.add_argument(
        "-s", "--set", metavar="SET", help="Set total to n number of minutes"
    )
    parser.add_argument(
        "-c",
        "--compact",
        help="Compact output of the form days:hours:minutes.",
        action="store_true",
    )
    parser.add_argument(
        "-st", "--stats", help="Output various stats", action="store_true"
    )

    args = vars(parser.parse_args())

    if args["file"]:
        database = args["file"]
    else:
        database = "meditation_tracker.db"

    database = os.path.expanduser(database)
    conn = create_connection(database)

    with conn:
        create_table(conn)
        if args["add"]:
            try:
                duration = int(args["add"])
                if duration < 1:
                    raise ValueError()
                if args["date"]:
                    # set datetime objekt thingy
                    # check correctly formated
                    date = datetime.datetime.today()
                else:
                    date = datetime.datetime.today().strftime("%Y-%m-%d")
                session = [duration, date]
                add_session_to_db(conn, session)
                total_duration = get_sum_of_durations(conn)
                if args["compact"]:
                    output = get_compact_output(total_duration)
                else:
                    output = get_output(total_duration)
                print(output)
            except ValueError:
                print("Duration must be an int >= 1")
        if args["compact"] and not args["add"]:
            total_duration = get_sum_of_durations(conn)
            output = get_compact_output(total_duration)
            print(output)
        elif args["stats"]:
            print_stats(conn)
            print_graph_time(get_all_sessions(conn))
        else:
            total_duration = get_sum_of_durations(conn)
            output = get_compact_output(total_duration)
            print(output)


if __name__ == "__main__":
    main()
