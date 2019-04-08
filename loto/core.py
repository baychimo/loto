#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command line interface wrapper to make running the different experiments and creating (first run)
or refreshing the database a little friendlier for the user.

Should be run as a standalone script, depending on how you installed it, e.g.::

    $ python loto/core.py
"""
import importlib
import sys
import warnings

import click


def lazy_load(slow_module):
    """Speed up CLI's perceived responsiveness by lazy loading modules.

    https://bugs.python.org/msg214954

    Args:
        slow_module(str): the module to load.
    """
    try:
        return sys.modules[slow_module]
    except KeyError:
        spec = importlib.util.find_spec(slow_module)
        module = importlib.util.module_from_spec(spec)
        loader = importlib.util.LazyLoader(spec.loader)
        loader.exec_module(module)
        return module


@click.group()
@click.option('-r', '--refresh', is_flag=True, help='Refresh database before running experiment')
@click.pass_context
def cli(ctx, refresh):
    """Command line interface to run experiments (stats and predictions) on lottery numbers

    Have fun!
    """
    ctx.ensure_object(dict)
    if refresh:
        get_data = lazy_load('get_data')
        get_data.main()
        ctx.obj['rf'] = refresh
    else:
        ctx.obj['rf'] = False


@cli.command()
@click.pass_context
def rf(ctx):
    """Create/refresh DB only"""
    if not ctx.obj['rf']:
        get_data = lazy_load('get_data')
        get_data.main()


@cli.command()
def x1():
    """Statistics with Dieharder & Ent"""
    x1 = lazy_load('x1_statistics')
    x1.main()


@cli.command()
def x2():
    """Plots with Matplotlib"""
    x2 = lazy_load('x2_plots')
    x2.main()


@cli.command()
def x3():
    """Checking "previous art" from OEIS (On-Line Encyclopedia of Integer Sequences)"""
    x3 = lazy_load('x3_oeis')
    x3.main()


@cli.command()
def x4():
    """Predictions made with a Compact Prediction Tree + (SPMF/Java)"""
    x4 = lazy_load('x4_cpt_plus')
    x4.main()


@cli.command()
def x5():
    """Predictions made with the Prophet library (FB)"""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        x5 = lazy_load('x5_prophet')
        x5.main()


@cli.command()
def x6():
    """Predictions made with different sources of randomness"""
    x6 = lazy_load('x6_serendipity')
    x6.main()


if __name__ == '__main__':

    cli()
