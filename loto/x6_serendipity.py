#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Try different kinds of random

If nothing else works, going back to different sources of randomness to predict the next winning
numbers. The processes are run simultaneously to add bullshit (via multiprocessing/manager).

Should be run from the CLI (depending on how you installed it), e.g.::

    $ python loto/core.py x6

But can also be run as a script::

    $ python loto/x6_serendipity.py
"""
import json
import multiprocessing
import random
from random import SystemRandom

import colorama
from pyfiglet import Figlet
import requests
from requests.exceptions import RequestException

import config as cf


def nist_beacon(url, queue):
    """Gets latest pulse of entropy from NIST Beacon service.

    The last pulse given by the beacon is used as a seed to generate random numbers for a
    "prediction".

    Args:
        url (str): NIST Beacon service URL for last pulse.
        queue (obj): multiprocessing manager queue.

    Returns:
        obj: the manager queue object appended with a dict containing the prediction.
            5 balls (1, 50) and 2 stars (1, 12)
            {'balls': [12, 13, 16, 41, 11], 'stars': [12, 1]}
    """
    try:
        print("Getting entropy from NIST beacon...")

        prediction = {'prediction_nist_beacon': {'balls': [], 'stars': []}}

        response = requests.get(url, timeout=1)
        json_data = json.loads(response.text)
        beacon_seed = json_data['pulse']['localRandomValue']

        random.seed(beacon_seed)

        balls_set = set()
        while len(balls_set) < 5:
            number = random.randint(1, 50)
            balls_set.add(number)
        prediction['prediction_nist_beacon']['balls'] = list(balls_set)

        stars_set = set()
        while len(stars_set) < 2:
            number = random.randint(1, 12)
            stars_set.add(number)
        prediction['prediction_nist_beacon']['stars'] = list(stars_set)

        prediction['prediction_nist_beacon']['balls'].sort()
        prediction['prediction_nist_beacon']['stars'].sort()
        queue.put({**prediction})

    except RequestException as e:
        print(f"NIST Beacon unreachable, error :: {e}")
        prediction['prediction_nist_beacon']['balls'] = [0, 0, 0, 0, 0]
        prediction['prediction_nist_beacon']['stars'] = [0, 0]
        queue.put({**prediction})


def random_org(urls, queue):
    """Gets random sequences of numbers from random.org service.

    The service is called twice: once for the balls (5 ints between 1 and 50) and once for the
    stars (2 ints between 1 and 12).

    Args:
        urls (dict): Random.org preformated URLs.
        queue (obj): multiprocessing manager queue.

    Returns:
        obj: the manager queue object appended with a dict containing the prediction.
            5 balls (1, 50) and 2 stars (1, 12)
            {'balls': [12, 13, 16, 41, 11], 'stars': [12, 1]}
    """
    try:
        print("Getting random sequences from random.org...")

        prediction = {'prediction_random_org': {'balls': [], 'stars': []}}

        balls_set = set()
        response = requests.get(urls['balls'], timeout=1)
        for number in response.text.split():
            balls_set.add(int(number))
        prediction['prediction_random_org']['balls'] = list(balls_set)

        stars_set = set()
        response = requests.get(urls['stars'], timeout=1)
        for number in response.text.split():
            stars_set.add(int(number))
        prediction['prediction_random_org']['stars'] = list(stars_set)

        prediction['prediction_random_org']['balls'].sort()
        prediction['prediction_random_org']['stars'].sort()
        queue.put({**prediction})

    except RequestException as e:
        print(f"Random.org service unreachable, error :: {e}")
        prediction['prediction_random_org']['balls'] = [0, 0, 0, 0, 0]
        prediction['prediction_random_org']['stars'] = [0, 0]
        queue.put({**prediction})


def anu_quantum_rng(url, queue):
    """Gets random numbers in hex format from ANU's Quantum RNG.

    Seven 128 bits long hex numbers are requested. Each of them is used to seed the random
    function, one for each ball (5) and one for each star (2).

    Args:
        url (str): ANU's Quantum RNG preformated URL.
        queue (obj): multiprocessing manager queue.

    Returns:
        obj: the manager queue object appended with a dict containing the prediction.
            5 balls (1, 50) and 2 stars (1, 12)
            {'balls': [12, 13, 16, 41, 11], 'stars': [12, 1]}
    """
    try:
        print("Getting entropy from ANU's Quantum RNG...")

        prediction = {'prediction_anu_qrng': {'balls': [], 'stars': []}}

        response = requests.get(url, timeout=1)
        json_data = json.loads(response.text)
        quantum_seeds = json_data['data']

        balls_set = set()
        for i, seed in enumerate(quantum_seeds[:5]):
            random.seed(seed)
            old_len = len(balls_set)
            new_len = 0
            # As long as the set does not increase in size we're looping on duplicates
            while old_len >= new_len:
                number = random.randint(1, 50)
                balls_set.add(number)
                new_len = len(balls_set)
        prediction['prediction_anu_qrng']['balls'] = list(balls_set)

        stars_set = set()
        for i, seed in enumerate(quantum_seeds[-2:]):
            random.seed(seed)
            old_len = len(stars_set)
            new_len = 0
            while old_len >= new_len:
                number = random.randint(1, 12)
                stars_set.add(number)
                new_len = len(stars_set)
        prediction['prediction_anu_qrng']['stars'] = list(stars_set)

        prediction['prediction_anu_qrng']['balls'].sort()
        prediction['prediction_anu_qrng']['stars'].sort()
        queue.put({**prediction})

    except RequestException as e:
        print(f"ANU quantum RNG service unreachable, error :: {e}")
        prediction['prediction_anu_qrng']['balls'] = [0, 0, 0, 0, 0]
        prediction['prediction_anu_qrng']['stars'] = [0, 0]
        queue.put({**prediction})


def os_random(queue):
    """Generates prediction with dev/urandom.

    Args:
        queue (obj): multiprocessing manager queue.

    Returns:
        obj: the manager queue object appended with a dict containing the prediction.
            5 balls (1, 50) and 2 stars (1, 12)
            {'balls': [12, 13, 16, 41, 11], 'stars': [12, 1]}
    """
    prediction = {'prediction_os_random': {'balls': [], 'stars': []}}

    r = SystemRandom()
    sample = r.sample

    balls = [x for x in range(1, 51)]
    prediction['prediction_os_random']['balls'] = sample(balls, 5)

    stars = [x for x in range(1, 13)]
    prediction['prediction_os_random']['stars'] = sample(stars, 2)

    prediction['prediction_os_random']['balls'].sort()
    prediction['prediction_os_random']['stars'].sort()
    queue.put({**prediction})


def print_report(dict_nbs):
    """Print DIY mini-table with predictions."""
    colorama.init()
    dash_line = 80 * "-"
    equal_line = 80 * "="
    gb = colorama.Back.GREEN
    rb = colorama.Back.RED
    rs = colorama.Style.RESET_ALL

    print(f"\n{gb}{equal_line}{rs}")
    print(f"{gb}| R A N D O M   P R E D I C T I O N S{42 * ' '}|{rs}")

    balls = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_nist_beacon']['balls'])))
    stars = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_nist_beacon']['stars'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{rb}| NIST Beacon                    :      | {balls} |   | {stars} |{rs}")

    balls = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_random_org']['balls'])))
    stars = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_random_org']['stars'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{rb}| Random.org                     :      | {balls} |   | {stars} |{rs}")

    balls = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_anu_qrng']['balls'])))
    stars = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_anu_qrng']['stars'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{rb}| ANU Quantum RNG                :      | {balls} |   | {stars} |{rs}")

    balls = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_os_random']['balls'])))
    stars = ''.join(
        ' | '.join(map('{:02d}'.format, dict_nbs['Q']['prediction_os_random']['stars'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{rb}| OS random (dev/urandom)        :      | {balls} |   | {stars} |{rs}")

    print(f"{gb}{equal_line}{rs}\n")


def main():
    """"""
    print(f"{Figlet(font='slant').renderText('X6 Random')}")

    with multiprocessing.Manager() as manager:

        dict_nbs = {}
        queue = manager.Queue()

        p1 = multiprocessing.Process(target=nist_beacon, args=(cf.BEACON_LP_URL, queue,))
        p1.start()
        p2 = multiprocessing.Process(target=random_org, args=(cf.RANDOM_ORG_URLS, queue,))
        p2.start()
        p3 = multiprocessing.Process(target=anu_quantum_rng, args=(cf.ANU_QRNG_URL, queue,))
        p3.start()
        p4 = multiprocessing.Process(target=os_random, args=(queue,))
        p4.start()

        p1.join()
        dict_nbs['Q'] = queue.get()
        p2.join()
        dict_nbs['Q'].update(queue.get())
        p3.join()
        dict_nbs['Q'].update(queue.get())
        p4.join()
        dict_nbs['Q'].update(queue.get())

    # print(json.dumps(dict_nbs, indent=4))
    print_report(dict_nbs)


if __name__ == '__main__':

    main()
