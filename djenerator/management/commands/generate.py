#!/usr/bin/env python
from djenerator.generate_test_data import djenerator
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    args = '<size app_name output_name>'
    help = '''Generates random test data for an app using djenerator. The
              arguments of the command are `size app_name output_name` '''

    def add_arguments(self, parser):
        parser.add_argument('size')
        parser.add_argument('app_name')
        parser.add_argument('output_name')

    def handle(self, *args, **options):
        size = int(options['size'])
        app_name = options['app_name']
        output_name = options['output_name']
        output_file = open(output_name + '.json', 'w')
        djenerator(app_name, size, output_file)
        output_file.close()
