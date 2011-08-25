#!/usr/bin/env python
"""
This module has utility functions for reading models and their fields.
"""
import inspect
import settings
from django.core.management import setup_environ
from django.db.models import Model

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


def list_of_models(models_module, keep_abstract=None):
    """ List of models
    
    This function filters the models from the instances in given module. 
    
    Args:
        models_module : A reference to a given models module.
        abstact(optional) : A boolean value that decides filtering of abstract
                            models.
                
    Returns:
        A list of reference to the classes of the models in 
        the imported models file.
    """
    models = filter(is_instance_of_model, models_module.__dict__.values())
    if keep_abstract:
        return models
    else:
        def is_not_abstract(model):
            return not model._meta.abstract

        return filter(is_not_abstract, models)


def list_of_fields(model):
    """ List of fields
    
    Retrieves the fields of a given model.
    
    Args:
        model : A reference to the class of a given model.
    
    Returns:
        A list of references to the fields of the given model.
    """
    fields = model._meta._fields() + model._meta._many_to_many()
    # If the inheritance is multi-table inheritence, the fields of 
    # the super class(that should be inherited) will not appear
    # in fields, and they will be replaced by a OneToOneField to the 
    # super class or ManyToManyField in case of a proxy model, so 
    # this block of code will be replace the related field
    # by those of the super class. 
    if Model != model.__base__:
        clone = [fld for fld in fields]
        for field in clone:
            if (is_related(field) and ('OneToOne' in relation_type(field) 
                or 'ManyToMany' in relation_type(field)) and (field.rel.to in 
                model.__bases__) and field.rel.to != model):
                fields.remove(field)
                fields += filter(lambda x : not is_auto_field(x),
                                 list_of_fields(field.rel.to))
    return fields


def names_of_fields(model):
    """ Names of fields
    
    Retrieves the names of the fields of a given model.
    
    Args : 
        model : A reference to the class of a given model.
    
    Returns :
        A list of strings of the attributes' names of the field of 
        the given model.
    """
    def get_name(s):
        return s.name
    
    return map(get_name, list_of_fields(model))


