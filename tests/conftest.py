#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

import pytest
import jpype

from .context import *


def buildup():
    """Everything we need to do BEFORE the tests are run"""
    # Start a Java VM
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        '-ea',
        '-Djava.class.path=' + config.ROOT_DIR + '/lib/spmf.jar'
    )
    # Export the package and object which are needed in x4_cpt_plus.py
    pytest.pkg = jpype.JPackage('ca').pfv.spmf.algorithms.sequenceprediction.ipredict
    optionalParameters = 'CCF:true CBS:true CCFmin:1 CCFmax:5 CCFsup:2 splitMethod:0 ' \
                         'splitLength:5 minPredictionRatio:1.0 noiseRatio:1'
    prediction_model_class = pytest.pkg.predictor.CPT.CPTPlus.CPTPlusPredictor
    pytest.prediction_model = prediction_model_class(
        jpype.JString('CPT+'),
        jpype.JString(optionalParameters)
    )


def teardown():
    """Everything we need to do AFTER the tests are run"""
    try:
        os.remove(config.TEST_DB_PATH + config.TEST_DB_NAME)  # Delete the test database file
        os.remove(TEST_FILES_DIR + 'random_data.csv')         # Delete csv fake file
        jpype.shutdownJVM()                                   # Shut down the JVM
    except BaseException:
        pass


@pytest.fixture(scope='session', autouse=True)
def loto_fixture():
    buildup()
    yield
    teardown()
