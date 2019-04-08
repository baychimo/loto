#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os


# Let's do everything from here
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Downloads
TMP_DL_DIR = os.path.join(ROOT_DIR, 'data/scrap/')
URLS = [
    'https://media.fdj.fr/generated/game/euromillions/euromillions.zip',
    'https://media.fdj.fr/generated/game/euromillions/euromillions_2.zip',
    'https://media.fdj.fr/generated/game/euromillions/euromillions_3.zip',
    'https://media.fdj.fr/generated/game/euromillions/euromillions_4.zip'
]

# Files folder
FILES_DIR = os.path.join(ROOT_DIR, 'data/files/')
TEST_FILES_DIR = os.path.join(ROOT_DIR, '../tests/fake_data/files/')

# Images folder
IMAGES_DIR = os.path.join(ROOT_DIR, 'data/images/')

# Database
DB_NAME = 'numbers.db'
TEST_DB_NAME = 'numbers_test.db'
DB_PATH = os.path.join(ROOT_DIR, 'data/db/')
TEST_DB_PATH = os.path.join(ROOT_DIR, '../tests/fake_data/db/')
TABLE_INFO = {
    'tablename': 'numbers',
    'fields': {
        'draw_date': 'datetime',
        'balls': {
            'ball_1': 'int',
            'ball_2': 'int',
            'ball_3': 'int',
            'ball_4': 'int',
            'ball_5': 'int'
        },
        'stars': {
            'star_1': 'int',
            'star_2': 'int'
        }
    }
}

# Other constants
LOTO_DAYS = 'Tue Fri'

# OEIS base URL (not really an API)
OEIS_URL = 'https://oeis.org/search?fmt=json&q='

# NIST beacon last pulse
BEACON_LP_URL = 'https://beacon.nist.gov/beacon/2.0/pulse/last'

# random.org
RANDOM_ORG_URLS = {
    'balls': 'https://www.random.org/integer-sets/'
             '?sets=1&num=5&min=1&max=50&order=index&format=plain&rnd=new',
    'stars': 'https://www.random.org/integer-sets/'
             '?sets=1&num=2&min=1&max=12&order=index&format=plain&rnd=new'
}

# ANU's Quantum RNG
ANU_QRNG_URL = 'https://qrng.anu.edu.au/API/jsonI.php?length=7&type=hex16&size=128'
