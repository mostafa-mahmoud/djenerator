#!/usr/bin/env python
"""
This module has a function that matches django fields to the corresponding
random value generator.
"""
from django.db.models.fields import BigIntegerField
from django.db.models.fields import BinaryField
from django.db.models.fields import BooleanField
from django.db.models.fields import CharField
from django.db.models.fields import CommaSeparatedIntegerField
from django.db.models.fields import DateField
from django.db.models.fields import DateTimeField
from django.db.models.fields import DecimalField
from django.db.models.fields import DurationField
from django.db.models.fields import EmailField
from django.db.models.fields import FilePathField
from django.db.models.fields import FloatField
from django.db.models.fields import GenericIPAddressField
from django.db.models.fields import IntegerField
from django.db.models.fields import NullBooleanField
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields import PositiveSmallIntegerField
from django.db.models.fields import SlugField
from django.db.models.fields import SmallIntegerField
from django.db.models.fields import TextField
from django.db.models.fields import TimeField
from django.db.models.fields import URLField
from django.db.models.fields import UUIDField
from values_generator import generate_big_integer
from values_generator import generate_boolean
from values_generator import generate_comma_separated_int
from values_generator import generate_date_time
from values_generator import generate_decimal
from values_generator import generate_email
from values_generator import generate_float
from values_generator import generate_int
from values_generator import generate_ip
from values_generator import generate_positive_integer
from values_generator import generate_small_integer
from values_generator import generate_string
from values_generator import generate_text


def generate_values(field, size=100):
    return list(set([generate_value(field) for _ in xrange(size)]))


def generate_value(field):
    if isinstance(field, BigIntegerField):
        return generate_big_integer()
    elif isinstance(field, EmailField):
        return generate_email(field.max_length)
    elif isinstance(field, BooleanField):
        return generate_boolean(field.null)
    elif isinstance(field, CommaSeparatedIntegerField):
        return generate_comma_separated_int(field.max_length)
    elif isinstance(field, DecimalField):
        return generate_decimal(32, 8)
    elif isinstance(field, DateTimeField):
        return generate_date_time()
    elif isinstance(field, DateField):
        return generate_date_time().date()
    elif isinstance(field, FloatField):
        return generate_float()
    elif isinstance(field, NullBooleanField):
        return generate_boolean(null_allowed=True)
    elif isinstance(field, PositiveIntegerField):
        return generate_positive_integer()
    elif isinstance(field, PositiveSmallIntegerField):
        return abs(generate_small_integer())
    elif isinstance(field, TextField):
        return generate_text(field.max_length)
    elif isinstance(field, SmallIntegerField):
        return generate_small_integer()
    elif isinstance(field, TimeField):
        return generate_date_time().time()
    elif isinstance(field, IntegerField):
        return generate_int()
    elif isinstance(field, GenericIPAddressField):
        return generate_ip()
    elif isinstance(field, DurationField):
        t1 = generate_date_time()
        t2 = generate_date_time()
        if t1 < t2:
            return t2 - t1
        else:
            return t1 - t2
    elif isinstance(field, CharField):
        return generate_string(field.max_length)
    elif isinstance(field, BinaryField):
        pass
    elif isinstance(field, URLField):
        pass
    elif isinstance(field, UUIDField):
        pass
    elif isinstance(field, SlugField):
        pass
    elif isinstance(field, FilePathField):
        pass
    # TODO(mostafa-mahmoud): ImageField, FileField
