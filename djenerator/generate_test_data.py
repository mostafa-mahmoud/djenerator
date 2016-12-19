#!/usr/bin/env python
"""
This file generates random test data from sample given data for
given models.
"""
import inspect
import os
import random
from django.db.models import Model
from fields_generator import generate_random_values
from model_reader import is_auto_field
from model_reader import is_related
from model_reader import is_required
from model_reader import is_reverse_related
from model_reader import list_of_fields
from model_reader import list_of_models
from model_reader import module_import
from model_reader import relation_type
from utility import sort_unique_tuples
from utility import unique_items


def field_sample_values(field):
    """
    Retrieves the list of sample values for a given field.

    :param DjangoField field: A reference to the class of the field.
    :rtype: List
    :returns: A list of sample values for the given field.
    """
    list_field_values = []
    if not is_auto_field(field):
        if is_reverse_related(field):
            # TODO(mostafa-mahmoud): Check if this case needs to be handled.
            pass
        elif is_related(field):
            model = field.rel.to
            list_field_values = list(model.objects.all())
            if 'ManyToMany' in relation_type(field) and list_field_values:
                siz = random.randint(1, len(list_field_values))
                list_field_values = [random.sample(list_field_values, siz)]
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
                        app_name = field.model._meta.app_label
                        path = '%s/TestTemplates/%s' % (app_name, input_method)
                        input_file = open(path, 'r')
                        list_field_values = [word[:-1] for word in input_file]
                    elif (isinstance(input_method, list)
                          or isinstance(input_method, tuple)):
                        list_field_values = input_method
                    else:
                        if inspect.isfunction(input_method):
                            list_field_values = input_method()
            if not found:
                app_name = field.model._meta.app_label
                path = '%s/TestTemplates/sample__%s__%s' % (app_name,
                       field.model.__name__, field.name)
                if os.path.exists(path):
                    input_file = open(path, 'r')
                    list_field_values = [word[:-1] for word in input_file]
                else:
                    list_field_values = generate_random_values(field)
    return list(list_field_values)


def dfs(instances, cur_tuple, index, to_be_computed, constraints,
        model, to_be_shuffled):
    """
    Value generator for the fields of a given model by simulating
    a depth first search. The model will be saved in a (temporary) database.

    The interface of the predicate should be:
        boolean predicate(cur_tuple, model, field)
         - cur_tuple: List of tuples of the filled values of the field being
                      filled, in the format (str:field_name , field_value).
         - model: A reference to the class of the given model.
         - field: A reference to the class of the field being generated

         The function should handle that the given tuple might be not full,
         and it should depend that the previously generated models are stored
         in the temporary database, and it should return a boolean value that's
         true only if the required constraint is satisfied.

    :param int instances:
        The target number of generated instances of the model.
    :param cur_tuple:
        A list of pairs str:field_name, field_value of the values of
        the filled fields.
    :type cur_tuple: List(pair(str, .))
    :param int index:
        The index of the field being filled in the list of fields.
    :param List to_be_computed:
        A list used for accumulation of the ignored fields.
    :param List constraints:
        A list of predicate functions that will constraint the output.
    :param DjangoModel model: A reference to the class of the given model.
    :param boolean to_be_shuffled:
        A boolean variable that will determine if the sample data
        will be shuffled or not.
    :rtype: None
    """
    fields = list_of_fields(model)
    if index >= len(fields):
        dfs.total += 1
        create_model(model, cur_tuple)
        return 1
    else:
        list_field_values = field_sample_values(fields[index])
        if not list_field_values:
            many_to_many_related = (is_related(fields[index]) and 'ManyToMany'
                                    in relation_type(fields[index]))
            optional_field = not is_required(fields[index])
            auto_fld = is_auto_field(fields[index])
            if many_to_many_related or optional_field or auto_fld:
                if not is_auto_field(fields[index]):
                    to_be_computed.append(fields[index])
                return dfs(instances, cur_tuple, index + 1, to_be_computed,
                           constraints, model, to_be_shuffled)
        else:
            if to_be_shuffled:
                random.shuffle(list_field_values)
            instances_so_far = 0
            for field_id, nxt_field in enumerate(list_field_values):
                new_tuple = cur_tuple[:]
                new_tuple.append((fields[index].name, nxt_field))
                are_constraints_satisfied = True
                for cons in constraints:
                    if not cons(new_tuple, model, fields[index]):
                        are_constraints_satisfied = False
                        break
                if are_constraints_satisfied:
                    instances_remaining = instances - instances_so_far
                    remaining_values = len(list_field_values) - field_id
                    value_instances = ((instances_remaining - 1 +
                                       remaining_values) / remaining_values)
                    new_instances = dfs(value_instances, new_tuple, index + 1,
                                        to_be_computed, constraints, model,
                                        to_be_shuffled)
                    instances_so_far += new_instances
                    if instances_so_far >= instances or dfs.total >= dfs.size:
                        return instances_so_far
            return instances_so_far


def generate_model(model, size, shuffle=None):
    """
    Generate 'size' sample models given a model and stores them in a temporary
    data base.

    :param DjangoModel model: A reference to the class of the given model.
    :param int size:
        An integer of the size of the sample models to be generated.
    :param boolean shuffle:
        An boolean to decide if the sample input will be shuffled or not.
        Shuffles by default.
    :rtype: tuple
    :returns:
        A tuple that contains a reference to the class of the given model,
        and list of field that's not computed.
    """
    unique_fields = [(field.name,) for field in list_of_fields(model)
                     if (hasattr(field, 'unique') and field.unique
                         and not is_auto_field(field))]
    unique_together = []
    if hasattr(model._meta, 'unique_together'):
        unique_together = list(model._meta.unique_together)
    unique = unique_together + unique_fields
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
    dfs.total = 0
    dfs(size, [], 0, to_be_computed, constraints, model, shuffle)
    return model, to_be_computed


def create_model(model, val):
    """
    Creates a new model given a reference to it's class and a list of
    the values of it's variables.

    :param DjangoModel model:
        A reference to the class of the model that will be created.
    :param val: A list of pairs having the format(field name, field value).
    :type val: tuple(pair(str, .))
    :returns: A model with the values given.
    """
    vals_dictionary = dict(val)
    have_many_to_many_relation = any(x for x in list_of_fields(model)
                                     if (is_related(x) and
                                         'ManyToMany' in relation_type(x)))
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
            if 'ManyToMany' not in dict_T[key]:
                setattr(mdl, key, val)
        mdl.save()
        for key, val in vals_dictionary.items():
            if 'ManyToMany' in dict_T[key]:
                for x in val:
                    getattr(mdl, key).add(x)
        mdl.save()
        return mdl


def dependencies(model):
    """
    Retrieves the models the must be generated before a given model.

    :param DjangoModel model: A reference to the class of the given model.

    :rtype: List
    :returns: list of references to the classes of the models.
    """
    fields = list_of_fields(model)
    return [field.rel.to for field in fields
            if (is_required(field) and (is_related(field)
                and 'ManyToMany' not in relation_type(field)))]


def topological_sort(models):
    """
    Sort a given list of models according to the dependencies of the
    relations between the models.

    :param List models:
        A list of references to the classes of the given models.
    :rtype: List
    :returns: A list of references to the classes of the given models.
    """
    result = []
    visited = []
    S = filter(dependencies, models)

    def visit(model):
        if model not in visited:
            visited.append(model)
            for dep_model in dependencies(model):
                visit(dep_model)
            result.append(model)

    while S:
        model = S.pop(0)
        visit(model)
    result_singleton = []
    for model in models:
        if model not in result:
            result_singleton.append(model)
    return result_singleton + result


def recompute(model, field):
    """
    Recompute the previously ignored fields in the models.

    :param DjangoModel model: A reference to the class of the given model.
    :param DjangoField field:
        A reference to the class of the non-computed field.
    :rtype: None
    """
    if is_related(field):
        models = model.objects.all()
        list_field_values = field_sample_values(field)
        random.shuffle(list_field_values)
        n = len(list_field_values)
        for index, mdl in enumerate(models):
            if ('ManyToMany' in relation_type(field) and
               not getattr(mdl, field.name).exists() or
               not is_required(field) and not getattr(mdl, field.name)):
                setattr(mdl, field.name, list_field_values[index % n])
                mdl.save()


def generate_test_data(app_models, size, **size_options):
    """
    Generates a list of 'size' random data for each model in the models module
    in the given path, If the sample data is not enough for generating 'size'
    models, then all of the sample data will be used. If the models are
    inconsistent then no data will be generated. The data will be stored in
    a temporary database used for generation.

    :param str app_models:
        A string that contains the path of the models module.
    :param int size: An integer that specifies the size of the generated data.
    :param dict size_options:
        A dictionary of that maps a str:model_name to int:model_size, that will
        be used as a size of the generated models. If a model is not in
        size_options then the default value 'size' will be used.
    :rtype: None
    """
    models = topological_sort(list_of_models(module_import(app_models)))
    to_be_computed = [generate_model(model,
                      (model.__name__ in size_options.keys()
                       and size_options[model.__name__]) or size,
                      True) for model in models]
    precomp = set([])
    for mdl, flds in to_be_computed:
        for fld in flds:
            if (mdl, fld.name) not in precomp:
                precomp.add((mdl, fld.name))
                recompute(mdl, fld)
