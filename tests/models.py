#!/usr/bin/env python
from django.db import models


class ExtendingModel(models.Model):
    pass


class NotExtendingModel(object):
    pass


class TestModel0(models.Model):
    field1 = models.BooleanField()
    field2 = models.EmailField(max_length=200)

    class TestData:
        field1 = [True, False]
        field2 = ['a@b.com', 'z@x.com']


class TestModel1(models.Model):
    field1 = models.CharField(max_length=200)
    field2 = models.BigIntegerField()
    field3 = models.ForeignKey(TestModel0)

    class Meta:
        unique_together = (('field1', 'field2'), ('field2', 'field3'))

    class TestData:
        field1 = ['Hello World']
        field2 = [2, 43, 6, 5, 2 ** 50, 1000000000000000, -111]


def vals1():
    return ['Hello Second Field', 'field 2']


class TestModelA(models.Model):
    field1A = models.CharField(max_length=200)
    field2A = models.CharField(max_length=200)

    class TestData:
        field1A = ['Hello World', 'Hello Africa', 'axxx!!']
        field2A = vals1

    def __unicode__(self):
        return str(self.id) + " " + self.field1A + " " + self.field2A


class TestModelB(models.Model):
    field1B = models.CharField(max_length=100)
    field2B = models.ForeignKey(TestModelA)

    class TestData:
        field1B = ['Hello Universe', 'Hello Parallel Universe!']

    def __unicode__(self):
        return self.field1B + " " + str(self.field2B)


class TestModelC(models.Model):
    field1C = models.CharField(max_length=50)
    field2C = models.OneToOneField(TestModelB)

    class TestData:
        field1C = 'test_c'

    def __unicode__(self):
        return self.field1C + " " + str(self.field2C)


def cubes():
    return [x * x * x for x in range(10)]


class TestModelD(models.Model):
    field1D = models.IntegerField()
    field2D = models.ManyToManyField(TestModelA)

    class TestData:
        field1D = cubes

    def __unicode__(self):
        return str(self.field1D) + " " + str(self.field2D.all())


class TestModelE(models.Model):
    field1E = models.OneToOneField(TestModelB)
    field2E = models.ManyToManyField(TestModelA)
    field3E = models.ForeignKey(TestModelC)
    field4E = models.IntegerField()

    class TestData:
        field4E = [1000000009, 1000003, 101]

    def __unicode__(self):
        return str(self.field4E)


class TestModelX(models.Model):
    field1X = models.IntegerField()

    class TestData:
        field1X = cubes

    def __unicode__(self):
        return str(self.field1X)


class TestModelY(models.Model):
    field1Y = models.IntegerField()
    field2Y = models.CharField(max_length=200)
    field3Y = models.ForeignKey(TestModelX)

    class TestData:
        field1Y = [2, 3, 5, 7, 11, 13]
        field2Y = ['MMa', 'XXa', 'azz']

    def __unicode__(self):
        return str(self.field1Y) + " " + self.field2Y + " " + str(self.field3Y)


class SuperClass(models.Model):
    fieldS = models.IntegerField()
    fieldAbr = models.IntegerField()
    fieldFak = models.IntegerField()
    fieldMTM = models.ManyToManyField('self')

    class TestData:
        fieldS = [1, 11, 21, 1211, 111221, 312211, 13112221, 1113213211]
        fieldAbr = (2, 6, 22, 134, 582, 1111111)
        fieldFak = [0, 1, 2, 3, 4, 5]


class SuperAbstract(models.Model):
    fieldAbs = models.IntegerField()

    class TestData:
        fieldAbs = (2, 4, 16, 112, 448, 7168, 157696)

    class Meta:
        abstract = True


class ExtendAbstract(SuperAbstract):
    fieldExAbs = models.CharField(max_length=200)
    fieldZZZ = models.IntegerField()

    class TestData:
        fieldExAbs = ['Abstract 101', 'Abstract 202', 'Abstract 503']


class ExtendSuperClass(SuperClass):
    fieldExSup = models.CharField(max_length=200)

    class TestData:
        fieldExSup = ['Super 101', 'Super 202', 'Super 503']


class ProxyExtend(SuperClass):

    class Meta:
        proxy = True


def fun(cur_tuple, model, field):
    dic = dict(cur_tuple)
    keys = dic.keys()
    if not 'fieldF' in keys or not 'fieldB' in keys:
        return True
    return (dic['fieldB'] < 50) or (dic['fieldD'] / 2 % 2 == 1)


class TestModelFieldsTwo(models.Model):
    fieldA = models.CharField(max_length=500)
    fieldB = models.IntegerField()
    fieldC = models.CharField(max_length=50)
    fieldD = models.IntegerField()
    fieldE = models.BooleanField()
    fieldF = models.IntegerField()
    fieldG = models.CharField(max_length=200)
    fieldH = models.BooleanField()
    fieldZ = models.ManyToManyField(TestModelE)

    class TestData:
        fieldA = ['A', 'B', 'C', 'D', 'E']
        fieldB = [10, 20, 30, 40, 50, 60, 70, 80]
        fieldC = ['Winner', 'Loser', 'Warrior']
        fieldD = [3, 5, 11, 13, 17, 19, 29, 31, 41, 43]
        fieldE = [True, False]
        fieldF = [6, 28, 496, 8128, 33550336]
        fieldG = ['Mathematics', 'Physics', 'Chemistry', 'Biology']
        fieldH = [True, False]

    class Constraints:
        constraints = [fun]


class TestModelFields(models.Model):
    fieldY = models.OneToOneField(TestModelY)
    fieldA = models.CharField(max_length=500)
    fieldB = models.IntegerField()
    fieldC = models.CharField(max_length=50)
    fieldD = models.IntegerField()
    fieldE = models.BooleanField()
    fieldF = models.IntegerField()
    fieldG = models.CharField(max_length=200)
    fieldH = models.BooleanField()
    fieldX = models.ForeignKey(TestModelX)
    fieldZ = models.ManyToManyField(TestModelE)

    class Meta:
        unique_together = ('fieldA', 'fieldC')

    class TestData:
        fieldA = ['A', 'B', 'C', 'D', 'E']
        fieldB = [10, 20, 30, 40, 50, 60, 70, 80]
        fieldC = ['Winner', 'Loser', 'Warrior']
        fieldD = [3, 5, 11, 13, 17, 19, 29, 31, 41, 43]
        fieldE = [True, False]
        fieldF = [6, 28, 496, 8128, 33550336]
        fieldG = ['Mathematics', 'Physics', 'Chemistry', 'Biology']
        fieldH = [True, False]

    class Constraints:
        constraints = [fun]


class CycleA(models.Model):
    ab = models.ForeignKey('CycleB')
    ae = models.ForeignKey('CycleE')
    a = models.IntegerField()

    class TestData:
        a = range(1000)


class CycleB(models.Model):
    bc = models.ForeignKey('CycleC')
    b = models.IntegerField()

    class TestData:
        b = range(1000, 2000)


class CycleC(models.Model):
    cc = models.ManyToManyField('self')
    ca = models.OneToOneField(CycleA, null=True)
    c = models.DecimalField(max_digits=15, decimal_places=10)

    class TestData:
        c = ['3.14159', '2.818281828', '1.6181', '1.4142', '1.73201']


class CycleD(models.Model):
    dc = models.ForeignKey(CycleC)
    df = models.ForeignKey('CycleF', null=True)
    d = models.IntegerField()

    class TestData:
        d = range(3000, 4000)


class CycleE(models.Model):
    ec = models.ForeignKey(CycleC)
    ed = models.ForeignKey(CycleD)
    e = models.IntegerField()

    class TestData:
        e = range(6000, 10000)


class CycleF(models.Model):
    fd = models.ForeignKey(CycleD)
    f = models.IntegerField()


class AllFieldsModel(models.Model):
    bigint_field = models.BigIntegerField()
    int_field = models.IntegerField()
    email_field = models.EmailField(max_length=40)
    bool_field = models.BooleanField()
    char_field = models.CharField(max_length=100)
    comma_sep_int_field = models.CommaSeparatedIntegerField(max_length=20)
    decimal_field = models.DecimalField(max_digits=15, decimal_places=8)
    datetime_field = models.DateTimeField()
    date_field = models.DateField()
    duration_field = models.DurationField()
    float_field = models.FloatField()
    null_bool_field = models.NullBooleanField()
    pos_int_field = models.PositiveIntegerField()
    small_pos_int_field = models.PositiveSmallIntegerField()
    small_int_field = models.SmallIntegerField()
    text_field = models.TextField(max_length=500)
    time_field = models.TimeField()
    gen_ip_field = models.GenericIPAddressField()
    url_field = models.URLField()
    slug_field = models.SlugField()
    uuid_field = models.UUIDField()
    file_path_field = models.FilePathField()
