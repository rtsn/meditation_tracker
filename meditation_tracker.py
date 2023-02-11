#! /usr/bin/env python3
"""
A simple meditation time tracker
"""
# make -a and -s mutually exlusive
# add db support
# assume date is today else check if -date is present
# file = db_file
# requirements

import os.path
import argparse
import datetime
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
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
    """ create a table from the createTable_sql statement
    :param conn: Connection object
    :return:
    """
    sql = '''CREATE TABLE IF NOT EXISTS meditation_sessions(
            id integer PRIMARY KEY,
            duration integer NOT NULL,
            [date] timestamp NOT NULL
            ); '''
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except Error as sqlite_er:
        print(sqlite_er)

def add_session_to_db(conn, session):
    """ add meditation session to s
    :param conn:
    :param duration in minutes >= 1
    :param date:
    :return: ???
    """

    sql = '''INSERT INTO meditation_sessions(duration, date)
              VALUES(?,?)'''

    try:
        cur = conn.cursor()
        cur.execute(sql,session)
        return cur.lastrowid
    except Error as sqlite_er:
        print(sqlite_er)
        return None

def get_sum_of_durations(conn):
    """Get a sum total of duration entries in db"""
    sql = 'SELECT SUM(duration) FROM meditation_sessions;'
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchone()[0]
    except Error as sqlite_er:
        print(sqlite_er)
        return None

def get_number_of_sessions():
    pass

def get_average():
    pass

def longest_gap():
    pass

def longest_streak():
    pass

def get_output(minutes):
    """ Get a user friendly output of time in the format days, hours and
    minutes."""
    days = minutes//((24*60))
    minutes = minutes - (days*24*60)
    hours = minutes//60
    minutes = minutes - hours*60

    output = "You have spent "

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
    else:
        output += "no time"

    output += " in meditation."

    return output

def get_compact_output(minutes):
    """Get a compact output in the form days:hours:minutes."""
    days = minutes//((24*60))
    minutes = minutes - (days*24*60)
    hours = minutes//60
    minutes = minutes - hours*60

    output = ""
    if days > 0:
        output += str(days)+"d"
    if hours > 0:
        if output != "":
            output += ":"
        output += str(hours)+"h"
    if minutes > 0:
        if output != "":
            output += ":"
        output += str(minutes)+"m"
    return output

def main():
    # Construct the argument parser and parse the arguments
    arg_desc = '''\
            A very simple meditation time tracker!
            --------------------------------
                This program loads an image
                with OpenCV and Python argparse!
            '''
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter,
                                        description= arg_desc)

    parser.add_argument("-f", "--file",
            metavar="FILE",
            help = "Path to database file.")
    parser.add_argument("-a", "--add",
            metavar="ADD",
            help = "Add an interger number of minutes to the total")
    parser.add_argument("-d", "--date",
            metavar="DATE",
            help = "Specify date of session (YYYY-MM-DD)")
    parser.add_argument("-s", "--set",
            metavar="SET",
            help = "Set total to n number of minutes")
    parser.add_argument("-c", "--compact",
            help = "Compact output of the form days:hours:minutes.",
            action='store_true')

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
            duration = int(args["add"])
            #check that this is an int
            if args["date"]:
                # set datetime objekt thingy
                # check correctly formated
                date = datetime.datetime.today()
            else:
                date = datetime.datetime.today().strftime('%Y-%m-%d')
            session = [duration,date]
            add_session_to_db(conn, session)
            total_duration = get_sum_of_durations(conn)
            if args["compact"]:
                output = get_compact_output(total_duration)
            else:
                output = get_output(total_duration)
            print(output)
        if args["compact"] and not args["add"]:
            total_duration = get_sum_of_durations(conn)
            output = get_compact_output(total_duration)
            print(output)

if __name__ == "__main__":
    main()
