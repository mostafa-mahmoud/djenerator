
import inspect
import random
from importlib import import_module

from django.core.exceptions import ValidationError


def is_django_model_class(cls) -> bool:
    """
    Tests if a given reference is a reference to a class extending
    django.db.models.Model

    :param reference: A given Anonymous reference.
    """
    if not inspect.isclass(cls):
        return False
    return any(
        'django.db.models.base.Model' == '%s.%s' % (b.__module__, b.__name__)
        for b in inspect.getmro(cls)
    )


def is_required(field) -> bool:
    """
    Check if a given field is required.

    :param DjangoField fields: A reference to the given field.
    """
    return not field.null


def field_type(field) -> str:
    """
    Retrieves the type of a given field.

    :param DjangoField field: A reference to the given field.
    """
    return field.get_internal_type()


def is_related(field) -> bool:
    """
    Test if a given field is a related field.

    :param DjangoField field: A reference to the given field.
    """
    return 'django.db.models.fields.related' in field.__module__


def is_unidirectional_related(field) -> bool:
    """
    Test if a given field is a related field.

    :param DjangoField field: A reference to the given field.
    """
    return is_related(field) and (
        field_type(field) in ["OneToOneField", "ForeignKey"]
    )


def dependencies(model_cls, strong_dependency: bool = False) -> list:
    """
    Retrieves the models the must be generated before a given model.

    :param DjangoModel model_cls: A reference to the class of the given model.
    :returns: list of references to the classes of the models.
    """
    return [
        get_related_model(field)
        for field in retrieve_fields(model_cls)
        if (
            is_unidirectional_related(field) and (
                is_required(field) or strong_dependency
            ) or (is_related(field) and strong_dependency)
        )
    ]


def is_unique(field) -> bool:
    """
    Test if a field requires unique values.

    :param DjangoField field: A reference to the given field.
    """
    return field.unique or field.primary_key


def is_reverse_related(field) -> bool:
    """
    Test if a given field is a reverse related field.

    :param DjangoField field: A reference to the given field.
    """
    return 'django.db.models.fields.reverse_related' in field.__module__


def field_name(field) -> str:
    """
    Get a name of django field.

    :param DjangoField field: A reference to the given field.
    """
    return field.name


def is_auto_field(field) -> bool:
    """
    Test if a given field is an Auto-Field.

    :param DjangoField field: A reference to the given field.
    """
    return (
        hasattr(field, 'get_internal_type') and field.get_internal_type() in [
            'AutoField', 'BigAutoField', 'SmallAutoField'
        ]
    )


def get_related_model(field):
    """
    Retrieve the class reference of the related model for a related field.

    :param DjangoField field: A reference to the given field.
    """
    if hasattr(field, "related_model"):
        return field.related_model


def is_many_to_many_field(field) -> bool:
    """
    Check if a given field is a ManyToMany relations field.

    :param DjangoField field: A reference to the given field.
    """
    return is_related(field) and not is_unidirectional_related(field)


def retrieve_models(*module_paths, keep_abstract: bool = False) -> list:
    """
    Retrieve all django models from a given module.

    :param str module_paths: Multiple paths of the models modules.
    :param keep_abstact: A flag that decides filtering of abstract models.
    :returns: A list of references to the classes of the models.
    """
    models = []
    for module_path in module_paths:
        models_module = import_module(module_path)
        models += list(filter(
            is_django_model_class, models_module.__dict__.values()
        ))
    if not keep_abstract:
        models = list(filter(lambda model: not model._meta.abstract, models))
    return models


def retrieve_fields(model_cls):
    """
    Retrieves the fields of a given model.

    :param DjangoModel model: A reference to the class of a given model.
    :rtype: List(DjangoFieldClass)
    :returns: A list of references to the classes of fields of the given model.
    """
    fields = list(filter(
        lambda field: (
            not is_reverse_related(field) and not is_auto_field(field) and
            not (
                is_related(field) and (
                    field_name(field) ==
                    get_related_model(field).__name__.lower() + "_ptr"
                )
            )
        ),
        model_cls._meta._get_fields()
    ))
    return fields
    # if (hasattr(model._meta, '_fields')
    #         and hasattr(model._meta, '_many_to_many')):
    #     fields = model._meta._fields() + model._meta._many_to_many()
    # else:
    #     fields = model._fields

    # If the inheritance is multi-table inheritence, the fields of
    # the super class(that should be inherited) will not appear
    # in fields, and they will be replaced by a OneToOneField to the
    # super class or ManyToManyField in case of a proxy model, so
    # this block of code will be replace the related field
    # by those of the super class.
    # if Model != model_cls.__base__:
    #     clone = fields[:]  # [fld for fld in fields]
    #     for field in clone:
    #         if (
    #             is_related(field) and
    #             field_type(field) in ["OneToOneField", "ManyToManyField"] and
    #             get_related_model(field) in model_cls.__bases__ and
    #             get_related_model(field) != model_cls
    #         ):
    #             fields.remove(field)
    #             # fields += filter(lambda x: not is_auto_field(x),
    #             #                  retrieve_fields(get_related_model(field)))


def retrieve_generators(module_path, models_names):
    """
    Retrieve the generator classes in test_data module in an app.
    """
    try:
        module = import_module(module_path)
        return {
            name: {
                k: v for k, v in getattr(module, name).__dict__.items()
                if not k.startswith("__") or not k.endswith("__")
            }
            for name in models_names if hasattr(module, name)
        }
    except ImportError:
        return {}
    except ModuleNotFoundError:
        return {}


def validate_data(value, *validators) -> bool:
    """
    Validate if a value satisfies the validators of a django field.
    """
    try:
        for validator in validators:
            validator(value)
    except ValidationError:
        return False
    return True


def make_generator(func):
    """
    Create an infinite generator out of a function returning random values.
    """
    while True:
        yield func()


def choices(lst: list, k: int = 1) -> list:
    """
    Select k random values randomly from a list.
    """
    if hasattr(random, "choices"):
        return random.choices(lst, k=k)
    else:
        return [random.choice(lst) for _ in range(k)]


def get_timezone(tz: str):
    """
    Get the timezone from the timezone.
    """
    try:
        import zoneinfo
        return zoneinfo.ZoneInfo(tz)
    except ImportError:
        try:
            from backports import zoneinfo
            return zoneinfo.ZoneInfo(tz)
        except Exception:
            import pytz
            return pytz.timezone(tz)
