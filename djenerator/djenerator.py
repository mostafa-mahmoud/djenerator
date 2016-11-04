#!/usr/bin/env python
"""
Module for the exportable functions for djenerator.
"""
from django.core import management
from django.db import connection
from generate_test_data import generate_test_data


def djenerator(app_path, size, output_file):
    """ djenerator
    Generates a sample data for all models in a given app
    and export the data to a .json file. If the file object given is None,
    then the data will be dumped in the current database. (A temporary database
    is created otherwise, while generating the data.)


    Args :
        app_path : A string that contains the path of the app.
        size : The number of models generated for each model in the models.
        output_file : A file object in which the data will be dumped.

    Returns:
        None

    """
    if output_file:
        db_name = connection.creation.create_test_db()
    generate_test_data(app_path + '.models', size)
    if output_file:
        management.call_command('dumpdata', app_path,
                                stdout=output_file, indent=2)
