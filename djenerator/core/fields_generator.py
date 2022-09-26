"""
This module has a function that matches django fields to the corresponding
random value generator.
"""
import json
import os
import random
import warnings

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
try:
    from django.db.models.fields.json import JSONField
except ImportError:
    JSONField = None
from django.db.models.fields.files import (
    FieldFile, FileField, ImageField, ImageFieldFile,
)
from django.utils.text import slugify

from .exceptions import InconsistentDefinition, SparseGeneratorError
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
    generate_json,
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
    results = []
    is_hashable = not (JSONField is not None and isinstance(field, JSONField))
    if is_hashable:
        results = set([])
    fail = 0
    for idx, value in enumerate(generator):
        if is_hashable and (
            value is None or value in results or
            not validate_data(value, *field.validators)
        ):
            fail += 1
        else:
            if is_hashable:
                results.add(value)
            else:
                results.append(value)
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


def extract_validator_args(field):
    clss = [
        validator.__name__ if validator.__class__.__name__ == "function" else
        validator.__class__.__name__ for validator in field._validators
    ]
    if len(clss) != len(set(clss)):
        raise InconsistentDefinition(
            "There are duplicate validators of the same type for %s.%s: %s" %
            (field.model.__name__, field.name, clss)
        )
    kwargs = {}
    for validator in field._validators:
        if isinstance(validator, validators.EmailValidator):
            kwargs["allowlist"] = list(set(
                (getattr(validator, "domain_allowlist", []) or []) +
                (getattr(validator, "domain_whitelist", []) or [])
            ))
        elif isinstance(validator, validators.URLValidator):
            kwargs["schemas"] = validator.schemes or []
        elif isinstance(validator, validators.MaxValueValidator):
            kwargs["mx"] = validator.limit_value
        elif isinstance(validator, validators.MinValueValidator):
            kwargs["mn"] = validator.limit_value
        elif isinstance(validator, validators.MaxLengthValidator):
            kwargs["max_length"] = validator.limit_value
        elif isinstance(validator, validators.MinLengthValidator):
            kwargs["min_length"] = validator.limit_value
        elif (
            hasattr(validators, "FileExtensionValidator") and
            isinstance(validator, validators.FileExtensionValidator)
        ):
            kwargs["extensions"] = validator.allowed_extensions
        elif isinstance(validator, validators.DecimalValidator):
            kwargs["max_digits"] = validator.max_digits
            kwargs["decimal_places"] = validator.decimal_places
            # kwargs["max_whole_digits"] = validator.max_whole_digits
        elif (
            hasattr(validators, "StepValueValidator") and
            isinstance(validator, validators.StepValueValidator)
        ):
            kwargs["step"] = validator.step_size
    if hasattr(field, "max_length") and field.max_length is not None:
        kwargs["max_length"] = field.max_length
    return kwargs


def generate_random_value(field):
    """
    Generate a random value for a given field, by matching to the corresponding
    random generator in values_generator.

    :param DjangoField field: A reference to the field to get values for.
    :returns: A random value generated for the given field.
    """
    kwargs = extract_validator_args(field)
    if (
        PositiveBigIntegerField is not None and
        isinstance(field, PositiveBigIntegerField)
    ):
        return generate_positive_big_integer(**kwargs)
    elif isinstance(field, BigIntegerField):
        return generate_big_integer(**kwargs)
    elif isinstance(field, PositiveSmallIntegerField):
        return abs(generate_small_integer(**kwargs))
    elif isinstance(field, PositiveIntegerField):
        return abs(generate_positive_integer(**kwargs))
    elif isinstance(field, SmallIntegerField):
        return generate_small_integer(**kwargs)
    elif isinstance(field, IntegerField):
        return generate_int(**kwargs)
    elif isinstance(field, (BooleanField, NullBooleanField)):
        return generate_boolean(**kwargs)
    elif (isinstance(field, EmailField) or
          validators.validate_email in field.validators or any(
              isinstance(v, validators.EmailValidator)
              for v in field.validators
          )):
        return generate_email(**kwargs)
    elif (isinstance(field, URLField) or any(
            isinstance(v, validators.URLValidator) for v in field.validators
          )):
        return generate_url(**kwargs)
    elif (
        validators.validate_ipv4_address in field.validators or
        (isinstance(field, GenericIPAddressField) and field.protocol == "IPv4")
    ):
        return generate_ip(v6=False)
    elif (
        validators.validate_ipv6_address in field.validators or
        (isinstance(field, GenericIPAddressField) and field.protocol == "IPv6")
    ):
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
        return generate_integer_list(**kwargs)
    elif isinstance(field, BinaryField):
        kwargs["max_length"] = field.max_length or 100
        return generate_string(**kwargs).encode()
    elif (
        isinstance(field, SlugField) or
        validators.validate_slug in field.validators or
        validators.validate_unicode_slug in field.validators
    ):
        return slugify(generate_string(special=['_', '-'], **kwargs))
    elif JSONField is not None and isinstance(field, JSONField):
        return generate_json(**kwargs)
    elif isinstance(field, TextField):
        return generate_text(**kwargs)
    elif (
        isinstance(field, DecimalField) or any(
            isinstance(v, validators.DecimalValidator)
            for v in field.validators
        )
    ):
        if hasattr(field, "max_digits"):
            kwargs["max_digits"] = field.max_digits
        if hasattr(field, "decimal_places"):
            kwargs["decimal_places"] = field.decimal_places
        return generate_decimal(**kwargs)
    elif isinstance(field, DateTimeField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone, **kwargs)
    elif isinstance(field, DateField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone, **kwargs).date()
    elif isinstance(field, FloatField):
        return generate_float(**kwargs)
    elif isinstance(field, TimeField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        return generate_date_time(tz=timezone, **kwargs).time()
    elif isinstance(field, DurationField):
        timezone = settings.USE_TZ and settings.TIME_ZONE
        t1 = generate_date_time(tz=timezone, **kwargs)
        t2 = generate_date_time(tz=timezone, **kwargs)
        if t1 < t2:
            return t2 - t1
        else:
            return t1 - t2
    elif isinstance(field, UUIDField):
        return generate_uuid()
    elif isinstance(field, FilePathField):
        return generate_file_path(**kwargs)
    elif any(
        isinstance(v, validators.RegexValidator) for v in field.validators
    ):
        # TODO: Handle this scenario with exrex package.
        if random.random() < 0.1:
            return generate_string(**kwargs)
        else:
            return generate_text(**kwargs)
    elif isinstance(field, CharField):
        if random.random() < 0.1:
            return generate_string(**kwargs)
        else:
            return generate_text(**kwargs)
    elif isinstance(field, ImageField):
        # extensions = {
        #     '.blp': 'BLP', '.bmp': 'BMP', '.dib': 'DIB', '.bufr': 'BUFR',
        #     '.cur': 'CUR', '.pcx': 'PCX', '.dcx': 'DCX', '.dds': 'DDS',
        #     '.ps': 'EPS', '.eps': 'EPS', '.fit': 'FITS', '.fits': 'FITS',
        #     '.fli': 'FLI', '.flc': 'FLI', '.ftc': 'FTEX', '.ftu': 'FTEX',
        #     '.gbr': 'GBR', '.gif': 'GIF', '.grib': 'GRIB', '.h5': 'HDF5',
        #    '.hdf': 'HDF5', '.png': 'PNG', '.apng': 'PNG', '.jp2': 'JPEG2000',
        #     '.j2k': 'JPEG2000', '.jpc': 'JPEG2000', '.jpf': 'JPEG2000',
        #     '.jpx': 'JPEG2000', '.j2c': 'JPEG2000', '.icns': 'ICNS',
        #     '.ico': 'ICO', '.im': 'IM', '.iim': 'IPTC', '.tif': 'TIFF',
        #     '.tiff': 'TIFF', '.jfif': 'JPEG', '.jpe': 'JPEG', '.jpg': 'JPEG',
        #     '.jpeg': 'JPEG', '.mpg': 'MPEG', '.mpeg': 'MPEG', '.mpo': 'MPO',
        #     '.msp': 'MSP', '.palm': 'PALM', '.pcd': 'PCD', '.pdf': 'PDF',
        #     '.pxr': 'PIXAR', '.pbm': 'PPM', '.pgm': 'PPM', '.ppm': 'PPM',
        #     '.pnm': 'PPM', '.psd': 'PSD', '.bw': 'SGI', '.rgb': 'SGI',
        #     '.rgba': 'SGI', '.sgi': 'SGI', '.ras': 'SUN', '.tga': 'TGA',
        #     '.icb': 'TGA', '.vda': 'TGA', '.vst': 'TGA', '.webp': 'WEBP',
        #     '.wmf': 'WMF', '.emf': 'WMF', '.xbm': 'XBM', '.xpm': 'XPM'
        # }
        extensions = [".png"]
        if "extensions" in kwargs.keys():
            extensions = kwargs["extensions"][:]
            del kwargs["extensions"]
            if ".png" not in extensions:
                raise NotImplementedError("Only PNG picture can be generated.")

        kwargs["width"] = field.width_field or 128
        kwargs["height"] = field.height_field or 128

        name = generate_file_name(12, extensions=[".png"])
        image = generate_png(**kwargs)

        content = ContentFile(image)
        val = ImageFieldFile(content, field, name)
        val.save(name, content, False)
        return val
    elif isinstance(field, FileField):
        warn = False
        if "extensions" in kwargs.keys():
            extensions = kwargs["extensions"][:]
            del kwargs["extensions"]
        else:
            extensions = [".txt", ".json"]
        if ".txt" in extensions and ".json" in extensions:
            extensions = [".txt", ".json"]
        elif ".txt" in extensions:
            extensions = [".txt"]
        elif ".json" in extensions:
            extensions = [".json"]
        else:
            warn = True
        name = generate_file_name(12, extensions=extensions)
        if warn:
            warnings.warn(
                "Native text (not following the file extension) is "
                "written in " + str(os.path.join(field.upload_to, name))
            )
        if name.endswith(".json"):
            txt = json.dumps(generate_json(**kwargs))
        else:
            txt = generate_text(**kwargs)
        content = ContentFile(txt)
        val = FieldFile(content, field, name)
        val.save(name, content, False)
        return val
