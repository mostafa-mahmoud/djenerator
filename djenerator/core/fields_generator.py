"""
This module has a function that matches django fields to the corresponding
random value generator.
"""
from django.conf import settings
from django.core import validators
from django.core.files.base import ContentFile
from django.db.models.fields import (
    BigIntegerField,
    BinaryField,
    BooleanField,
    CharField,
    CommaSeparatedIntegerField,
    DateField,
    DateTimeField,
    DecimalField,
    DurationField,
    EmailField,
    FilePathField,
    FloatField,
    GenericIPAddressField,
    IntegerField,
    IPAddressField,
    NullBooleanField,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    SlugField,
    SmallIntegerField,
    TextField,
    TimeField,
    URLField,
    UUIDField,
)
try:
    from django.db.models.fields import PositiveBigIntegerField
except ImportError:
    PositiveBigIntegerField = None
from django.db.models.fields.files import (
    FieldFile, FileField, ImageField, ImageFieldFile,
)

from .exceptions import SparseGeneratorError
from .utils import is_unique, validate_data
from .values_generator import (
    generate_big_integer,
    generate_boolean,
    # generate_comma_separated_int,
    generate_date_time,
    generate_decimal,
    generate_email,
    generate_file_name,
    generate_file_path,
    generate_float,
    generate_int,
    generate_integer_list,
    generate_ip,
    generate_png,
    generate_positive_big_integer,
    generate_positive_integer,
    generate_small_integer,
    generate_string,
    generate_text,
    generate_url,
    generate_uuid,
)


def generate_random_field_values(field, generator, size: int) -> list:
    """
    Generate a list of random values for a given field. The size of the output
    list might be less than 'size', if the total number of the possible values
    are less than 'size', like in Booleans. The given generator can be an
    iterator over a list, or a generator that generates random (possibly
    repetitive) values. The generator must always yield a "valid" value with
    high probability, otherwise it will raise a SparseGeneratorException if
    it fails frequently (50 times in a row); valid here means non-repetitive
    values that satisfies the validator of the django field.

    :param DjangoField field: A reference to the field to get values for.
    :param generator: A generator that generates a set of values.
    :param size: The size of the output list.
    :returns: A list of random values generated for the given field.
    """
    results = set([])
    fail = 0
    for idx, value in enumerate(generator):
        if (
            value is None or value in results or
            not validate_data(value, *field.validators)
        ):
            fail += 1
        else:
            results.add(value)
            fail = 0
        if len(results) >= size or fail >= 50 or idx >= 10 * size:
            break
    if fail >= 50 and is_unique(field):
        raise SparseGeneratorError(
            ("%s.%s has generated very few valid values"
             ", but it must by a unique field.") %
            (field.model.__name__, field.name)
        )
    return list(results)


def generate_random_value(field):
    """
    Generate a random value for a given field, by matching to the corresponding
    random generator in values_generator.

    :param DjangoField field: A reference to the field to get values for.
    :returns: A random value generated for the given field.
    """
    if (
        PositiveBigIntegerField is not None and
        isinstance(field, PositiveBigIntegerField)
    ):
        return generate_positive_big_integer()
    elif isinstance(field, BigIntegerField):
        return generate_big_integer()
    elif isinstance(field, PositiveSmallIntegerField):
        return abs(generate_small_integer())
    elif isinstance(field, PositiveIntegerField):
        return generate_positive_integer()
    elif isinstance(field, SmallIntegerField):
        return generate_small_integer()
    elif isinstance(field, IntegerField):
        return generate_int()
    elif isinstance(field, (BooleanField, NullBooleanField)):
        return generate_boolean()
    elif (isinstance(field, EmailField) or
          validators.validate_email in field.validators or any(
              isinstance(v, validators.EmailValidator)
              for v in field.validators
          )):
        return generate_email(field.max_length)
    elif (isinstance(field, URLField) or any(
            isinstance(v, validators.URLValidator) for v in field.validators
          )):
        return generate_url(field.max_length)
    elif validators.validate_ipv4_address in field.validators:
        return generate_ip(v6=False)
    elif validators.validate_ipv6_address in field.validators:
        return generate_ip(v4=False)
    elif (isinstance(field, (GenericIPAddressField, IPAddressField)) or
          validators.validate_ipv46_address in field.validators):
        return generate_ip()
    elif (
        isinstance(field, CommaSeparatedIntegerField) or
        validators.validate_comma_separated_integer_list in field.validators or
        validators.int_list_validator in field.validators
    ):
        # return generate_comma_separated_int(field.max_length)
        return generate_integer_list(field.max_length)
    elif isinstance(field, BinaryField):
        return generate_string(field.max_length or 100).encode()
    elif (
        isinstance(field, SlugField) or
        validators.validate_slug in field.validators or
        validators.validate_unicode_slug in field.validators
    ):
        return generate_string(field.max_length, special=['_', '-'])
    elif isinstance(field, TextField):
        return generate_text(field.max_length)
    elif (
        isinstance(field, DecimalField) or any(
            isinstance(v, validators.DecimalValidator)
            for v in field.validators
        )
    ):
        return generate_decimal(field.max_digits, field.decimal_places)
    elif isinstance(field, DateTimeField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone)
    elif isinstance(field, DateField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone).date()
    elif isinstance(field, FloatField):
        return generate_float()
    elif isinstance(field, TimeField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone).time()
    elif isinstance(field, DurationField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        t1 = generate_date_time(tz=timezone)
        t2 = generate_date_time(tz=timezone)
        if t1 < t2:
            return t2 - t1
        else:
            return t1 - t2
    elif isinstance(field, UUIDField):
        return generate_uuid()
    elif isinstance(field, FilePathField):
        return generate_file_path()
    elif any(
        isinstance(v, validators.RegexValidator) for v in field.validators
    ):
        # TODO: Handle this scenario with exrex package.
        return generate_string(field.max_length)
    elif isinstance(field, CharField):
        return generate_string(field.max_length)
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
