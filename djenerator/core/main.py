import logging
import math
import random

from django.db.utils import IntegrityError

from .algos import topological_sort
from .fields_generator import generate_random_field_values
from .utils import (
    dependencies,
    field_name,
    get_related_model,
    is_many_to_many_field,
    is_related,
    is_required,
    is_unique,
    retrieve_fields,
    retrieve_generators,
    retrieve_models,
)


logger = logging.getLogger('djenerator')


def generate_field_values(
    field, size, prev_generated, fill_null=True,
    generators={}, num_unique_constraints=0
):
    values = []
    gen_size = size * (int(math.sqrt(1000 * num_unique_constraints)) + 1)
    if field_name(field) in generators.keys():
        values = generators[field_name(field)](gen_size)
    elif is_related(field):
        related_model_cls = get_related_model(field)
        if related_model_cls.__name__ in prev_generated.keys():
            values = prev_generated[related_model_cls.__name__]
    else:
        values = generate_random_field_values(
            field, gen_size, is_unique(field)
        )
    # if num_unique_constraints > 0:
    #     logger.debug(f"{field.name} {len(values)}")

    if not fill_null and not is_required(field):
        values.append(None)

    if not values:
        return values
    elif is_unique(field):
        random.shuffle(values)  # choose without replacement
        return values[:size]
    else:
        return random.choices(values, k=size)  # choose with replacement


def generate_models(
    model_cls, size, prev_generated, generators={}, fill_null=True
):
    fields = retrieve_fields(model_cls)
    generated_dicts = {}
    recheck = []

    unique_together_counts = {}
    for tup in model_cls._meta.unique_together:
        for name in tup:
            num_constraints = unique_together_counts.get(name, 0) + 1
            unique_together_counts[name] = num_constraints

    for field in fields:
        if is_many_to_many_field(field):
            recheck.append(field)
            continue
        num_constraints = unique_together_counts.get(field_name(field), 0)
        values = generate_field_values(
            field, size, prev_generated,
            num_unique_constraints=num_constraints,
            generators=generators,
            fill_null=fill_null
        )
        if values:
            generated_dicts[field_name(field)] = values
            # print(field_name(field), "VALUES:", values)
            assert len(values) == size
        else:
            recheck.append(field)
    models = []
    for i in range(size):
        try:
            model = model_cls.objects.create(**{
                key: generated_dicts[key][i] for key in generated_dicts.keys()
            })
        except IntegrityError:  # as error:
            """
            for j in range(size):
                print({
                    key: generated_dicts[key][j]
                    for key in generated_dicts.keys()
                }, "\n")
            print("\n--------------------\n")
            for k, v in generated_dicts.items():
                print(k, "::", len(set(v)), set(v), "\n")
            """
            raise
        logger.info(f"generated Model {model.__class__.__name__} {model.pk}")
        models.append(model)
    return models, recheck


def postcompute(to_postcompute, generated, fill_null=True):
    for model_cls_name, fields in to_postcompute.items():
        models = generated[model_cls_name]
        for field in fields:
            values = generate_field_values(
                field, len(models), generated, fill_null=fill_null
            )
            if is_many_to_many_field(field):
                for model in models:
                    getattr(model, field_name(field)).add(*random.choices(
                        values, k=random.randint(1, min(5, len(values)))
                    ))
            else:
                for model, value in zip(models, values):
                    setattr(model, field_name(field), value)

        for model in models:
            model.save()


def generate_test_data(app_name, size, models_cls=None):
    """
    Generates a list of 'size' random data for each model in the models module
    in the given path, If the sample data is not enough for generating 'size'
    models, then all of the sample data will be used. If the models are
    inconsistent then no data will be generated. The data will be stored in
    a temporary database used for generation.

    :param str app_name: Name of the app
    :param int size: An integer that specifies the size of the generated data.
    :param dict size_options:
        A dictionary of that maps a str:model_name to int:model_size, that will
        be used as a size of the generated models. If a model is not in
        size_options then the default value 'size' will be used.
    :rtype: None
    """

    all_models = retrieve_models(app_name + ".models")
    generators = retrieve_generators(app_name + ".test_data")
    if models_cls is None:
        models_cls = all_models[:]
    else:
        names_map = dict(
            (model_cls.__name__, model_cls) for model_cls in all_models
        )
        models_cls = [names_map[model_cls] for model_cls in models_cls]
        # get all dependencies
        models_cls = list(set([
            dep for model_cls in models_cls for dep in dependencies(model_cls)
        ]))

    models_cls, cycle = topological_sort(models_cls, dependencies)
    if cycle:
        raise ValueError(
            "Detected cyclic dependencies between models. " +
            " -> ".join(map(str, cycle))
        )

    to_postcompute = {}
    generated = {}
    for model_cls in models_cls:
        models, recheck = generate_models(
            model_cls, size, generated, generators=generators
        )
        generated[model_cls.__name__] = models
        if recheck:
            to_postcompute[model_cls.__name__] = recheck

    postcompute(to_postcompute, generated)
