#!/usr/bin/env python
from djenerator.djenerator import djenerator
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    args = '<size app_name>'
    help = '''Generates random test data for an app using djenerator. The
              arguments of the command are `size app_name` '''

    def add_arguments(self, parser):
        parser.add_argument('size')
        parser.add_argument('app_name')

    def handle(self, *args, **options):
        size = int(options['size'])
        app_name = options['app_name']
        djenerator(app_name, size, None)
