#!/usr/bin/env python
"""
Module for the exportable functions for djenerator.
"""
from django.core import management
from django.db import connection
from generate_test_data import generate_test_data


def djenerator(app_path, size, output_file, **size_options):
    """
    Generates a sample data for all models in a given app and exports the data
    to a json file. If the file object given is None, then the data will be
    dumped in the current database. (A temporary database is created otherwise,
    while generating the data.)

    :param str app_path: The path of the app.
    :param int size:
        The number of models generated for each model in the models.
    :param File output_file: A file in which the data will be dumped.
    :param dict size_options:
        A dictionary that maps str:model_name to int:model_size, which is the
        number of generated instances for the model.
        If a model isn't in size_options, then the default 'size' will be used.
    :rtype: None
    """
    if output_file:
        db_name = connection.creation.create_test_db()
    generate_test_data(app_path + '.models', size, **size_options)
    if output_file:
        management.call_command('dumpdata', app_path,
                                stdout=output_file, indent=2)
