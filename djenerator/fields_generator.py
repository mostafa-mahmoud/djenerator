#!/usr/bin/env python
"""
This module has a function that matches django fields to the corresponding
random value generator.
"""
import base64
from django.conf import settings
from django.core.files.base import ContentFile
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
from django.db.models.fields.files import FieldFile
from django.db.models.fields.files import FileField
from django.db.models.fields.files import ImageField
from django.db.models.fields.files import ImageFieldFile
from values_generator import generate_big_integer
from values_generator import generate_boolean
from values_generator import generate_comma_separated_int
from values_generator import generate_date_time
from values_generator import generate_decimal
from values_generator import generate_email
from values_generator import generate_file_name
from values_generator import generate_file_path
from values_generator import generate_float
from values_generator import generate_int
from values_generator import generate_ip
from values_generator import generate_png
from values_generator import generate_positive_integer
from values_generator import generate_small_integer
from values_generator import generate_string
from values_generator import generate_text
from values_generator import generate_url
from values_generator import generate_uuid


def generate_random_values(field, size=50):
    """
    Generate a list of random values for a given field. The size of the output
    list might be less than 'size', if the total number of the possible values
    are less than 'size', like in Booleans.

    :param DjangoField field:
        A reference to the field to get values for.
    :param int size: The size of the output list.
    :rtype: List
    :returns: A list of random values generated for the given field.
    """
    return list(set([generate_random_value(field) for _ in xrange(size)]))


def generate_random_value(field):
    """
    Generate a random value for a given field, by matching to the corresponding
    random generator in values_generator.

    :param DjangoField field:
        A reference to the field to get values for.
    :returns: A random value generated for the given field.
    """
    if isinstance(field, BigIntegerField):
        return generate_big_integer()
    elif isinstance(field, EmailField):
        return generate_email(field.max_length)
    elif isinstance(field, BooleanField):
        return generate_boolean(field.null)
    elif isinstance(field, CommaSeparatedIntegerField):
        return generate_comma_separated_int(field.max_length)
    elif isinstance(field, DecimalField):
        return generate_decimal(field.max_digits, field.decimal_places)
    elif isinstance(field, DateTimeField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone)
    elif isinstance(field, DateField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone).date()
    elif isinstance(field, FloatField):
        return generate_float()
    elif isinstance(field, NullBooleanField):
        return generate_boolean(null_allowed=True)
    elif isinstance(field, PositiveSmallIntegerField):
        return abs(generate_small_integer())
    elif isinstance(field, PositiveIntegerField):
        return generate_positive_integer()
    elif isinstance(field, URLField):
        return generate_url(field.max_length)
    elif isinstance(field, BinaryField):
        length = field.max_length
        if not length:
            length = 100
        return buffer(base64.b64encode(generate_string(length)))
    elif isinstance(field, SlugField):
        return generate_string(field.max_length, special=['_', '-'])
    elif isinstance(field, TextField):
        return generate_text(field.max_length)
    elif isinstance(field, SmallIntegerField):
        return generate_small_integer()
    elif isinstance(field, TimeField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone).time()
    elif isinstance(field, IntegerField):
        return generate_int()
    elif isinstance(field, GenericIPAddressField):
        return generate_ip()
    elif isinstance(field, DurationField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        t1 = generate_date_time(tz=timezone)
        t2 = generate_date_time(tz=timezone)
        if t1 < t2:
            return t2 - t1
        else:
            return t1 - t2
    elif isinstance(field, CharField):
        return generate_string(field.max_length)
    elif isinstance(field, UUIDField):
        return generate_uuid()
    elif isinstance(field, FilePathField):
        return generate_file_path()
    elif isinstance(field, ImageField):
        name = generate_file_name(12, extension='png')
        image = generate_png()
        content = ContentFile(image)
        val = ImageFieldFile(content, field, name)
        val.save(name, content, False)
        return val
    elif isinstance(field, FileField):
        name = generate_file_name(12, extension='txt')
        txt = generate_text(field.max_length)
        content = ContentFile(txt)
        val = FieldFile(content, field, name)
        val.save(name, content, False)
        return val
