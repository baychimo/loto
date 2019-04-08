#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CPT+ - Use a Compact Prediction Tree Plus to predict the next winning numbers.

So many combinations are possible here. I made choices to limit the scope (what to put in and in
what form/shape/order).

Should be run from the CLI (depending on how you installed it), e.g.::

    $ python loto/core.py x4

But can also be run as a script::

    $ python loto/x4_cpt_plus.py
"""
import tempfile

import colorama
import jpype
from pyfiglet import Figlet
from tqdm import tqdm

import helpers as hp
import config as cf


def build_cptp_data(db_path, db_name):
    """Builds training sets files for the SPMF library.

    Training sets files created using the DB. A training set file in the format expected by the
    java SPMF library: ' -1 ' between each number within a sequence and ' -2' to end a sequence
    (see `SPMF/CPT+ docs <http://www.philippe-fournier-viger.com/spmf/CPTPlus.php>`_). The files
    are stored in the data/files folder.

    We keep the numbers from the two last lotteries out of the training sets, instead we return
    them as lists to build the prediction set (balls_draw_m2) and the verification set
    (balls_draw_m1). Same for stars numbers.

    Args:
        db_path(str): path to the directory where the DB is stored.
        db_name(str): name of the DB.

    Returns:
        dict: dictionary of lists {
            'paths'           : [strings],
            'balls_draw_m1'   : [ints],
            'balls_draw_m2'   : [ints],
            'stars_draw_m1'   : [ints],
            'stars_draw_m2'   : [ints]}
    """
    dict_nbs = {}
    # Numbers as sequence: every sequence is a row in the database. Either a row of 5 ball numbers
    # (1 file) or a row of 2 star numbers (another file).
    numbers_as_sequences = hp.get_numbers_as_sequences(db_path, db_name)
    for k, v in numbers_as_sequences.items():               # Inside the dict
        # Copy last and before-last numbers then delete them from list
        dict_nbs[k + '_draw_m1'] = v[-1:]
        del v[-1]
        dict_nbs[k + '_draw_m2'] = v[-1:]
        del v[-1]
        file_path = cf.FILES_DIR + 'x4_data_set_seq_' + k + '.txt'
        with open(file_path, 'w') as file:
            for iv in v:                                    # Inside the lists
                for iiv in iv:                              # Inside the tuples
                    file.write(str(iiv) + ' -1 ')
                file.write('-2\n')
        if 'paths' not in dict_nbs:
            dict_nbs['paths'] = {k: file_path}
        else:
            dict_nbs['paths'].update({k: file_path})

    # While sorting we remove one onion layer (the now redundant tuple layer returned by db)
    dict_nbs['balls_draw_m2'] = sorted(dict_nbs['balls_draw_m2'][0])
    dict_nbs['stars_draw_m2'] = sorted(dict_nbs['stars_draw_m2'][0])
    dict_nbs['balls_draw_m1'] = sorted(dict_nbs['balls_draw_m1'][0])
    dict_nbs['stars_draw_m1'] = sorted(dict_nbs['stars_draw_m1'][0])
    return dict_nbs


def load_training_set(pkg, path, numbers=[]):
    """Loads the training set file of training sequences.

    Either simply load a training set file (in the tree) as is, or load a training set file
    appended with an additional sequence.

    Args:
        pkg(jpype object): common root of the java package from which we load the classes we need.
        path(str): filepath to the training file to load.
        numbers(list): optional, number sequence(s) to append to training file.

    Returns:
        jpype object: training set object.
    """
    # Loading the java classes we need and instantiating the objects we will use
    # Training Set: this is the file we feed to the tree
    training_set_class = pkg.database.SequenceDatabase
    training_set = training_set_class()

    if numbers:
        with tempfile.NamedTemporaryFile(mode='w+') as tmpf:
            with open(path, 'r') as file:
                tmpf.write(file.read())
                new_line = ' -1 '.join(map(str, numbers)) + ' -1 -2\n'  # SPMF format
                tmpf.write(new_line)
                tmpf.seek(0)
                training_set.loadFileSPMFFormat(
                    jpype.JString(tmpf.name),
                    jpype.JInt(99999), jpype.JInt(0), jpype.JInt(99999)
                )
    else:
        training_set.loadFileSPMFFormat(
            jpype.JString(path),
            jpype.JInt(99999), jpype.JInt(0), jpype.JInt(99999)
        )

    return training_set


def prepare_prediction_request(pkg, numbers):
    """Turns a python list into a java sequence, in order to query for a prediction.

    Args:
        pkg(jpype object): common root of the java package from which we load the classes we need.
        numbers(list): the sequence of numbers to use as a query/arg for the prediction.

    Returns:
        jpype object: sequence of numbers in their java format.
    """
    # Loading the java classes we need and instantiating the objects we will use.
    sequence_class = pkg.database.Sequence
    sequence = sequence_class(jpype.JInt(0))
    item_class = pkg.database.Item
    integer_class = jpype.JClass('java.lang.Integer')

    for number in numbers:
        integer = integer_class(jpype.JInt(number))
        item = item_class(integer)
        sequence.addItem(item)

    return sequence


def make_predictions(pkg, prediction_model, previous_numbers):
    """Iterates over predictions until we get enough of them.

    Make predictions for a given sequence.

    Args:
        pkg(jpype object): common root of the java package from which we load the classes we need.
        prediction_model(jpype object): CPT+ java object trained, used here to make predictions.
        previous_numbers(list): number sequence for which we want a prediction.

    Returns:
        list: the predictions. A list of 5 numbers for the balls or a list of 2 for the stars.
    """
    # Loading the java classes we need and instantiating the objects we will use
    sequence_numbers = prepare_prediction_request(pkg, previous_numbers)
    sequence_class = pkg.database.Sequence
    item_class = pkg.database.Item
    integer_class = jpype.JClass('java.lang.Integer')

    # For emphasis, we tell the user when there is no prediction (prediction set to zero)
    nbtype = 'balls' if len(previous_numbers) > 2 else 'stars'

    numbers_set = set()
    for i in range(1, len(previous_numbers) + 1):
        old_len = len(numbers_set)
        new_len = 0
        # set() garanties no duplicates.
        # Keep on predicting until something is added to set or tree clueless
        while old_len >= new_len:
            prediction = prediction_model.Predict(sequence_numbers)
            try:
                p = int(str(prediction.get(jpype.JInt(0))))
            except jpype.JavaException:
                msg = f"CPT+ has no more prediction for this branch, prediction set to zero "\
                      f"for {nbtype}_{str(i)}"
                numbers_set.add(0)
                break
            integer = integer_class(jpype.JInt(p))  # Add last prediction p to input seq
            item = item_class(integer)
            sequence_numbers.addItem(item)
            prediction = sequence_class(jpype.JInt(0))  # Re-initialize prediction
            numbers_set.add(p)
            new_len = len(numbers_set)
        try:
            tqdm.write(colorama.Fore.RED + msg + colorama.Style.RESET_ALL)
        except BaseException:
            pass
    return list(numbers_set)


def print_report(dict_nbs):
    """Print DIY mini-table with predictions."""
    colorama.init()
    dash_line = 80 * "-"
    equal_line = 80 * "="
    gb = colorama.Back.GREEN
    rb = colorama.Back.RED
    rs = colorama.Style.RESET_ALL

    print(f"\n{gb}{equal_line}{rs}")
    print(f"{gb}| C O M P A C T   P R E D I C T I O N   T R E E  +{29 * ' '}|{rs}")

    # For historical purposes, the (-2) draw numbers used for the "validation prediction" of (-1)
    # numbers
    balls = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_draw_m2'])))
    stars = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_draw_m2'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{gb}| Numbers for draw (-2)          :      | {balls} |   | {stars} |{rs}")

    # For comparison & validation of the process, the numbers predicted by CPT+ for (-1) draw
    balls = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_predict_m1'])))
    stars = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_predict_m1'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{gb}| Prediction for draw (-1)       :      | {balls} |   | {stars} |{rs}")

    # For comparison & validation, the actual numbers of the latest draw (-1)
    balls = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_draw_m1'])))
    stars = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_draw_m1'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{gb}| Actual numbers for draw (-1)   :      | {balls} |   | {stars} |{rs}")

    # The winning numbers for next draw
    balls = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['balls_predict_next'])))
    stars = ''.join(' | '.join(map('{:02d}'.format, dict_nbs['stars_predict_next'])))
    print(f"{gb}{dash_line}{rs}")
    print(f"{rb}| Prediction for next draw       :      | {balls} |   | {stars} |{rs}")

    print(f"{gb}{equal_line}{rs}\n")


def main():
    """"""
    # Creating the needed datasets from the database, starting/shutting down JVM, loading the
    # prediction object from SPMF/CPT+ and iterating on training/predicting until we get our
    # winning numbers.

    print(f"{Figlet(font='slant').renderText('X4 Compact Prediction Tree +')}")

    # Creating the files we need for validation from DB, the set to predict and the set for
    # checking the prediction
    hp.create_necessary_directories(cf.FILES_DIR)  # First run
    dict_nbs = build_cptp_data(cf.DB_PATH, cf.DB_NAME)

    # Starting the Java Virtual Machine and passing it the java jar (lib) we want to load/use
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        '-ea',
        '-Djava.class.path=' + cf.ROOT_DIR + '/lib/spmf.jar'
    )

    # This is the part of the SPMF lib where the algorithm we want to use is located (CPT+)
    pkg = jpype.JPackage('ca').pfv.spmf.algorithms.sequenceprediction.ipredict

    # This is the main class: the prediction model
    optionalParameters = 'CCF:true CBS:true CCFmin:1 CCFmax:5 CCFsup:2 splitMethod:0 ' \
                         'splitLength:5 minPredictionRatio:1.0 noiseRatio:1'
    prediction_model_class = pkg.predictor.CPT.CPTPlus.CPTPlusPredictor
    prediction_model = prediction_model_class(
        jpype.JString('CPT+'),
        jpype.JString(optionalParameters)
    )

    # PREDICTIONS
    with tqdm(total=14, ncols=80) as pbar:
        # Validation: we try to predict draw[-1] from [-2] for which we already know the actual
        # draws
        training_set = load_training_set(pkg, dict_nbs['paths']['balls'])
        prediction_model.Train(training_set.getSequences())
        dict_nbs['balls_predict_m1'] = make_predictions(
            pkg,
            prediction_model,
            dict_nbs['balls_draw_m2']
        )
        dict_nbs['balls_predict_m1'].sort()
        pbar.update(5)

        training_set = load_training_set(pkg, dict_nbs['paths']['stars'])
        prediction_model.Train(training_set.getSequences())
        dict_nbs['stars_predict_m1'] = make_predictions(
            pkg,
            prediction_model,
            dict_nbs['stars_draw_m2']
        )
        dict_nbs['stars_predict_m1'].sort()
        pbar.update(2)

        # Now we try to predict the future
        training_set = load_training_set(
            pkg,
            dict_nbs['paths']['balls'],
            dict_nbs['balls_draw_m2']
        )
        prediction_model.Train(training_set.getSequences())
        dict_nbs['balls_predict_next'] = make_predictions(
            pkg,
            prediction_model,
            dict_nbs['balls_draw_m1']
        )
        dict_nbs['balls_predict_next'].sort()
        pbar.update(5)

        training_set = load_training_set(
            pkg,
            dict_nbs['paths']['stars'],
            dict_nbs['stars_draw_m2']
        )
        prediction_model.Train(training_set.getSequences())
        dict_nbs['stars_predict_next'] = make_predictions(
            pkg,
            prediction_model,
            dict_nbs['stars_draw_m1']
        )
        dict_nbs['stars_predict_next'].sort()
        pbar.update(2)

    print_report(dict_nbs)
    jpype.shutdownJVM()


if __name__ == '__main__':

    main()
