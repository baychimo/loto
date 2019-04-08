#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from unittest import mock
import json
# import os
# import shutil
import pytest
import tempfile
import multiprocessing
# import time
# import pandas as pd
# # import zipfile
# import contextlib
# import pytest
# from fbprophet import Prophet
from hypothesis import given, settings, example
# from hypothesis.extra.pandas import column, data_frames, range_indexes
# from hypothesis.extra.numpy import datetime64_dtypes
import hypothesis.strategies as st
import responses
from requests.exceptions import RequestException
from .context import *


http_status_codes = [x for x in range(400, 452)] + [x for x in range(500, 512)]


# @given(
#     dict_nbs=st.dictionaries(
#         keys=st.text(),
#         values=st.dictionaries(
#             keys=st.text(),
#             values=st.dictionaries(
#                 keys=st.text(),
#                 values=st.lists(
#                     st.integers(),
#                     max_size=1
#                 ), max_size=4
#             ), max_size=10
#         ), max_size=1
#     )
# )
# @example({})
# def test_print_report_x6_hostile(dict_nbs):
#     with pytest.raises(KeyError):  # We expect the script to crash in a nonsensical context
#         x6_serendipity.print_report(dict_nbs)
