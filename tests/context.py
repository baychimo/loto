#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../loto')))

from loto import (
    core,
    helpers,
    config,
    x1_statistics,
    x2_plots,
    x3_oeis,
    x4_cpt_plus,
    x5_prophet,
    x6_serendipity
)
