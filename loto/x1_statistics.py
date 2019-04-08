#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run statistical tests suites Dieharder & ENT

Should be run from the CLI (depending on how you installed it), e.g.::

    $ python loto/core.py x1

But can also be run as a script::

    $ python loto/x1_statistics.py
"""
import shutil
import subprocess

from pyfiglet import Figlet

import helpers as hp
import config as cf


def build_stats_tests_sets(db_path, db_name):
    """Creates test sets files from the DB.

    A test set file is in the format: one number per line.

    Args:
        db_path(str): path to the directory where the DB is stored.
        db_name(str): name of the DB.

    Returns:
        list: list containing the paths to the files juste created.
    """
    hp.create_necessary_directories(cf.FILES_DIR)  # First run
    files = []
    # Numbers as columns: every sequence is a column in the database. Each column is written to its
    # own file (5 balls + 2 stars = 7 files)
    test_set_cl = hp.get_numbers_as_columns(cf.DB_PATH, cf.DB_NAME)
    for k, v in test_set_cl.items():                    # Inside the dict
        file_path = cf.FILES_DIR + 'x1_tests_set_cl_' + k + '.txt'
        with open(file_path, 'w') as file:
            for iv in v:                                # Inside the lists
                for iiv in iv:                          # Inside the tuples
                    file.write(str(iiv) + '\n')
        files.append(file_path)

    # Numbers as sequence: every sequence is a concatenation of rows in the database. Each sequence
    # is written to its own file (1 seq for balls and 1 for stars)
    test_set_seq = hp.get_numbers_as_sequences(db_path, db_name)
    # Flatten/concatenate results to get a single sequence for ball numbers
    test_set_seq['balls'] = [i for sub in test_set_seq['balls'] for i in sub]
    # Same for stars
    test_set_seq['stars'] = [i for sub in test_set_seq['stars'] for i in sub]
    for k, v in test_set_seq.items():                   # Inside the dict
        file_path = cf.FILES_DIR + 'x1_tests_set_seq_' + k + '.txt'
        with open(file_path, 'w') as file:
            for iv in v:                                # Inside the lists
                file.write(str(iv) + '\n')
        files.append(file_path)

    return files


def check_installed_tools(desired_tools):
    """Prints out if any or all of the tools required are installed on the user's machine.

    Args:
        desired_tools(list): list of the tools wished to be run, e.g. ['pracrand', 'ent',
            'dieharder'].

    Returns:
        list: list of actually installed tools, e.g. ['pracrand', 'dieharder'].
    """
    installed_tools = []
    for tool in desired_tools:
        if shutil.which(tool) is not None:
            print(f"{tool.capitalize()} is installed and in path\n")
            installed_tools.append(tool)
        else:
            print(f"{tool.capitalize()} is not installed or not in path")
            print(f"{tool.capitalize()} tests won't be run...\n")
    return installed_tools


def run_tools(installed_tools, list_paths):
    """Starts a subprocess to run each requested tool, sequentially.

    Each tool is ran with sensible defaults.

    Args:
        installed_tools(list): list of the tools to be run, e.g. ['ent', 'dieharder'].
    """
    for tool in installed_tools:
        print(f"{80 * '#'}\n# {tool.upper()} \n{80 * '#'}")
        for path in list_paths:
            print(f"\n{80 * '-'}\n{path}\n")
            if tool == 'ent':
                # '-c' = print occurrence counts
                subprocess.run(['ent', '-c', path])
            elif tool == 'dieharder':
                # '-f' = filename | '-a' = run all tests with std/default options, (very) long
                subprocess.run(['dieharder', '-a', '-f', path])
        print("\n\n")


def main():
    """"""
    print(f"{Figlet(font='slant').renderText('X1 Statistics')}")

    # Let's check if the tools we would love to use are installed
    desired_tools = ['ent', 'dieharder']
    installed_tools = check_installed_tools(desired_tools)
    # Build the files we need for the statistical tests
    list_paths = build_stats_tests_sets(cf.DB_PATH, cf.DB_NAME)
    # For every file, run all the tests from all the tools present on the user's machine
    run_tools(installed_tools, list_paths)


if __name__ == '__main__':

    main()
