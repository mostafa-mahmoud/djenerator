#!/usr/bin/env python
"""
This file generates random test data from sample given data for
given models.
"""
import inspect
import random
import settings
from django.core import management
from django.core import serializers
from django.core.management import setup_environ
from django.db import connection
from django.db.models import Model
from model_reader import is_auto_field
from model_reader import is_related
from model_reader import list_of_fields
from model_reader import list_of_models
from model_reader import module_import
from model_reader import relation_type
from utility import sort_unique_tuples
from utility import unique_items

setup_environ(settings)

def field_sample_values(field):
    """ Field sample values
    
    Retrieves the list of sample values for a given field.
    
    Args : 
        field : a reference to the class of the field.
    
    Returns :
    a list of sample values for the given field.
    """
    list_field_values = []
    if not is_auto_field(field):
        if is_related(field):
            model = field.rel.to
            list_field_values = list(model.objects.all())
            if 'ManyToMany' in relation_type(field) and list_field_values:
                sz = random.randint(1, len(list_field_values))
                list_field_values = [random.sample(list_field_values, sz)]
        else:
            found = False
            if hasattr(field.model, 'TestData'):
                model = field.model
                while (model.__base__ != Model 
                       and not hasattr(model.TestData, field.name)):
                    model = model.__base__
                if field.name in model.TestData.__dict__.keys():
                    found = True
                    input_method = model.TestData.__dict__[field.name]
                    if isinstance(input_method, str):
                        input_file = open('TestTemplates/' + input_method, 'r')
                        list_field_values = [word[:-1] for word in input_file]
                    elif (isinstance(input_method, list) 
                          or isinstance(input_method, tuple)):
                        list_field_values = input_method
                    else:
                        if inspect.isfunction(input_method):
                            list_field_values = input_method()
            if not found:
                path = 'TestTemplates/sample__%s__%s' % (field.model.__name__,
                                                         field.name)
                input_file = open(path, 'r')
                list_field_values = [word[:-1] for word in input_file]
            # TODO(mostafa.amin93@gmail.com) : Generate totally randomized
            #                                  objects if the file is not found
    return list(list_field_values)


def dfs(cur_tuple, index, to_be_computed, constraints, model, to_be_shuffled):
    """ Depth first search
    
    Generates values for the fields of a given model by simulating
    a depth first search.
    
    Args : 
        cur_tuple : current tuple, a tuple of the values of the filled fields.
        index : the index of the field being filled in the list of fields.
        to_be_computed : A list used for accumulation of the ignored fields.
        constraints : a list of utility, that will constraint the output.
        model : a reference to the class of the given model.
        to_be_shuffled : A boolean variable that will determine if the sample
                         data will be shuffled or not.
    
    Returns:
        None
        
    The model will be saved in a temporary database.
            
    The interface of the predicate should be :        
        predicate(cur_tuple, model, field)
            where:
                - cur_tuple : list of tuples of the filled values of the field 
                              being filled, in the 
                              format (field name , field value).
                
                - model : a reference to the class of the given model.
                
                - field : A reference to the class of the field being generated.
         The function should handle that the given tuple might be not full, 
         and it should depend that the previously generated models are stored
         in the temporary database, and it should return a boolean value that's 
         true only if the required constraint is satisfied.
                
    """
    fields = list_of_fields(model)
    if dfs.size <= 0:
        return True
    if index >= len(fields):
        dfs.size -= 1
        create_model(model, cur_tuple)
    else:
        list_field_values = field_sample_values(fields[index])
        if not list_field_values:
            many_to_many_related = (is_related(fields[index]) and 'ManyToMany'
                                    in relation_type(fields[index]))
            optional_field = fields[index].null
            auto_fld = is_auto_field(fields[index])
            if many_to_many_related or optional_field or auto_fld:
                if not is_auto_field(fields[index]):
                    to_be_computed.append(fields[index])
                return dfs(cur_tuple, index + 1, to_be_computed,
                           constraints, model, to_be_shuffled)
        else:
            if to_be_shuffled:
                random.shuffle(list_field_values)
            for nxt_field in list_field_values:
                new_tuple = cur_tuple[:]
                new_tuple.append((fields[index].name, nxt_field))
                are_constraints_satisfied = True
                for cons in constraints:
                    if not cons(new_tuple, model, fields[index]):
                        are_constraints_satisfied = False
                        break
                if are_constraints_satisfied:
                    is_done = dfs(new_tuple, index + 1, to_be_computed, 
                                  constraints, model, to_be_shuffled)
                    if is_done:
                        return True


def generate_model(model, size, shuffle=None):
    """ Generate model
    
    Generate 'size' sample models given a model and stores them in a temporary
    data base.
    
    Args : 
        model : A reference to the class of the given model.
        size : An integer of the size of the sample models to be generated.
        shuffle : An optional boolean variable that will determine if the sample 
                  input will be shuffled or not.
    
    Returns : 
        A tuple that contains a reference to the class of the given model, 
        and list of field that's not computed.
    """
    unique_fields = [(f.name,) for f in list_of_fields(model) 
                     if f.unique and not is_auto_field(f)]
    unique_together = model._meta.unique_together
    unique = list(unique_together) + unique_fields
    unique = sort_unique_tuples(unique, model)
    unique_constraints = [unique_items(un_tuple) for un_tuple in unique]
    constraints = []
    if hasattr(model, 'Constraints'):
        constraints = model.Constraints.constraints
    constraints += unique_constraints
    if shuffle is None:
        shuffle = True
    to_be_computed = []
    dfs.size = size
    dfs([], 0, to_be_computed, constraints, model, shuffle)
    return model, to_be_computed


def create_model(model, val):
    """ Create models
    
    Creates a new model given a reference to it's class and a list of the values
    of it's variables.
    
    Args : 
        model : A reference to the class of the model that will be created.
        val : A list of tuples having the format (field name, field value)
    
    Returns :
        A model with the values given.
    """
    vals_dictionary = dict(val)
    have_many_to_many_relation = any([x for x in list_of_fields(model) 
                                       if is_related(x) 
                                       and 'ManyToMany' in relation_type(x)])
    if not have_many_to_many_relation:
        mdl = model(**vals_dictionary)
        mdl.save()
        return mdl
    else:
        mdl = model()
        flds = list_of_fields(model)
        dict_T = {}
        for field in flds:
            dict_T[field.name] = relation_type(field)
        for key, val in vals_dictionary.items():
            if not 'ManyToMany' in dict_T[key]:
                setattr(mdl, key, val)
        mdl.save()
        for key, val in vals_dictionary.items():
            if 'ManyToMany' in dict_T[key]:
                for x in val:
                    getattr(mdl, key).add(x)
        mdl.save()
        return mdl


def dependencies(model):
    """ Dependencies
    Retrieves the models the must be generated before a given model.
    
    Args : 
        model : a reference to the class of the given model.
    
    Returns :
        list of references to the classes of the models.
        
    """
    fields = list_of_fields(model)
    return [field.rel.to for field in fields 
            if ((not field.null) and (is_related(field) 
                and not 'ManyToMany' in relation_type(field)))]


def topological_sort(models):
    """ Topological sorting
    Sort a given list of models according to the dependencies of the 
    relations between the models.
    
    Args : 
        models : A list of references to the classes of the given models.
    
    Return :
        A list of references to the classes of the given models.
    """
    result = []
    visited = []
    S = filter(dependencies, models)
    def visit(model):
        if not model in visited:
            visited.append(model)
            for dep_model in dependencies(model):
                visit(dep_model)
            result.append(model)
            
    while S:
        model = S.pop(0)
        visit(model)
    result_singleton = []
    for model in models:
        if not model in result:
            result_singleton.append(model)
    return result_singleton + result


def recompute(model, field):
    """ recompute
    Recompute the ignored fields in the models.
    
    Args : 
        model : A reference to the class of the given model.
        field : A reference to the class of the non-computed field.
    
    Returns :
        None
    """
    if is_related(field):
        models = list(model.objects.all())
        list_field_values = field_sample_values(field)
        random.shuffle(list_field_values)
        n = len(list_field_values)
        for (index, mdl) in enumerate(models):
            if ('ManyToMany' in relation_type(field) and 
                not getattr(mdl, field.name).all() or
                field.null and not getattr(mdl, field.name)):
                setattr(mdl, field.name, list_field_values[index % n])
                mdl.save()


def generate_test_data(app_models, size):
    """ Generate test data
    Generates a list of 'size' random data for each model in the models module 
    in the given path, If the sample data is not enough for generating 'size'
    models, then all of the sample data will be used. If the models are 
    inconsistent then no data will be generated. The data will be stored in 
    a temporary database used for generation.
    
    Args:
        app_models : A string that contains the path of the models module.
        size : An integer that specifies the size of the generated data.
    
    Returns:
        None.
    """
    models = topological_sort(list_of_models(module_import(app_models)))
    to_be_computed = [generate_model(model, size) for model in models]
    precomp = set([]) 
    for mdlfld in to_be_computed:
        mdl = mdlfld[0]
        for fld in mdlfld[1]:
            if not (mdl, fld.name) in precomp:
                precomp.add((mdl, fld.name))
                recompute(mdl, fld)


def djenerator(app_path, size, output_file, printing=None):
    """ djenerator
    Generates a sample data for all models in a given app and export the data to
    a .json file.
    
    Args : 
        app_path : A string that contains the path of the app.
        size : The number of models generated for each model in the models.
        output_file : a file object in which the data will be dumped.
    
    Returns:
        None
    
    """
    db_name = connection.creation.create_test_db()
    generate_test_data(app_path + '.models', size)
    management.call_command("dumpdata", app_path, stdout=output_file)
    if printing:
        mdls = module_import(app_path + '.models')
        data_base = [mdl.objects.all() for mdl in list_of_models(mdls)]
        for mdls_ls in data_base:
            for mdl in mdls_ls:
                if hasattr(mdl, '__unicode__'):
                    print mdl.__unicode__()
                else:
                    print mdl


