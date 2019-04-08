#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Visualize the lottery numbers distribution with matplotlib.

Many different combinations of parameters can be tried here. Most graphs generated here are trying
to be visually pleasing if not very helpful :-)

Should be run from the CLI (depending on how you installed it), e.g.::

    $ python loto/core.py x2

But can also be run as a script::

    $ python loto/x2_plots.py
"""
import sqlite3
import sys

import colorama
import matplotlib.pyplot as plt
import pandas as pd
from pyfiglet import Figlet
from tqdm import tqdm

import helpers as hp
import config as cf


def load_plots_dataframe(db_path, db_name):
    """Returns a pandas dataframe containing all the rows & columns of the numbers table.

    Args:
        db_path(str): path to the directory where the DB is stored.
        db_name(str): name of the DB.

    Returns:
        pandas dataframe: one to one extraction of the table.
    """
    try:
        con = sqlite3.connect(db_path + db_name)
        sql = '''SELECT draw_date,
                        ball_1, ball_2, ball_3, ball_4, ball_5,
                        star_1, star_2
                 FROM numbers
                 ORDER BY draw_date ASC;'''
        return pd.read_sql(sql, con, parse_dates=['draw_date'])
    except sqlite3.OperationalError as e:
        print(f"Sqlite error :: {e}")
        print(f"{colorama.Fore.RED}Is this your first run? Try running 'python loto/core.py rf'\
                {colorama.Style.RESET_ALL}")
        sys.exit(1)


def gen_heatmap(df):
    """Generates a heatmap image.

    On the y-axis the draw dates, on the x-axis the balls and stars. Generates a nice image of the
    distribution of the numbers more than anything else. The image is written to the images dir.

    Args:
        df(dataframe): pandas dataframe containing all the draw results for the lottery
            (dates/balls/stars).

    Returns:
        string: a string containing either a success or failure message.
    """
    try:
        plt.figure(figsize=(6, 9))
        plt.xlabel('')
        plt.ylabel('')
        plt.pcolormesh(df)
        plt.xticks([])
        plt.yticks([])
        plt.savefig(
            cf.IMAGES_DIR + 'x2_heatmap.png',
            dpi=150,
            bbox_inches='tight',
            pad_inches=-0.03
        )
        plt.close()
        return f"Heatmap created    ::   x2_heatmap.png"
    except BaseException as e:
        return f"Heatmap not created, error :: {e}"


def gen_line_plot(df):
    """Generates a line plot.

    Args:
        df(dataframe): pandas dataframe containing all the draw results for the lottery
            (dates/balls/stars).

    Returns:
        string: a string containing either a success or failure message.
    """
    try:
        with plt.style.context('dark_background'):
            df.plot.line(figsize=(14, 3), cmap='gist_rainbow')
            plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
                       mode="expand", borderaxespad=0, ncol=7)
            plt.xlabel('')
            plt.ylabel('')
            plt.savefig(cf.IMAGES_DIR + 'x2_line.png', dpi=150, bbox_inches='tight')
            plt.close()
        return f"Line plot created  ::   x2_line.png"
    except BaseException as e:
        return f"Line plot not created, error :: {e}"


def gen_area_plot(df):
    """Generates an area plot.

    Args:
        df(dataframe): pandas dataframe containing all the draw results for the lottery
            (dates/balls/stars).

    Returns:
        string: a string containing either a success or failure message.
    """
    try:
        with plt.style.context('dark_background'):
            df.plot.area(figsize=(14, 3), legend=False, subplots=True)
            plt.figlegend(loc='upper right', labelspacing=1.15, borderaxespad=1.65)
            plt.xlabel('')
            [ax.set_yticks([]) for ax in plt.gcf().axes]
            plt.savefig(cf.IMAGES_DIR + 'x2_area.png', dpi=150, bbox_inches='tight')
            plt.close()
        return f"Area plot created  ::   x2_area.png"
    except BaseException as e:
        return f"Area plot not created, error :: {e}"


def gen_pie_plot(df):
    """Generates pie plots.

    Shows the distribution of numbers drawn per ball (e.g. how many times the number 42 was drawn
    for ball n°3).

    Args:
        df(dataframe): pandas dataframe containing all the draw results for the lottery
            (dates/balls/stars).

    Returns:
        string: a string containing either a success or failure message.
    """
    try:
        with plt.style.context('dark_background'):
            fig, axs = plt.subplots(1, 7, figsize=(20, 7))
            for i, column in enumerate(df.columns.values):
                col_df = df.groupby(column).size()
                if i < 5:
                    col_df.plot.pie(ax=axs[i], fontsize=4.5)
                else:
                    col_df.plot.pie(ax=axs[i], fontsize=8)
                axs[i].set_ylabel('')
            plt.savefig(cf.IMAGES_DIR + 'x2_pie.png', dpi=150, bbox_inches='tight')
            plt.close()
        return f"Pie plot created   ::   x2_pie.png"
    except BaseException as e:
        return f"Pie plot not created, error :: {e}"


def main():
    """"""
    print(f"{Figlet(font='slant').renderText('X2 Plots')}")

    hp.create_necessary_directories(cf.IMAGES_DIR)  # First run

    df = load_plots_dataframe(cf.DB_PATH, cf.DB_NAME)
    df.set_index('draw_date', inplace=True, drop=True)

    functions = [gen_heatmap, gen_line_plot, gen_area_plot, gen_pie_plot]

    for fn in tqdm(functions, ncols=80):
        msg = fn(df)
        tqdm.write(msg)

    print(f"\nAll images were saved to this folder:\n{cf.IMAGES_DIR}\n")


if __name__ == "__main__":

    main()
