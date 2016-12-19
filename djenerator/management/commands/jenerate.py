#!/usr/bin/env python
from djenerator.djenerator import djenerator
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = '<size app_name output_name>'
    help = '''Generates random test data for an app using djenerator. The
              arguments of the command are `size app_name output_name` '''

    def add_arguments(self, parser):
        parser.add_argument('size', type=int)
        parser.add_argument('app_name', type=str)
        parser.add_argument('output_name', type=str)
        parser.add_argument('--model_sizes', nargs='+')

    def handle(self, *args, **options):
        size = int(options['size'])
        app_name = options['app_name']
        output_name = options['output_name']
        output_file = open(output_name + '.json', 'w')
        parsed_sizes = []
        if 'model_sizes' in options.keys() and options['model_sizes']:
            parsed_sizes = map(lambda t: t.split(':'), options['model_sizes'])
        model_sizes = dict(map(lambda t: (t[0], int(t[1])), parsed_sizes))
        djenerator(app_name, size, output_file, **model_sizes)
        output_file.close()
