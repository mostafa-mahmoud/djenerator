#!/usr/bin/env python
"""
This module has utility functions for reading models and their fields.
"""
import inspect
import settings
from django.core.management import setup_environ

setup_environ(settings)

def is_instance_of_model(reference):
    """ Is instance of Model
    
    Tests if a given reference is a reference to a class that extends 
    django.db.models.Model
    
    Args : 
        reference : A given Anonymous reference.
    
    Returns :
        A boolean value that is true only if the given reference is a reference
        to a class.
    """
    if not inspect.isclass(reference):
        return False
    bases = ['%s.%s' % (b.__module__, b.__name__) for b 
            in inspect.getmro(reference)]
    return 'django.db.models.base.Model' in bases


