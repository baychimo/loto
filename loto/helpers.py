#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common helpers/utilities functions.

Helpers for downloading files, listing files in a directory, decompressing zipped folders,
reshaping data from a csv file, so it can be loaded in a sqlite3 DB.
"""
import csv
import datetime as dt
import itertools
import os
import sys
import shutil
import sqlite3
import time
import zipfile

import colorama
import dateutil.parser
import pandas as pd
import requests
from requests.exceptions import RequestException
from tqdm import tqdm

import config as cf


def create_necessary_directories(path):
    """Given a path, creates all necessary folders to satisfy it.

    If the path/folder already exists, nothing is done.

    Args:
        path(str): path to the directory(ies) to be created.
    """
    try:
        os.makedirs(path)
    except BaseException:
        pass


def download_files(urls, path):
    """Handles the downloading of lottery files.

    Destroys and recreates the download folder.
    Downloads files from a given list of urls into that folder.

    Args:
        urls(list): list of urls of the files to be downloaded.
        path(str): path to the download directory.
    """
    try:
        os.makedirs(path)
    except BaseException:
        shutil.rmtree(path)
        os.makedirs(path)
    print("Downloading files with previous draw numbers from lottery website---------------")
    for url in tqdm(urls, ncols=80):
        try:
            response = requests.get(url, timeout=2)
            with open(path + os.path.basename(url), 'wb') as file:
                file.write(response.content)
            tqdm.write(url)
        except RequestException as e:
            tqdm.write("DOWNLOAD ERROR :: " + str(e))
            sys.exit(1)


def list_files(path, ext):
    """Lists files in a folder for a specific extension.

    Walks all files in a folder and returns a list containing the paths of the files in that folder
    for a specific file extension.

    Args:
        path(str): path to the directory to explore.
        ext(str): extension of the files to list.

    Returns:
        list: A list containing paths.
    """
    files = []
    for (path, dirnames, filenames) in os.walk(path):
        files.extend(
            os.path.join(path, name) for name in filenames if name.endswith(ext)
        )
    return files


def decompress_files(path):
    """Decompresses all zip files in a folder.

    Args:
        path(str): path to the folder containing the zip files.
    """
    print("Decompressing downloaded files:-------------------------------------------------")
    files = list_files(path, '.zip')
    for file in tqdm(files, ncols=80):
        with zipfile.ZipFile(file, 'r') as zip_ref:
            zip_ref.extractall(path)
            tqdm.write(file)


def get_next_lottery_date():
    """Returns the date of the next lottery day.

    Euromillions is drawn every Tuesday and Friday. So depending on the current day, it will return
    either next Tuesday or next Friday.

    Returns:
        timestamp: next lottery day, returned as a pandas timestamp.
    """
    today = dt.datetime.today()

    days_till_next_tuesday = 1 - today.weekday()
    if days_till_next_tuesday <= 0:
        days_till_next_tuesday += 7
    next_tuesday = today + dt.timedelta(days_till_next_tuesday)

    days_till_next_friday = 1 - today.weekday()
    if days_till_next_friday <= 0:
        days_till_next_friday += 7
    next_friday = today + dt.timedelta(days_till_next_friday)

    next_tuesday = pd.Timestamp(next_tuesday.date())
    next_friday = pd.Timestamp(next_tuesday.date())

    return next_tuesday if next_tuesday < next_friday else next_friday


def prepare_data(path):
    """Prepares data to be loaded in the database.

    Extract the data we want from the CSV files which is to be loaded in the DB.
    Returns data in the shape we expect (as a python list).

    Args:
        path(str): path to the folder containing the CSV files to prepare.

    Returns:
        list: a list containing columns corresponding to DB expectations.
    """
    files = list_files(path, '.csv')
    data = []

    for file in files:
        with open(file, 'r', encoding='ISO-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            lst = list(reader)
            for e in lst:
                e['date_de_tirage'] = dateutil.parser.parse(e['date_de_tirage'], dayfirst=True)
                e['boule_1'] = int(e['boule_1'])
                e['boule_2'] = int(e['boule_2'])
                e['boule_3'] = int(e['boule_3'])
                e['boule_4'] = int(e['boule_4'])
                e['boule_5'] = int(e['boule_5'])
                e['etoile_1'] = int(e['etoile_1'])
                e['etoile_2'] = int(e['etoile_2'])
                data.append(e)

    return [(e['date_de_tirage'],
             e['boule_1'],
             e['boule_2'],
             e['boule_3'],
             e['boule_4'],
             e['boule_5'],
             e['etoile_1'],
             e['etoile_2'])
            for e in data]


def load_db(numbers, db_path, db_name):
    """Loads the numbers in the database.

    Destroys and recreates the DB folder.
    (Re)creates the DB.
    Loads given data in the DB.

    Args:
        numbers(list): euromillions winning numbers list.
        db_name(str): name given to the DB.
        db_path(str): path to the directory where the DB is stored.
    """
    print("Loading data in database:-------------------------------------------------------")
    # Sqlite does not enforce any type checking. And our numbers are strings, so there will be
    # some type casting here, but hey that's better than nothing :-)
    for row in numbers:
        if not all([isinstance(row[0], dt.datetime),
                    isinstance(row[1], int),
                    isinstance(row[2], int),
                    isinstance(row[3], int),
                    isinstance(row[4], int),
                    isinstance(row[5], int),
                    isinstance(row[6], int),
                    isinstance(row[7], int)]):
            raise TypeError("Some data is invalid in lottery files:", str(row))

    try:
        os.makedirs(db_path)
    except BaseException:
        shutil.rmtree(db_path)
        os.makedirs(db_path)
        print("INFO                   :: DB exists, overwritten")

    con = sqlite3.connect(db_path + db_name)
    print(f"Sqlite3 DB created     :: {db_name}")
    c = con.cursor()

    c.execute(
        '''CREATE TABLE IF NOT EXISTS numbers
        (draw_date datetime, ball_1 int, ball_2 int, ball_3 int,
         ball_4 int, ball_5 int, star_1 int, star_2 int);''')
    print("Table created          :: numbers")

    c.executemany(
        '''INSERT INTO numbers
        (draw_date, ball_1, ball_2, ball_3, ball_4, ball_5,
         star_1, star_2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);''', numbers)
    c.execute('''SELECT COUNT(*) FROM numbers''')
    count = c.fetchall()
    print(f"Number of records      :: {count[0][0]}")

    con.commit()
    con.close()


def get_numbers_as_columns(db_path, db_name):
    """Selects lottery numbers as columns of numbers.

    For each column containing either a ball number or a star number, extracts all numbers to a
    list, sorted by date. The lists are returned as a dict of lists (of tuples).

    Args:
        db_name(str): name of the DB.
        db_path(str): path to the directory where the DB is stored.

    Returns:
        dict: dictionary of lists of tuples {'column_name': [(number, number,...)]}.
    """
    try:
        con = sqlite3.connect(db_path + db_name)
        c = con.cursor()
        numbers_as_columns = {}

        for ball in cf.TABLE_INFO['fields']['balls']:
            c.execute('''SELECT %s FROM numbers ORDER BY draw_date''' % ball)
            numbers_as_columns[ball] = c.fetchall()

        for star in cf.TABLE_INFO['fields']['stars']:
            c.execute('''SELECT %s FROM numbers ORDER BY draw_date''' % star)
            numbers_as_columns[star] = c.fetchall()

        con.close()
        return numbers_as_columns
    except sqlite3.OperationalError as e:
        print(f"Sqlite error :: {e}")
        print(f"{colorama.Fore.RED}Is this your first run? Try running 'python loto/core.py rf'\
                {colorama.Style.RESET_ALL}")
        sys.exit(1)


def get_numbers_as_sequences(db_path, db_name):
    """Selects lottery numbers as sequences of numbers (in the order drawn).

    Extract all ball numbers in lists of 5 (one for each draw). And extract all star numbers in
    lists of two. Return both lists in a dict.

    Args:
        db_name(str): name of the DB.
        db_path(str): path to the directory where the DB is stored.

    Returns:
        dict: dictionary of lists {'balls': [numbers], 'stars': [numbers]}.
    """
    try:
        con = sqlite3.connect(db_path + db_name)
        c = con.cursor()
        numbers_as_sequences = {}

        c.execute(
            '''SELECT ball_1, ball_2, ball_3, ball_4, ball_5
               FROM numbers ORDER BY draw_date'''
        )
        numbers_as_sequences['balls'] = c.fetchall()

        c.execute(
            '''SELECT star_1, star_2 FROM numbers ORDER BY draw_date'''
        )
        numbers_as_sequences['stars'] = c.fetchall()

        con.close()
        return numbers_as_sequences
    except sqlite3.OperationalError as e:
        print(f"Sqlite error :: {e}")
        print(f"{colorama.Fore.RED}Is this your first run? Try running 'python loto/core.py rf'\
                {colorama.Style.RESET_ALL}")
        sys.exit(1)


def spinning_cursor(seconds):
    """Shows a spinning cursor for a number of seconds."""
    spinner = itertools.cycle(['-', '\\', '|', '/'])
    t_end = time.time() + seconds
    while time.time() < t_end:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.2)
        sys.stdout.write('\b')
