#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Query the On-line Encyclopedia of Integer Sequences.

For now we query with the 10 latest draws numbers (5 balls + 7 stars). But many combinations can be
tried:longer sequences, sequences randomly picked, etc.

Should be run from the CLI (depending on how you installed it), e.g.::

    $ python loto/core.py x3

But can also be run as a script::

    $ python loto/x3_oeis.py
"""
import itertools
import json
import sys

from pyfiglet import Figlet
import requests
from requests.exceptions import RequestException

import helpers as hp
import config as cf


def get_latest_draws(db_path, db_name, nb_draws):
    """Creates sequences from the latest n draws.

    Args:
        db_path(str): path to the directory where the DB is stored.
        db_name(str): name of the DB.

    Returns:
        list: list of tuples of ints [(15, 31, 40, 44, 48, 1, 12), (16, 1, 2, 7, 48, 1, 12), etc.].
    """
    list_draws = []
    dict_nbs = hp.get_numbers_as_sequences(db_path, db_name)
    for k, v in dict_nbs.items():
        if k.startswith('ball'):
            selected_balls_numbers = v[-nb_draws:]
        else:
            selected_stars_numbers = v[-nb_draws:]
    for ((a, b)) in zip(selected_balls_numbers, selected_stars_numbers):
        list_draws.append(tuple(itertools.chain(a, b)))
    return list_draws


def balls_by_draws(draws):
    """Generates URLs used to query OEIS' database.

    Concatenates sequences of numbers in the format expected by the OEIS' API.

    Returns:
        list: list of URLs.
    """
    urls = []
    for draw in draws:
        balls_param = ''
        for index, ball in enumerate(draw):
            if index >= (len(draw) - 1):
                balls_param += str(ball)
            else:
                balls_param += str(ball) + ','
        urls.append(cf.OEIS_URL + balls_param)
    return urls


def check_sequences_oeis(urls, seconds):
    """Check if given sequences returns something from the OEIS.

    Args:
        urls(list): list of prepared urls to try.
        seconds(float): number of seconds to wait between requests.
    """
    try:
        for url in urls:
            response = requests.get(url, timeout=seconds)
            json_data = json.loads(response.text)
            # As we're trying NOT to hammer OEIS' server, we display a spinning cursor so the user
            # has something to look at between API queries :-)
            hp.spinning_cursor(seconds)

            if json_data['results'] is None:
                print(f"No luck for query       : {url}")
            else:
                print(f"Results found for query : {url}")
    except RequestException as e:
        print(f"Error querying OEIS' API :: {e}")
        sys.exit(1)


def main():
    """"""
    print(f"{Figlet(font='slant').renderText('X3 O.E.I.S')}")

    draws = get_latest_draws(cf.DB_PATH, cf.DB_NAME, 10)
    urls = balls_by_draws(draws)
    check_sequences_oeis(urls, 2)


if __name__ == '__main__':

    main()
