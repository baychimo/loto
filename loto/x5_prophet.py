#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prophet: ask FB's Prophet to predict the next winning numbers.

Feed the balls/stars numbers as time series (one dataframe each) to Prophet. See what comes out.

Dissapointing results for now of course, prophet seems to show me what I already knew : the
gambler's fallacy is real and on average a number between 1 and 50 is around 25 :-) Heavy computing
to get there...of course I'm joking here: there must be parameters to play with to get more
satisfying results. So next step: play with params, read the docs deeper.

Should be run from the CLI (depending on how you installed it), e.g.::

    $ python loto/core.py x5

But can also be run as a script::

    $ python loto/x5_prophet.py
"""
import datetime as dt
import os
import sqlite3
import sys

import colorama
import matplotlib.pyplot as plt
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from fbprophet import Prophet
from pyfiglet import Figlet
from tqdm import tqdm

import helpers as hp
import config as cf


class suppress_stdout_stderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
    This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).
    `Prophet's github corresponding issue <https://github.com/facebook/prophet/issues/223>`_.
    `Corresponding SO question <https://stackoverflow.com/questions/11130156/suppress-stdout-stderr
    -print-from-python-functions>`_.
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])


def load_prophet_dataframe(db_path, db_name, y_field):
    """
    Returns a pandas dataframe containing a time series with two columns: a date and a number.

    Args:
        db_path(str): path to the directory where the DB is stored.
        db_name(str): name of the DB.
        y_field(str): name of the number field to extract (ball_1, star_2,...).

    Returns :
        dataframe: time series of dates['ds'] + numbers['y'].
    """
    try:
        con = sqlite3.connect(db_path + db_name)
        sql = '''SELECT draw_date AS ds, %s AS y
                 FROM numbers ORDER BY draw_date ASC;''' % y_field
        return pd.read_sql(sql, con, parse_dates=['ds'])
    except sqlite3.OperationalError as e:
        print(f"\nSqlite error :: {e}")
        print(f"{colorama.Fore.RED}Is this your first run? Try running 'python loto/core.py rf'\
                {colorama.Style.RESET_ALL}")
        sys.exit(1)


def generate_plots(prophet, forecast, field):
    """Generate plots with matplotlib with prophet's forecast data.

    Args:
        prophet (obj): the prophet object instance.
        forecast (dataframe): dataframe containing prophet's prediction.
        field (str): name of the field (ball_1, star_2,...).
    """
    try:
        prophet.plot(forecast)
        image_1 = f"x5_prophecy_{field}.png"
        plt.savefig(cf.IMAGES_DIR + 'x5_prophecy_' + field + '.png')
        return f"Image generated: {image_1} \nHere: {cf.IMAGES_DIR}"
    except BaseException as e:
        return f"No image generated :: {e}"


def print_report(dict_nbs):
    """Print DIY mini-table with predictions."""
    colorama.init()
    dash_line = 80 * "-"
    equal_line = 80 * "="
    gb = colorama.Back.GREEN
    rb = colorama.Back.RED
    rs = colorama.Style.RESET_ALL

    print(f"\n{gb}{equal_line}{rs}")
    print(f"{gb}| P R O P H E T{64 * ' '}|{rs}")

    # For historical purposes, the (-2) draw numbers used for the "validation prediction" of (-1)
    # numbers
    ball_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_draw_m2'])))
    star_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_draw_m2'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{gb}| Numbers for draw (-2)          :      | {ball_nbs} |   | {star_nbs} |{rs}")

    # For comparison & validation of the process, the numbers predicted by prophet for (-1) draw
    ball_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_predict_m1'])))
    star_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_predict_m1'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{gb}| Prediction for draw (-1)       :      | {ball_nbs} |   | {star_nbs} |{rs}")

    # For comparison & validation, the actual numbers of the latest draw (-1)
    ball_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_draw_m1'])))
    star_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_draw_m1'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{gb}| Actual numbers for draw (-1)   :      | {ball_nbs} |   | {star_nbs} |{rs}")

    # The winning numbers for next draw
    ball_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_predict_next'])))
    star_nbs = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_predict_next'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{rb}| Prediction for next draw       :      | {ball_nbs} |   | {star_nbs} |{rs}")

    print(f"{gb}{equal_line}{rs}\n")


def main():
    """"""
    print(f"{Figlet(font='slant').renderText('X5 Prophet')}")

    hp.create_necessary_directories(cf.IMAGES_DIR)  # First run

    next_lottery_date = hp.get_next_lottery_date()
    fields = [f for f in cf.TABLE_INFO['fields']['balls']] + \
             [f for f in cf.TABLE_INFO['fields']['stars']]
    dict_nbs = {'balls_draw_m1': [], 'stars_draw_m1': [],
                'balls_draw_m2': [], 'stars_draw_m2': [],
                'balls_predict_m1': [], 'stars_predict_m1': [],
                'balls_predict_next': [], 'stars_predict_next': []}

    for field in tqdm(fields, ncols=80):
        start_time = dt.datetime.now()
        df = load_prophet_dataframe(cf.DB_PATH, cf.DB_NAME, field)
        validate_prediction_date = pd.Timestamp(df['ds'][-1:].values[0])

        # Get the (-2) draw numbers and (-1) draw numbers
        if field.startswith('ball'):
            dict_nbs['balls_draw_m1'].append(df['y'][-1:].values[0])
            dict_nbs['balls_draw_m2'].append(df['y'][-2:].values[0])
        else:
            dict_nbs['stars_draw_m1'].append(df['y'][-1:].values[0])
            dict_nbs['stars_draw_m2'].append(df['y'][-2:].values[0])

        m = Prophet()
        with suppress_stdout_stderr():
            m.fit(df)

        cbdays = CustomBusinessDay(weekmask=cf.LOTO_DAYS)
        future = m.make_future_dataframe(periods=365, freq=cbdays)
        forecast = m.predict(future)

        # Validate the word of prophet. Check what it forecasts for a draw for which we already
        # have the result (-2)
        dfv = forecast.loc[forecast['ds'] == validate_prediction_date]
        if field.startswith('ball'):
            dict_nbs['balls_predict_m1'].append(int(round(dfv['yhat'])))
        else:
            dict_nbs['stars_predict_m1'].append(int(round(dfv['yhat'])))

        # The interesting bit: the prediction for the next draw
        dff = forecast.loc[forecast['ds'] == next_lottery_date]
        if field.startswith('ball'):
            dict_nbs['balls_predict_next'].append(int(round(dff['yhat'])))
        else:
            dict_nbs['stars_predict_next'].append(int(round(dff['yhat'])))

        time_elapsed = str(dt.datetime.now() - start_time)
        tqdm.write(field + time_elapsed.rjust(80 - len(field)))

        plots_message = generate_plots(m, forecast, field)
        tqdm.write(plots_message)

    print_report(dict_nbs)


if __name__ == "__main__":

    main()
