import random


class TestModel1:
    field2 = lambda: random.randint(1, 1000) * 91
    field3 = list(range(10000))


class TestModelFieldsTwo:
    fieldG = lambda: format(random.randint(1, 10 ** 15), ",")


class TestModelFields:
    fieldB = [1, 2, 3, 4, 5]