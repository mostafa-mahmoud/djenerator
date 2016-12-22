==========
Djenerator
==========
Djenerator is a simple tool made to generate test/random data from the model description of django.

Installation
============
Using pip, you can install djenerator using this command:

.. code-block:: bash

   $ pip install djenerator

Usage
=====
Full documentation: http://pythonhosted.org/djenerator/usage.html

Add 'djenerator' to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'djenerator',
        ...
    )

The generation of data are then done by a command using manage.py file in your project:

.. code-block:: bash

   $ python manage.py jenerate size app_name output_file

There's another command that can be used for data generation, in this case the generated data will be dumped in the database:

.. code-block:: bash

   $ python manage.py jendb size app_name

Running the tests
=================
Run the tests by running the command:

.. code-block:: bash

   $ python runtests.py

TODOs and BUGS
==============
See: https://github.com/mostafa-mahmoud/djenerator/issues
