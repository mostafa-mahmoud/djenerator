# Djenerator

Djenerator is a simple tool made to generate test/random data from the model descriptions of django.

## Installation

1. Using pip, you can install djenerator using this command:

```bash
$ pip3 install djenerator
```

2. Add `'djenerator'` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
   'django.contrib.admin',
   'django.contrib.auth',
   'django.contrib.contenttypes',
   'django.contrib.sessions',
   # ...
   'djenerator',
   # ...
]
```

## Usage

The generation of data can be done by a command using the `manage.py` file in your project:

```bash
$ python3 manage.py jenerate app_name size
```

Equivalently, this can be done within python code

```python
from djenerator import generate_test_data
generate_test_data(app_name, size)
```

### To generate for specific models

```bash
$ python3 manage.py jenerate app_name size --models ModelA ModelB ...
```

Equivalently, this can be done within python code

```python
from djenerator import generate_test_data
generate_test_data(app_name, size, models_cls=["ModelA", "ModelB"])
```

### To allow some null values

By default, djenerator generates data for all fields even if null values are allowed. To allow some null values, allow the following option:

```bash
$ python3 manage.py jenerate app_name size --allow-null
```

Equivalently, this can be done within python code

```python
from djenerator import generate_test_data
generate_test_data(app_name, size, allow_null=True)
```

## Writing your custom generators

You can add a customized values generator for a some fields in some models.
**This will most likely be required if you are writing your own validators.**
Writing your customized generator, can be done by adding a class to the module `{app_name}.test_data`:
1. Write a class with the same name as the model.
2. For the fields to write a custom generator, write an attirbute with a matching name, with the generator as a value.

The generator is either a function with no any required arguments that generates random values, or can also be an iterable of all possible values.

As an example, in an app `testapp`, if `testapp/models.py` is:

```python
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_mod91(value):
    if value % 91 != 0:
        raise ValidationError(
            _('%(value)s is not an even number'), params={'value': value},
        )


class TestModel(models.Model):
    field1 = models.CharField(max_length=256)
    field2 = models.BigIntegerField(validators=[validate_mod91])
    field3 = models.IntegerField()

    class Meta:
        unique_together = (('field1', 'field2'),)
```

then `testapp/test_data.py` will contain the following:

```python
import random

class TestModel:
    field2 = lambda: random.randint(1, 1000) * 91
    field3 = list(range(10000))
```

The value generator does not necessarily need to always generate unique or valid values, however, it should generate them with high probability.
In the example above, the `validate_mod91` checks if a number is divisible by 91, two bad generators can be:
1. `lambda: random.randint(0, 100000)` will generate valid values but with only 1% chance; however, a chance higher than 20% or even 50% would be much better.
1. `lambda: random.randint(0, 10) * 91` will generate only 11 unique valid values; however, it is recommended to return a factor higher than the total number of models to be generated (especially if there are `unique` or many `unique_together` constraints).


## Running the tests

Run the tests by running the command:

```bash
$ python3 manage.py test
```

The following combinations are tested:

| Django      | Python      | Status |
| ----------- | ----------- | ------ |
|    1.10.8   |     3.5     |   ✅   |
|    1.11.29  |     3.5     |   ✅   |
|    1.11.29  |     3.6     |   ✅   |
|    1.11.29  |     3.7     |   ✅   |
|    2.2.28   |     3.5     |   ✅   |
|    2.2.28   |     3.6     |   ✅   |
|    2.2.28   |     3.7     |   ✅   |
|    3.2.15   |     3.6     |   ✅   |
|    3.2.15   |     3.7     |   ✅   |
|    4.0.7    |     3.8     |   ✅   |
|    4.0.7    |     3.9     |   ✅   |
|    4.1.1    |     3.8     |   ✅   |
|    4.1.1    |     3.9     |   ✅   |

## Requirements

1. `django >= 1.10`.
1. `pytz` is required to be manually installed for `django < 1.11`, otherwise it is installed by django when it is required (it is not required for some higher versions of django).
1. `pillow` if ImageFields are used, we don't require it be default, but django will.

Our setup requires only `django`, other packages are reported by django.

## TODOs and BUGS

See: https://github.com/mostafa-mahmoud/djenerator/issues
