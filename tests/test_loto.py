#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
I wanted to familiarize with the Hypothesis library. So...many tests are probably a little over the
top.

Run the tests like so to get more interesting info::

    pytest -v --durations=0 --hypothesis-show-statistics tests/
"""
import contextlib
import csv
import multiprocessing
import tempfile
import time
import zipfile
from unittest import mock

from hypothesis import given, settings, example
from hypothesis.extra.pandas import column, data_frames, range_indexes
import hypothesis.strategies as st
import pandas as pd
import pytest
import responses
from requests.exceptions import RequestException

from .context import *


###################################################################################################
# Shared / Common variables
###################################################################################################
numbers_fields = [f for f in config.TABLE_INFO['fields']['balls']] + \
                 [f for f in config.TABLE_INFO['fields']['stars']]

http_status_codes = [x for x in range(400, 452)] + [x for x in range(500, 512)]


###################################################################################################
# helpers
###################################################################################################
@mock.patch('os.makedirs')
def test_create_necessary_directories(mock_makedirs):
    helpers.create_necessary_directories(config.FILES_DIR)
    mock_makedirs.assert_called_once_with(config.FILES_DIR)


@mock.patch('os.makedirs')
@mock.patch('shutil.rmtree')
@responses.activate
def test_download_files_success(mock_rmtree, mock_makedirs):
    for url in config.URLS:
        responses.add(responses.GET, url, status=200)
    helpers.download_files(config.URLS, config.TMP_DL_DIR)
    mock_makedirs.assert_called_once_with(config.TMP_DL_DIR)


# Hypothesis does not work well with mock patches as decorators so we use context managers where
# both tools are needed
@given(status_code=st.sampled_from(http_status_codes))
@responses.activate
def test_download_files_error(status_code):
    for url in config.URLS:
        responses.add(
            responses.GET,
            url,
            status=status_code,
            body=RequestException(str(status_code))
        )

    with contextlib.ExitStack() as stack:
        mock_makedirs = stack.enter_context(mock.patch('os.makedirs'))
        stack.enter_context(mock.patch('shutil.rmtree'))
        stack.enter_context(pytest.raises(SystemExit))

        helpers.download_files(config.URLS, config.TMP_DL_DIR)

    mock_makedirs.assert_called_once_with(config.TMP_DL_DIR)


@mock.patch('os.walk')
def test_list_files(mock_walk):
    mock_walk.return_value = [('/x/y/z', ('z'), ('a.zip', 'b.zip')), ]

    files = helpers.list_files('dummy', '.zip')
    assert isinstance(files, list)
    assert files == ['/x/y/z/a.zip', '/x/y/z/b.zip']

    files = helpers.list_files('dummy', '.txt')
    assert isinstance(files, list)
    assert not files


@mock.patch.object(zipfile, 'ZipFile', autospec=True)
@mock.patch('os.walk')
def test_decompress_files(mock_walk, mock_zipfile):
    mock_walk.return_value = [('/x/y/z', ('z'), ('a.zip', 'b.zip')), ]
    helpers.decompress_files('dummy')
    calls = [mock.call('/x/y/z/a.zip', 'r'), mock.call('/x/y/z/b.zip', 'r')]
    mock_zipfile.assert_has_calls(calls, any_order=True)


def test_get_next_lottery_date():
    next_lottery_date = helpers.get_next_lottery_date()
    assert isinstance(next_lottery_date, pd.Timestamp)
    assert next_lottery_date > pd.Timestamp.now()


@mock.patch.object(csv, 'DictReader', autospec=True)
@mock.patch('builtins.open')
@mock.patch('os.walk')
def test_prepare_data(mock_walk, mock_open, mock_reader):
    mock_walk.return_value = [('/x/y/z', ('z'), ('a.csv', 'b.csv')), ]
    data = helpers.prepare_data('dummy')
    assert mock_reader.call_count == 2
    assert isinstance(data, list)


# Correct structure, column names and data type. Random values
@given(
    random_values=st.tuples(
        st.datetimes(),
        st.integers(),
        st.integers(),
        st.integers(),
        st.integers(),
        st.integers(),
        st.integers(),
        st.integers(),
    )
)
def test_prepare_data_clean(random_values):
    with open(config.TEST_FILES_DIR + 'random_data.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['date_de_tirage', 'boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5',
                         'etoile_1', 'etoile_2'])
        writer.writerow(random_values)

    data = helpers.prepare_data(config.TEST_FILES_DIR)
    assert isinstance(data, list)
    assert data


# Correct structure and column names. Wrong data types, random values
@given(
    random_values=st.tuples(
        st.datetimes(),
        st.integers(),
        st.text(alphabet=st.characters(blacklist_categories=('Cc', 'Cs', ))),
        st.integers(),
        st.floats(),
        st.integers(),
        st.emails(),
        st.integers(),
        st.integers(),                                       # Useless
        st.characters(blacklist_categories=('Cc', 'Cs', )),  # columns
        st.integers(),                                       # added
    )
)
def test_prepare_data_wrong_types(random_values):
    with open(config.TEST_FILES_DIR + 'random_data.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['date_de_tirage', 'boule_1', 'boule_2', 'boule_3', 'boule_4', 'boule_5',
                         'etoile_1', 'etoile_2'])
        writer.writerow(random_values)

    with pytest.raises(ValueError):
        data = helpers.prepare_data(config.TEST_FILES_DIR)
        assert not data


@given(
    numbers=st.lists(
        st.tuples(
            st.datetimes(),
            st.integers(min_value=1, max_value=99),
            st.integers(min_value=1, max_value=99),
            st.integers(min_value=1, max_value=99),
            st.integers(min_value=1, max_value=99),
            st.integers(min_value=1, max_value=99),
            st.integers(min_value=1, max_value=99),
            st.integers(min_value=1, max_value=99),
        ),
        min_size=1,
        max_size=100
    )
)
def test_load_db_clean(numbers):
    with contextlib.ExitStack() as stack:
        mock_makedirs = stack.enter_context(mock.patch('os.makedirs'))
        stack.enter_context(mock.patch('shutil.rmtree'))

        time.sleep(0.15)  # Avoid sqlite locks
        helpers.load_db(numbers, config.TEST_DB_PATH, config.TEST_DB_NAME)

    mock_makedirs.assert_called_once_with(config.TEST_DB_PATH)


@given(
    numbers=st.lists(
        st.tuples(
            st.datetimes(),
            st.characters(),
            st.integers(min_value=0, max_value=99),
            st.text(),
            st.integers(min_value=0, max_value=99),
            st.integers(min_value=0, max_value=99),
            st.integers(min_value=0, max_value=99),
            st.integers(min_value=0, max_value=99),
        ),
        min_size=1,
        max_size=100
    )
)
def test_load_db_wrong_type(numbers):
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch('os.makedirs'))
        stack.enter_context(mock.patch('shutil.rmtree'))
        stack.enter_context(pytest.raises(TypeError))
        stack.enter_context(pytest.raises(ValueError))

        time.sleep(0.15)  # Avoid sqlite locks
        helpers.load_db(numbers, config.TEST_DB_PATH, config.TEST_DB_NAME)


def test_get_numbers_as_columns():
    nbs_as_columns = helpers.get_numbers_as_columns(config.TEST_DB_PATH, config.TEST_DB_NAME)
    assert isinstance(nbs_as_columns, dict)
    assert any(nbs_as_columns.values()) is True
    for k, v in nbs_as_columns.items():
        assert any([
            k in config.TABLE_INFO['fields']['balls'],
            k in config.TABLE_INFO['fields']['stars']
        ])


def test_get_numbers_as_sequences():
    nbs_as_sequences = helpers.get_numbers_as_sequences(config.TEST_DB_PATH, config.TEST_DB_NAME)
    assert isinstance(nbs_as_sequences, dict)
    assert any(nbs_as_sequences.values()) is True
    for k, v in nbs_as_sequences.items():
        assert k in config.TABLE_INFO['fields']


###################################################################################################
# x1_statistics
###################################################################################################
@mock.patch('builtins.open')
def test_build_stats_tests_sets(mock_open):
    files = x1_statistics.build_stats_tests_sets(config.TEST_DB_PATH, config.TEST_DB_NAME)
    assert isinstance(files, list)
    assert len(files) == 9


@mock.patch('shutil.which')
def test_check_installed_tools(mock_which):
    test_tools = ['hammer', 'screwdriver', 'wrench']
    installed_tools = x1_statistics.check_installed_tools(test_tools)
    assert isinstance(installed_tools, list)
    assert installed_tools
    assert len(installed_tools) == 3
    calls = [mock.call(x) for x in test_tools]
    mock_which.assert_has_calls(calls, any_order=True)

    installed_tools = x1_statistics.check_installed_tools([])
    assert isinstance(installed_tools, list)
    assert not installed_tools


@mock.patch('subprocess.run')
def test_run_tools_known(mock_run):
    installed_tools = ['ent', 'dieharder']
    list_paths = x1_statistics.build_stats_tests_sets(config.TEST_DB_PATH, config.TEST_DB_NAME)
    x1_statistics.run_tools(installed_tools, list_paths)

    calls = []
    for path in list_paths:
        calls.extend([mock.call(['ent', '-c', path]), mock.call(['dieharder', '-a', '-f', path])])
    mock_run.assert_has_calls(calls, any_order=True)


@mock.patch('subprocess.run')
def test_run_tools_unknown(mock_run):
    installed_tools = ['hammer', 'screwdriver', 'wrench']
    list_paths = x1_statistics.build_stats_tests_sets(config.TEST_DB_PATH, config.TEST_DB_NAME)
    x1_statistics.run_tools(installed_tools, list_paths)
    mock_run.assert_not_called()


###################################################################################################
# x2_plots
###################################################################################################
def test_load_plots_dataframe():
    df = x2_plots.load_plots_dataframe(config.TEST_DB_PATH, config.TEST_DB_NAME)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@settings(max_examples=50)
@given(
    data_frames(
        index=range_indexes(min_size=5),
        columns=([
            column('draw_date', elements=st.datetimes(
                min_value=pd.Timestamp.min.to_pydatetime(),
                max_value=pd.Timestamp.max.to_pydatetime())
            ),
            column('ball_1', elements=st.integers(min_value=0, max_value=99)),
            column('ball_2', elements=st.integers(min_value=0, max_value=99)),
            column('ball_3', elements=st.integers(min_value=0, max_value=99)),
            column('ball_4', elements=st.integers(min_value=0, max_value=99)),
            column('ball_5', elements=st.integers(min_value=0, max_value=99)),
            column('star_1', elements=st.integers(min_value=0, max_value=99)),
            column('star_2', elements=st.integers(min_value=0, max_value=99))
        ])
    )
)
def test_gen_heatmap(data_frames):
    with contextlib.ExitStack() as stack:
        mock_plt_savefig = stack.enter_context(mock.patch('matplotlib.pyplot.savefig'))

        data_frames.set_index('draw_date', inplace=True, drop=True)
        x2_plots.gen_heatmap(data_frames)

    calls = [
        mock.call(
            config.IMAGES_DIR + 'x2_heatmap.png',
            dpi=150,
            bbox_inches='tight',
            pad_inches=-0.03
        )
    ]
    mock_plt_savefig.assert_has_calls(calls, any_order=True)


@settings(deadline=300, max_examples=50)
@given(
    data_frames(
        index=range_indexes(min_size=5),
        columns=([
            column('draw_date', elements=st.datetimes(
                min_value=pd.Timestamp.min.to_pydatetime(),
                max_value=pd.Timestamp.max.to_pydatetime())
            ),
            column('ball_1', elements=st.integers(min_value=0, max_value=99)),
            column('ball_2', elements=st.integers(min_value=0, max_value=99)),
            column('ball_3', elements=st.integers(min_value=0, max_value=99)),
            column('ball_4', elements=st.integers(min_value=0, max_value=99)),
            column('ball_5', elements=st.integers(min_value=0, max_value=99)),
            column('star_1', elements=st.integers(min_value=0, max_value=99)),
            column('star_2', elements=st.integers(min_value=0, max_value=99))
        ])
    )
)
def test_gen_line_plot(data_frames):
    with contextlib.ExitStack() as stack:
        mock_plt_savefig = stack.enter_context(mock.patch('matplotlib.pyplot.savefig'))

        data_frames.set_index('draw_date', inplace=True, drop=True)
        x2_plots.gen_line_plot(data_frames)

    calls = [mock.call(config.IMAGES_DIR + 'x2_line.png', dpi=150, bbox_inches='tight')]
    mock_plt_savefig.assert_has_calls(calls, any_order=True)


@settings(deadline=1000, max_examples=50)  # This one is longer because of subplots (I guess)
@given(
    data_frames(
        index=range_indexes(min_size=5),
        columns=([
            column('draw_date', elements=st.datetimes(
                min_value=pd.Timestamp.min.to_pydatetime(),
                max_value=pd.Timestamp.max.to_pydatetime())
            ),
            column('ball_1', elements=st.integers(min_value=0, max_value=99)),
            column('ball_2', elements=st.integers(min_value=0, max_value=99)),
            column('ball_3', elements=st.integers(min_value=0, max_value=99)),
            column('ball_4', elements=st.integers(min_value=0, max_value=99)),
            column('ball_5', elements=st.integers(min_value=0, max_value=99)),
            column('star_1', elements=st.integers(min_value=0, max_value=99)),
            column('star_2', elements=st.integers(min_value=0, max_value=99))
        ])
    )
)
def test_gen_area_plot(data_frames):
    with contextlib.ExitStack() as stack:
        mock_plt_savefig = stack.enter_context(mock.patch('matplotlib.pyplot.savefig'))

        data_frames.set_index('draw_date', inplace=True, drop=True)
        x2_plots.gen_area_plot(data_frames)

    calls = [mock.call(config.IMAGES_DIR + 'x2_area.png', dpi=150, bbox_inches='tight')]
    mock_plt_savefig.assert_has_calls(calls, any_order=True)


@settings(deadline=500, max_examples=50)
@given(
    data_frames(
        index=range_indexes(min_size=5),
        columns=([
            column('draw_date', elements=st.datetimes(
                min_value=pd.Timestamp.min.to_pydatetime(),
                max_value=pd.Timestamp.max.to_pydatetime())
            ),
            column('ball_1', elements=st.integers(min_value=0, max_value=99)),
            column('ball_2', elements=st.integers(min_value=0, max_value=99)),
            column('ball_3', elements=st.integers(min_value=0, max_value=99)),
            column('ball_4', elements=st.integers(min_value=0, max_value=99)),
            column('ball_5', elements=st.integers(min_value=0, max_value=99)),
            column('star_1', elements=st.integers(min_value=0, max_value=99)),
            column('star_2', elements=st.integers(min_value=0, max_value=99))
        ])
    )
)
def test_gen_pie_plot(data_frames):
    with contextlib.ExitStack() as stack:
        mock_plt_savefig = stack.enter_context(mock.patch('matplotlib.pyplot.savefig'))

        data_frames.set_index('draw_date', inplace=True, drop=True)
        x2_plots.gen_pie_plot(data_frames)

    calls = [mock.call(config.IMAGES_DIR + 'x2_pie.png', dpi=150, bbox_inches='tight')]
    mock_plt_savefig.assert_has_calls(calls, any_order=True)


###################################################################################################
# x3_oeis
###################################################################################################
def test_get_latest_draws():
    draws = x3_oeis.get_latest_draws(config.TEST_DB_PATH, config.TEST_DB_NAME, 10)
    assert isinstance(draws, list)
    assert draws
    assert len(draws) == 10
    for draw in draws:
        assert isinstance(draw, tuple)
        assert draw
        assert len(draw) == 7
        for number in draw:
            assert isinstance(number, int)
            assert number


def test_balls_by_draws():
    draws = x3_oeis.get_latest_draws(config.TEST_DB_PATH, config.TEST_DB_NAME, 10)
    urls = x3_oeis.balls_by_draws(draws)
    assert isinstance(urls, list)
    assert urls
    assert len(urls) == 10


@responses.activate
def test_check_sequences_oeis_success():
    draws = x3_oeis.get_latest_draws(config.TEST_DB_PATH, config.TEST_DB_NAME, 10)
    urls = x3_oeis.balls_by_draws(draws)
    for url in urls:
        responses.add(responses.GET, url, status=200, json={'results': 'All good Neo'})
    with mock.patch('helpers.spinning_cursor') as mock_spinning_cursor:
        x3_oeis.check_sequences_oeis(urls, 0)
    calls = [mock.call(0) for x in range(len(urls))]
    mock_spinning_cursor.assert_has_calls(calls, any_order=True)


@given(status_code=st.sampled_from(http_status_codes))
@responses.activate
def test_check_sequences_oeis_error(status_code):
    draws = x3_oeis.get_latest_draws(config.TEST_DB_PATH, config.TEST_DB_NAME, 10)
    urls = x3_oeis.balls_by_draws(draws)
    for url in urls:
        responses.add(
            responses.GET,
            url,
            status=status_code,
            json=None,
            body=RequestException(str(status_code))
        )

    with pytest.raises(SystemExit):
        x3_oeis.check_sequences_oeis(urls, 0)


###################################################################################################
# x4_cpt_plus
###################################################################################################
@mock.patch('builtins.open')
def test_build_cptp_data(mock_open):
    dict_nbs = x4_cpt_plus.build_cptp_data(config.TEST_DB_PATH, config.TEST_DB_NAME)
    assert isinstance(dict_nbs, dict)
    assert any(dict_nbs.values()) is True


@given(numbers=st.lists(st.integers(min_value=1, max_value=99), min_size=1))
def test_load_training_set_balls(loto_fixture, numbers):
    filepath = config.FILES_DIR + 'x4_data_set_seq_balls.txt'
    training_set = x4_cpt_plus.load_training_set(pytest.pkg, filepath, [])
    training_set_appended = x4_cpt_plus.load_training_set(pytest.pkg, filepath, numbers)
    assert len(str(training_set.getSequences())) < len(str(training_set_appended.getSequences()))
    assert isinstance(training_set, pytest.pkg.database.SequenceDatabase)


@given(numbers=st.lists(st.integers(min_value=1, max_value=99), min_size=1))
def test_load_training_set_stars(loto_fixture, numbers):
    filepath = config.FILES_DIR + 'x4_data_set_seq_stars.txt'
    training_set = x4_cpt_plus.load_training_set(pytest.pkg, filepath, [])
    training_set_appended = x4_cpt_plus.load_training_set(pytest.pkg, filepath, numbers)
    assert len(str(training_set.getSequences())) < len(str(training_set_appended.getSequences()))
    assert isinstance(training_set, pytest.pkg.database.SequenceDatabase)


@given(numbers=st.lists(st.integers(min_value=1, max_value=99), min_size=1))
def test_prepare_prediction_request(loto_fixture, numbers):
    sequence = x4_cpt_plus.prepare_prediction_request(pytest.pkg, numbers)
    assert sequence.size() == len(numbers)
    assert isinstance(sequence, pytest.pkg.database.Sequence)


@given(
    random_values=st.lists(
        st.lists(
            st.integers(min_value=1, max_value=99),
            min_size=2, max_size=5, unique=True
        ),
        min_size=30
    ),
    previous_numbers=st.lists(
        st.integers(min_value=1, max_value=99),
        min_size=2, max_size=5
    )
)
def test_make_predictions(loto_fixture, previous_numbers, random_values):
    with tempfile.NamedTemporaryFile(mode='w+') as tmpf:
        for draw in random_values:
            line = ' -1 '.join(map(str, draw)) + ' -1 -2\n'  # SPMF format
            tmpf.write(line)
        tmpf.seek(0)
        training_set = x4_cpt_plus.load_training_set(pytest.pkg, tmpf.name)
        pytest.prediction_model.Train(training_set.getSequences())
        numbers_list = x4_cpt_plus.make_predictions(
            pytest.pkg,
            pytest.prediction_model,
            previous_numbers
        )
    if 0 not in numbers_list:
        assert len(numbers_list) == len(previous_numbers)
    assert isinstance(numbers_list, list)


dict_nbs = st.fixed_dictionaries({
    'balls_draw_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_draw_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2),
    'balls_draw_m2':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_draw_m2':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2),
    'balls_predict_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_predict_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2),
    'balls_predict_next':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_predict_next':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2)
})


@given(dict_nbs)
def test_print_report_x4_friendly(dict_nbs):
    x4_cpt_plus.print_report(dict_nbs)


@given(
    dict_nbs=st.dictionaries(
        keys=st.text(),
        values=st.lists(
            st.tuples(
                st.integers(),
                st.integers()
            ),
            max_size=1
        )
    )
)
@example({})
def test_print_report_x4_hostile(dict_nbs):
    with pytest.raises(KeyError):  # We expect the script to crash in a nonsensical context
        x4_cpt_plus.print_report(dict_nbs)


def test_print_report_x4_wrong_type():
    with pytest.raises(TypeError):
        x4_cpt_plus.print_report([])


###################################################################################################
# x5_prophet
###################################################################################################
@given(field=st.sampled_from(numbers_fields))
def test_load_prophet_dataframe(field):
    df = x5_prophet.load_prophet_dataframe(config.TEST_DB_PATH, config.TEST_DB_NAME, field)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@given(
    data_frames(
        index=range_indexes(min_size=5),
        columns=([
            column('ds', elements=st.datetimes(
                min_value=pd.Timestamp.min.to_pydatetime(),
                max_value=pd.Timestamp.max.to_pydatetime())
            ),
            column('y', elements=st.floats(allow_nan=False))
        ])
    )
)
def test_generate_plots(data_frames):
    with contextlib.ExitStack() as stack:
        false_prophet = stack.enter_context(mock.patch('fbprophet.Prophet'))
        mock_plt_savefig = stack.enter_context(mock.patch('matplotlib.pyplot.savefig'))

        m = false_prophet()
        m.fit(data_frames)
        future = m.make_future_dataframe(periods=365)
        forecast = m.predict(future)
        x5_prophet.generate_plots(m, forecast, 'y')

    calls = [mock.call(config.IMAGES_DIR + 'x5_prophecy_y.png')]
    mock_plt_savefig.assert_has_calls(calls, any_order=True)


dict_nbs = st.fixed_dictionaries({
    'balls_draw_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_draw_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2),
    'balls_draw_m2':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_draw_m2':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2),
    'balls_predict_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_predict_m1':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2),
    'balls_predict_next':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
    'stars_predict_next':
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2)
})


@given(dict_nbs)
def test_print_report_x5_friendly(dict_nbs):
    x5_prophet.print_report(dict_nbs)


@given(
    dict_nbs=st.dictionaries(
        keys=st.text(),
        values=st.lists(st.integers(), max_size=1)
    )
)
@example({})
def test_print_report_x5_hostile(dict_nbs):
    with pytest.raises(KeyError):  # We expect the script to crash in a nonsensical context
        x5_prophet.print_report(dict_nbs)


def test_print_report_x5_wrong_type():
    with pytest.raises(TypeError):
        x5_prophet.print_report([])


###################################################################################################
# x6_serendipity
###################################################################################################
@responses.activate
def test_nist_beacon_success():
    responses.add(
        responses.GET,
        config.BEACON_LP_URL,
        status=200,
        json={
            'pulse': {
                'localRandomValue': 'AAABBBCCC'
            }
        }
    )
    dict_nbs = {}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    x6_serendipity.nist_beacon(config.BEACON_LP_URL, queue)
    dict_nbs = queue.get()
    # For a given seed we get a same deterministic result
    assert dict_nbs == {
        'prediction_nist_beacon': {
            'balls': [2, 32, 40, 44, 48],
            'stars': [4, 9]
        }
    }
    assert len(set(dict_nbs['prediction_nist_beacon']['balls'])) == 5
    assert len(set(dict_nbs['prediction_nist_beacon']['stars'])) == 2


@given(status_code=st.sampled_from(http_status_codes))
@responses.activate
def test_nist_beacon_error(status_code):
    responses.add(
        responses.GET,
        config.BEACON_LP_URL,
        status=status_code,
        json=None,
        body=RequestException(str(status_code))
    )
    dict_nbs = {}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    x6_serendipity.nist_beacon(config.BEACON_LP_URL, queue)
    dict_nbs = queue.get()
    assert dict_nbs == {
        'prediction_nist_beacon': {
            'balls': [0, 0, 0, 0, 0],
            'stars': [0, 0]
        }
    }
    assert len(set(dict_nbs['prediction_nist_beacon']['balls'])) == 1
    assert len(set(dict_nbs['prediction_nist_beacon']['stars'])) == 1


@responses.activate
def test_random_org_success():
    responses.add(
        responses.GET, config.RANDOM_ORG_URLS['balls'], status=200, body='2 32 40 44 48'
    )
    responses.add(
        responses.GET, config.RANDOM_ORG_URLS['stars'], status=200, body='4 9'
    )
    dict_nbs = {}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    x6_serendipity.random_org(config.RANDOM_ORG_URLS, queue)
    dict_nbs = queue.get()
    assert dict_nbs == {
        'prediction_random_org': {
            'balls': [2, 32, 40, 44, 48],
            'stars': [4, 9]
        }
    }
    assert len(set(dict_nbs['prediction_random_org']['balls'])) == 5
    assert len(set(dict_nbs['prediction_random_org']['stars'])) == 2


@given(status_code=st.sampled_from(http_status_codes))
@responses.activate
def test_random_org_error(status_code):
    responses.add(
        responses.GET,
        config.RANDOM_ORG_URLS['balls'],
        status=status_code,
        body=RequestException(str(status_code))
    )
    responses.add(
        responses.GET,
        config.RANDOM_ORG_URLS['stars'],
        status=status_code,
        body=RequestException(str(status_code))
    )
    dict_nbs = {}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    x6_serendipity.random_org(config.RANDOM_ORG_URLS, queue)
    dict_nbs = queue.get()
    assert dict_nbs == {
        'prediction_random_org': {
            'balls': [0, 0, 0, 0, 0],
            'stars': [0, 0]
        }
    }
    assert len(set(dict_nbs['prediction_random_org']['balls'])) == 1
    assert len(set(dict_nbs['prediction_random_org']['stars'])) == 1


@responses.activate
def test_anu_quantum_rng_success():
    responses.add(
        responses.GET,
        config.ANU_QRNG_URL,
        status=200,
        json={
            'data': ["0729facd2cb02bff338221efbdc501bd",
                     "fc339368d6b287d058a897a61483db01",
                     "c1a426cd2a5549d308fbe967375b40dc",
                     "924a38ebe5ea3119b41d9ae57749cba7",
                     "b4fb67e2a714d2422f4d3f50c29b7add",
                     "1520811d897242c87216d94f43346c82",
                     "60392fd1be3834cecba71f729d12b0ca"]
        }
    )
    dict_nbs = {}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    x6_serendipity.anu_quantum_rng(config.ANU_QRNG_URL, queue)
    dict_nbs = queue.get()
    print(dict_nbs)
    # For any given seeds we get same deterministic results
    assert dict_nbs == {
        'prediction_anu_qrng': {
            'balls': [12, 13, 31, 46, 48],
            'stars': [4, 7]
        }
    }
    assert len(set(dict_nbs['prediction_anu_qrng']['balls'])) == 5
    assert len(set(dict_nbs['prediction_anu_qrng']['stars'])) == 2


@given(status_code=st.sampled_from(http_status_codes))
@responses.activate
def test_anu_quantum_rng_error(status_code):
    responses.add(
        responses.GET,
        config.ANU_QRNG_URL,
        status=status_code,
        json=None,
        body=RequestException(str(status_code))
    )
    dict_nbs = {}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    x6_serendipity.anu_quantum_rng(config.ANU_QRNG_URL, queue)
    dict_nbs = queue.get()
    assert dict_nbs == {
        'prediction_anu_qrng': {
            'balls': [0, 0, 0, 0, 0],
            'stars': [0, 0]
        }
    }
    assert len(set(dict_nbs['prediction_anu_qrng']['balls'])) == 1
    assert len(set(dict_nbs['prediction_anu_qrng']['stars'])) == 1


def test_os_random():
    dict_nbs = {}
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    x6_serendipity.os_random(queue)
    dict_nbs = queue.get()
    assert len(set(dict_nbs['prediction_os_random']['balls'])) == 5
    assert len(set(dict_nbs['prediction_os_random']['stars'])) == 2


dict_nbs = st.fixed_dictionaries({
    'Q': st.fixed_dictionaries({
        'prediction_nist_beacon': st.fixed_dictionaries({
            'balls': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
            'stars': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2)
        }),
        'prediction_random_org': st.fixed_dictionaries({
            'balls': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
            'stars': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2)
        }),
        'prediction_anu_qrng': st.fixed_dictionaries({
            'balls': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
            'stars': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2)
        }),
        'prediction_os_random': st.fixed_dictionaries({
            'balls': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5),
            'stars': st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=2)
        })
    })
})


@given(dict_nbs)
def test_print_report_x6_friendly(dict_nbs):
    x6_serendipity.print_report(dict_nbs)


@given(
    dict_nbs=st.dictionaries(
        keys=st.text(),
        values=st.dictionaries(
            keys=st.text(),
            values=st.dictionaries(
                keys=st.text(),
                values=st.lists(
                    st.integers(),
                    max_size=1
                ), max_size=4
            ), max_size=10
        ), max_size=1
    )
)
@example({})
def test_print_report_x6_hostile(dict_nbs):
    with pytest.raises(KeyError):  # We expect the script to crash in a nonsensical context
        x6_serendipity.print_report(dict_nbs)


def test_print_report_x6_wrong_type():
    with pytest.raises(TypeError):
        x6_serendipity.print_report([])
