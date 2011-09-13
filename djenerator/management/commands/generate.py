#!/usr/bin/env python
from djenerator.generate_test_data import djenerator
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    args = '<app_name size out_name>'
    help = 'Generates random test data'

    def handle(self, *args, **options):
        app_name = args[0]
        size = int(args[1])
        out_put_name = args[2]
        output_file = open(args[2] + '.json', 'w')
        djenerator(app_name, size, output_file)
        output_file.close()
