
import inspect
from importlib import import_module

from django.db.models import Model


def is_django_model_class(reference):
    """
    Tests if a given reference is a reference to a class extending
    django.db.models.Model

    :param reference: A given Anonymous reference.
    :rtype: bool
    """
    if not inspect.isclass(reference):
        return False
    return any(
        'django.db.models.base.Model' == '%s.%s' % (b.__module__, b.__name__)
        for b in inspect.getmro(reference)
    )


def is_required(field):
    """
    Check if a given field is required.

    :param DjangoField fields: A reference to the given field.
    :rtype: boolean
    """
    return not field.null


def field_type(field):
    """
    Retrieves the type of a given field.

    :param DjangoField field: A reference to the given field.
    :rtype: str
    :returns: The type of the field.
    """
    return field.get_internal_type()


def is_related(field):
    """
    Test if a given field is a related field.

    :param DjangoField field: A reference to the given field.
    :rtype: bool
    """
    return 'django.db.models.fields.related' in field.__module__


def is_unidirectional_related(field):
    """
    Test if a given field is a related field.

    :param DjangoField field: A reference to the given field.
    :rtype: bool
    """
    return is_related(field) and (
        field_type(field) in ["OneToOneField", "ForeignKey"]
    )


def dependencies(model_cls, strong_dependency=False):
    """
    Retrieves the models the must be generated before a given model.

    :param DjangoModel model: A reference to the class of the given model.

    :rtype: List
    :returns: list of references to the classes of the models.
    """
    return [
        get_related_model(field)
        for field in retrieve_fields(model_cls)
        if is_unidirectional_related(field) and (
            is_required(field) or strong_dependency
        )
    ]


def is_unique(field):
    """
    Test if a field requires unique values.

    :param DjangoField field: A reference to the given field.
    :rtype: bool
    """
    return field.unique or field.primary_key


def is_reverse_related(field):
    """
    Test if a given field is a reverse related field.

    :param DjangoField field: A reference to the given field.
    :rtype: boolean
    :returns:
        A boolean value that is true only if the field is reverse related.
    """
    return 'django.db.models.fields.reverse_related' in field.__module__


def field_name(field):
    return field.name


def is_auto_field(field):
    """
    Test if a given field is an Auto-Field.

    :param DjangoField field: A reference to the given field.
    :rtype: boolean
    """
    return (
        hasattr(field, 'get_internal_type') and field.get_internal_type() in [
            'AutoField', 'BigAutoField', 'SmallAutoField'
        ]
    )


def retrieve_models(*module_paths, keep_abstract=False):
    """
    Retrieve all django models from a given module.

    :param str module_paths: Multiple paths of the models modules.
    :param bool keep_abstact: A flag that decides filtering of abstract models.
    :rtype: List
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


def is_many_to_many_field(field):
    return is_related(field) and not is_unidirectional_related(field)


def retrieve_fields(model_cls):
    """
    Retrieves the fields of a given model.

    :param DjangoModel model: A reference to the class of a given model.
    :rtype: List(DjangoFieldClass)
    :returns: A list of references to the classes of fields of the given model.
    """
    fields = list(filter(
        lambda field: (
            not is_reverse_related(field) and not is_auto_field(field)  # and
            # (not is_related(field) or is_unidirectional_related(field))
        ),
        model_cls._meta._get_fields()
    ))
    """
    if (hasattr(model._meta, '_fields')
            and hasattr(model._meta, '_many_to_many')):
        fields = model._meta._fields() + model._meta._many_to_many()
    else:
        fields = model._fields
    """
    # If the inheritance is multi-table inheritence, the fields of
    # the super class(that should be inherited) will not appear
    # in fields, and they will be replaced by a OneToOneField to the
    # super class or ManyToManyField in case of a proxy model, so
    # this block of code will be replace the related field
    # by those of the super class.
    if Model != model_cls.__base__:
        clone = fields[:]  # [fld for fld in fields]
        for field in clone:
            if (
                is_related(field) and
                field_type(field) in ["OneToOneField", "ManyToManyField"] and
                field.rel.to in model_cls.__bases__ and
                field.rel.to != model_cls
            ):
                fields.remove(field)
                fields += filter(lambda x: not is_auto_field(x),
                                 retrieve_fields(field.rel.to))
    return fields


def retrieve_generators(module_path):
    try:
        # module =
        import_module(module_path)
        # module.getattr()
        return {}
    except ModuleNotFoundError:
        return {}


def names_of_fields(model_cls):
    """
    Retrieves the names of the fields of a given model.

    :param DjagoModel model: A reference to the class of a given model.
    :returns:
        A list of strings of the attributes' names of the field of
        the given model.
    """
    return [field.name for field in retrieve_fields(model_cls)]


def get_related_model(field):
    if hasattr(field, "related_model"):
        return field.related_model
