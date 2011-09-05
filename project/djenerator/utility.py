#!/usr/bin/env python
"""
This module contains utiltiy functions that are used in generating data.
"""
import settings
from django.core.management import setup_environ
from django.db import models
from django.db.models import Model

setup_environ(settings)

def unique_items(var_tuple):
    """ Unique items
    generate a function that can be used to check the uniqueness constraint.
    
    Args :
        var_tuple : A tuple of the names of the fields that should be unique 
                    together
    
    Returns :
        A function (variable, model, field);
            variable : A list of tuples in the form (field name, field value)
            model : A reference to the class of the given model.
            field : A reference to the class of the given field.
    
    """
    def uniqueness_constraint(variable, model, field):
        keys = dict(variable).keys()
        for key_name in var_tuple:
            if not key_name in keys:
                return True
        l = [(val, var) for (val, var) in variable if val in var_tuple]
        while model != Model and not model._meta.abstract:
            if bool(list(model.objects.filter(**dict(l)))):
                return False
            model = model.__base__
        return True
        
    return uniqueness_constraint


