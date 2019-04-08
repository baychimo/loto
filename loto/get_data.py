#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Creates or refreshes the database which will contain all the data we need for our
experiments.

Ideally this is run as an option of the CLI "-r" that you would use like so, for example::

    $ python loto/core.py -r x4
"""
import helpers as hp
import config as cf


def main():
    """"""
    hp.download_files(cf.URLS, cf.TMP_DL_DIR)
    hp.decompress_files(cf.TMP_DL_DIR)
    numbers = hp.prepare_data(cf.TMP_DL_DIR)
    hp.load_db(numbers, cf.DB_PATH, cf.DB_NAME)


if __name__ == '__main__':

    main()
