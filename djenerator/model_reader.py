#!/usr/bin/env python
"""
This module has utility functions for reading models and their fields.
"""
import inspect
from django.db.models import Model


def is_instance_of_django_model(reference):
    """
    Tests if a given reference is a reference to a class that extends
    django.db.models.Model

    :param reference: A given Anonymous reference.
    :rtype: boolean
    :returns:
        A boolean value that is true only if the given reference is a reference
        to a Model class.
    """
    if not inspect.isclass(reference):
        return False
    bases = ['%s.%s' % (b.__module__, b.__name__) for b
             in inspect.getmro(reference)]
    return 'django.db.models.base.Model' in bases


def is_required(field):
    """
    Test if a given field is required.

    :param DjangoField fields: A reference to the given field.
    :rtype: boolean
    :returns: A boolean value that is true only if the given field is required.
    """
    return not field.null


def is_related(field):
    """
    Test if a given field is a related field.

    :param DjangoField field: A reference to the given field.
    :rtype: boolean
    :returns: A boolean value that is true only if the given field is related.
    """
    return 'django.db.models.fields.related' in field.__module__


def is_reverse_related(field):
    """
    Test if a given field is a reverse related field.

    :param DjangoField field: A reference to the given field.
    :rtype: boolean
    :returns:
        A boolean value that is true only if the field is reverse related.
    """
    return 'django.db.models.fields.reverse_related' in field.__module__


def field_type(field):
    """
    Retrieves the type of a given field.

    :param DjangoField field: A reference to the given field.
    :rtype: str
    :returns: The type of the field.
    """
    return field.get_internal_type()


def is_auto_field(field):
    """
    Test if a given field is an Auto-Field.

    :param DjangoField field: A reference to the given field.
    :rtype: boolean
    :returns:
        A boolean value that's true only if the given field is an Auto-Field.
    """
    return (field.name == 'id' or
            hasattr(field, 'get_internal_type') and
            field.get_internal_type() == 'AutoField')


def relation_type(field):
    """
    Retrieves the type of the relation of a given related field.

    :param DjangoField field: A reference to the given field.
    :rtype: str
    :returns: A string that contains the type of the relation of the field.
    """
    return field.rel.__class__.__name__


def list_of_models(models_module, keep_abstract=None):
    """
    This function filters the models from the instances in given module.

    :param models_module: A reference to a given models' module.
    :param boolean keep_abstact:
        A boolean value that decides filtering of abstract models.
    :rtype: List
    :returns:
        A list of reference to the classes of the models in
        the imported models file.
    """
    models = filter(is_instance_of_django_model,
                    models_module.__dict__.values())
    if keep_abstract:
        return models
    else:

        def is_not_abstract(model):
            return not model._meta.abstract

        return filter(is_not_abstract, models)


def list_of_fields(model):
    """
    Retrieves the fields of a given model.

    :param DjangoModel model: A reference to the class of a given model.
    :rtype: List(DjangoFieldClass)
    :returns: A list of references to the classes of fields of the given model.
    """
    fields = list(model._meta._get_fields())
    fields = list(filter(lambda field: not is_reverse_related(field), fields))
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
    if Model != model.__base__:
        clone = [fld for fld in fields]
        for field in clone:
            if (is_related(field) and
               ('OneToOne' in relation_type(field) or
                'ManyToMany' in relation_type(field)) and
               (field.rel.to in model.__bases__) and field.rel.to != model):
                fields.remove(field)
                fields += filter(lambda x: not is_auto_field(x),
                                 list_of_fields(field.rel.to))
    return fields


def names_of_fields(model):
    """
    Retrieves the names of the fields of a given model.

    :param DjagoModel model: A reference to the class of a given model.
    :rtype: str
    :returns:
        A list of strings of the attributes' names of the field of
        the given model.
    """
    def get_name(s):
        return s.name

    return map(get_name, list_of_fields(model))


def module_import(app_path):
    """
    Imports a module in a given path.

    :param str app_path:
        A string that contains the path of the module and it's name.
    :returns: A reference to the module in the given path.
    """
    module = __import__(app_path)
    for part in app_path.split('.')[1:]:
        module = getattr(module, part)
    return module
