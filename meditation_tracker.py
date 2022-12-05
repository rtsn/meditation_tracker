#! /usr/bin/env python3
"""
A simple meditation time tracker
"""
# make -a and -s mutually exlusive

import os.path
import argparse

def create_file(file_name):
    """Creates file if it doesn't exist."""
    if not os.path.isfile(file_name):
        with open(file_name, "w", encoding="utf8") as file_object:
            file_object.write("0")

def get_minutes(file_name):
    """Returns number of minutes from file_name."""
    with open(file_name, "r", encoding="utf8") as file_object:
        minutes = int(file_object.read())
        file_object.close()
        return minutes

def write_file(file_name,minutes_to_add,total_minutes):
    """Either add (-a -add) MINUTES to total number of minutes in
    file_name or set (-s, --set, total_minutes = -1)."""
    if total_minutes == -1:
        total_minutes = minutes_to_add
    else:
        total_minutes += minutes_to_add
    with open(file_name, "w", encoding="utf8") as file_object:
        file_object.write(str(total_minutes))

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
    """Where everything is sewn together."""

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
            help = "Path to tracker file.")
    parser.add_argument("-a", "--add",
            metavar="ADD",
            help = "Add an interger number of minutes to the total")
    parser.add_argument("-s", "--set",
            metavar="SET",
            help = "Set total to n number of minutes")
    parser.add_argument("-c", "--compact",
            help = "Compact output of the form days:hours:minutes.",
            action='store_true')

    args = vars(parser.parse_args())

    if args["file"]:
        file_name = args["file"]
    else:
        file_name = "~/.med"

    file_name = os.path.expanduser(file_name)

    create_file(file_name)
    total_minutes = get_minutes(file_name)

    if args["add"]:
        minutes_to_add = int(args["add"])
        print(minutes_to_add)
        write_file(file_name,minutes_to_add,total_minutes)
    elif args["set"]:
        minutes_to_add = int(args["set"])
        write_file(file_name,minutes_to_add,-1)

    total_minutes = get_minutes(file_name)

    if args["compact"]:
        output = get_compact_output(total_minutes)
    else:
        output = get_output(total_minutes)

    print(output)

if __name__ == "__main__":
    main()
