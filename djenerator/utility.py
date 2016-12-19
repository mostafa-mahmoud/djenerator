#!/usr/bin/env python
"""
This module contains utiltiy functions that are used in generating data.
"""
from django.db.models import Model
from model_reader import list_of_fields
from model_reader import names_of_fields


def unique_items(var_tuple):
    """
    Generate a function that can be used to check the uniqueness constraint.

    :param tuple var_tuple:
        A tuple of the names of the fields that should be unique together
    :rtype: function
    :returns:
        boolean function(variable, model, field):
            variable: A list of tuples in the form (field name, field value)
            model: A reference to the class of the given model.
            field: A reference to the class of the given field.
    """
    def uniqueness_constraint(variable, model, field):
        keys = dict(variable).keys()
        for key_name in var_tuple:
            if key_name not in keys:
                return True
        l = [(val, var) for (val, var) in variable if val in var_tuple]
        while model != Model and not model._meta.abstract:
            if list(model.objects.filter(**dict(l))):
                return False
            model = model.__base__
        return True

    return uniqueness_constraint


def sort_unique_tuple(var_tuple, model):
    """
    Sorts a tuple of names of a fields for a given model, in the order of
    which field comes first.

    :param tuple var_tuple:
        A tuple of strings of the names of some fields in the given model.
    :param DjangoModel model: A reference to the class of the given model.
    :rtype: tuple(str)
    :returns: A tuple of the names of the fields.
    """
    result = []
    fields = list_of_fields(model)
    for field in fields:
        if field.name in var_tuple:
            result.append(field.name)
    return tuple(result)


def sort_unique_tuples(var_tuples, model):
    """
    Sort lexicographically the tuples of fields according to what appears first
    in the model.

    :param var_tuples: a list of tuples of names of some fields.
    :type var_tuples: List(tuple(str))
    :param model: A reference to the class of the given model.
    :rtype: List(tuple(str))
    :returns: A list of tuples of names of some fields.
    """
    fields = names_of_fields(model)
    var_tuples = [sort_unique_tuple(var_tup, model) for var_tup in var_tuples]

    def cm(a, b):
        if not len(a) and not len(b):
            return 0
        elif not len(a):
            return -1
        elif not len(b):
            return 1
        if a[0] == b[0]:
            return cm(a[1:], b[1:])
        else:
            if fields.index(a[0]) < fields.index(b[0]):
                return -1
            else:
                return 1

    clone = var_tuples[:]
    clone.sort(cmp=cm)
    return tuple(clone)
