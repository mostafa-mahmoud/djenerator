#!/usr/bin/env python
"""
Copyright (c) Rob Hudson and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import django
import os
import sys
from os.path import dirname, abspath
from optparse import OptionParser

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        # HACK: this fixes our threaded runserver remote tests
        # DATABASE_NAME='test_sentry',
        # TEST_DATABASE_NAME='test_sentry',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',

            'djenerator',

            'tests',

            'example',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
        SITE_ID=1,
        TIME_ZONE='UTC',
        USE_TZ=True,
        BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        MEDIA_ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'media'),
    )

from django.test.runner import DiscoverRunner


def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests.tests']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    test_runner = DiscoverRunner(verbosity=kwargs.get('verbosity', 1),
                                 interactive=kwargs.get('interactive', False),
                                 failfast=kwargs.get('failfast'))
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--failfast', action='store_true',
                      default=False, dest='failfast')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
    django.setup()

    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, *args)
