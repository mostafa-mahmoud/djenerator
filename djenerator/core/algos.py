
def topological_sort(models: list, dependencies_func) -> list:
    """
    Sort a given list of models according to the dependencies of the
    relations between the models.

    :param List models: A list of model class references.
    """
    result = []
    visited = set([])
    pending = set([])
    non_leafs = list(filter(dependencies_func, models))

    def visit(model):
        if model not in visited:
            if model in pending:
                return [model]
            pending.add(model)
            for dep_model in dependencies_func(model):
                cycle = visit(dep_model)
                if cycle:
                    cycle.append(model)
                    return cycle
            visited.add(model)
            pending.remove(model)
            result.append(model)

    while non_leafs:
        model = non_leafs.pop()
        cycle = visit(model)
        if cycle:
            return [], cycle

    result_singleton = []
    for model in models:
        if model not in result:
            result_singleton.append(model)
    return result_singleton + result, []
