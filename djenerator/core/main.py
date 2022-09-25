import functools
import inspect
import logging
import math
import random

from django.db.utils import IntegrityError

from .algos import topological_sort
from .exceptions import InvalidGenerator
from .fields_generator import (
    generate_random_field_values, generate_random_value
)
from .utils import (
    choices,
    dependencies,
    field_name,
    get_related_model,
    is_many_to_many_field,
    is_related,
    is_required,
    is_unique,
    make_generator,
    retrieve_fields,
    retrieve_generators,
    retrieve_models,
)


logger = logging.getLogger(__name__)


def generate_field_values(
    field, size: int, prev_generated: dict, allow_null: bool = False,
    generators: dict = {}, num_unique_constraints: int = 0
) -> list:
    """
    Generate a list of values for a given field.

    :param field: A Django Field.
    :param size: The number of values to generate.
    :param prev_generated: A dictionary of previously generated_values.
    :param allow_null: Allow null values to appear.
    :param generators:
        A dictionary containing generator function imported from the
        test_data module.
    :param num_unique_constraints:
        Number of unique_together constraints in the model including
        the given field.
    """
    gen_function = make_generator(
        functools.partial(generate_random_value, field)
    )
    values = []
    gen_size = size * (int(math.sqrt(1000 * num_unique_constraints)) + 1)
    if field_name(field) in generators.keys():
        iterator = generators[field_name(field)]
        if hasattr(iterator, "__iter__"):
            gen_function = iterator.__iter__()
        else:
            sign = inspect.signature(iterator)
            if [
                p.kind for p in sign.parameters.values()
                if p.kind not in [p.KEYWORD_ONLY, p.VAR_KEYWORD]
            ]:
                raise InvalidGenerator(
                    ("The generator for %s.%s has some required arguments"
                     ", which can't be given.") %
                    (field.model.__name__, field.name)
                )

            gen_function = make_generator(iterator)

    if is_related(field):
        related_model_cls = get_related_model(field)
        if related_model_cls.__name__ in prev_generated.keys():
            values = prev_generated[related_model_cls.__name__]
    else:
        values = generate_random_field_values(field, gen_function, gen_size)

    if allow_null and not is_required(field):
        values.append(None)

    if not values:
        return values
    elif is_unique(field):
        assert len(set(values)) >= size, len(set(values))
        random.shuffle(values)  # choose without replacement
        return values[:size]
    else:
        return choices(values, k=size)  # choose with replacement


def generate_models(
    model_cls, size: int, prev_generated: dict = {}, generators: dict = {},
    allow_null: bool = False
) -> tuple:
    """
    Generate a set of instances of a given model class.
    """
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
            generators=generators.get(model_cls.__name__, {}),
            allow_null=allow_null
        )
        if values:
            generated_dicts[field_name(field)] = values
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
            kwargs = {
                key: generated_dicts[key][i] for key in generated_dicts.keys()
            }
            logger.error(
                "skipping bad value for model %s: %s",
                model_cls.__name__, str(kwargs)
            )
        logger.info(
            "generated Model %s %s", model.__class__.__name__, model.pk
        )
        models.append(model)
    return models, recheck


def postcompute(to_postcompute, generated, allow_null=False):
    """
    Postcompute some of the postponed fields, especially when there are
    cyclic relations of ManyToManyRelations.
    """
    for model_cls_name, fields in to_postcompute.items():
        models = generated[model_cls_name]
        for field in fields:
            values = generate_field_values(
                field, len(models), generated, allow_null=allow_null
            )
            if is_many_to_many_field(field):
                for model in models:
                    getattr(model, field_name(field)).add(*choices(
                        values, k=random.randint(0, min(5, len(values)))
                    ))
            else:
                for model, value in zip(models, values):
                    setattr(model, field_name(field), value)

        for model in models:
            model.save()


def generate_test_data(app_name: str, size: int,
                       allow_null: bool = False, models_cls: list = None):
    """
    Generates a list of 'size' random data for each model in the models module
    in the given path, If the sample data is not enough for generating 'size'
    models, then all of the sample data will be used. If the models are
    inconsistent then no data will be generated. The data will be stored in
    a temporary database used for generation.

    :param app_name: Name of the app
    :param size: An integer that specifies the size of the generated data.
    :param allow_null: if True, no null values will be allowed.
    :param models_cls: Generate only for a specific set of models.
    """

    all_models = retrieve_models(app_name + ".models")
    if models_cls is None:
        models_cls = all_models[:]
    else:
        names_map = dict(
            (model_cls.__name__, model_cls) for model_cls in all_models
        )
        models_cls = set([names_map[model_cls] for model_cls in models_cls])
        # get all dependencies
        siz = len(models_cls)
        while True:
            models_cls |= set([
                dep for model_cls in models_cls
                for dep in dependencies(model_cls, True)
            ])
            if len(models_cls) <= siz:
                break
            else:
                siz = len(models_cls)
        models_cls = list(models_cls)

    models_cls, cycle = topological_sort(models_cls, dependencies)
    if cycle:
        raise ValueError(
            "Detected cyclic dependencies between models. " +
            " -> ".join(map(lambda cls: cls.__name__, cycle))
        )

    generators = retrieve_generators(
        app_name + ".test_data", [cls.__name__ for cls in models_cls]
    )
    to_postcompute = {}
    generated = {}
    for model_cls in models_cls:
        models, recheck = generate_models(
            model_cls, size, generated, generators=generators,
            allow_null=allow_null
        )
        generated[model_cls.__name__] = models
        if recheck:
            to_postcompute[model_cls.__name__] = recheck

    postcompute(to_postcompute, generated)
