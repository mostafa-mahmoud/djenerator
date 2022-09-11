"""
This module has a function that matches django fields to the corresponding
random value generator.
"""
from django.conf import settings
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
    PositiveBigIntegerField,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    SlugField,
    SmallIntegerField,
    TextField,
    TimeField,
    URLField,
    UUIDField,
)
from django.db.models.fields.files import (
    FieldFile, FileField, ImageField, ImageFieldFile,
)

from .exceptions import SparseGeneratorError
from .utils import validate_data
from .values_generator import (
    generate_big_integer,
    generate_boolean,
    generate_comma_separated_int,
    generate_date_time,
    generate_decimal,
    generate_email,
    generate_file_name,
    generate_file_path,
    generate_float,
    generate_int,
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


def generate_random_field_values(
    field, gen_function, size: int, force_unique: bool = False, validators=[]
) -> list:
    """
    Generate a list of random values for a given field. The size of the output
    list might be less than 'size', if the total number of the possible values
    are less than 'size', like in Booleans.

    :param DjangoField field: A reference to the field to get values for.
    :param size: The size of the output list.
    :param force_unique: A flag to validate unique values.
    :param validators:
        A list of django validators to generated only valid values.
    :returns: A list of random values generated for the given field.
    """
    results = set([])
    fail = 0
    for _ in range(10 * size):
        value = gen_function()
        if (
            value is None or value in results or
            not validate_data(value, *validators)
        ):
            fail += 1
        else:
            results.add(value)
            fail = 0
        if len(results) >= size or fail >= 50:
            break
    if fail >= 50 and force_unique:
        raise SparseGeneratorError(
            f"{field.model.__name__}.{field.name} has generated very few "
            "valid values, but it must by a unique field"
        )
    return list(results)


def generate_random_value(field):
    """
    Generate a random value for a given field, by matching to the corresponding
    random generator in values_generator.

    :param DjangoField field: A reference to the field to get values for.
    :returns: A random value generated for the given field.
    """
    if isinstance(field, PositiveBigIntegerField):
        return generate_positive_big_integer()
    elif isinstance(field, BigIntegerField):
        return generate_big_integer()
    elif isinstance(field, EmailField):
        return generate_email(field.max_length)
    elif isinstance(field, (BooleanField, NullBooleanField)):
        return generate_boolean()
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
        return generate_string(length).encode()
        # return buffer(base64.b64encode(generate_string(length)))
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
    elif isinstance(field, IPAddressField):
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
