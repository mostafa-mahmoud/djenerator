import os

import django
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


def validate_mod91(value):
    if value % 91 != 0:
        raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )


class ExtendingModel(models.Model):
    pass


class NotExtendingModel(object):
    pass


class TestModel0(models.Model):
    field1 = models.BooleanField()
    field2 = models.EmailField(
        validators=[
            (
                validators.EmailValidator(whitelist=["google.com"])
                if django.__version__ < "4.1" else
                validators.EmailValidator(allowlist=["google.com"])
            ),
            validators.MinLengthValidator(40),
        ]
    )
    field3 = models.URLField(
        validators=[
            validators.URLValidator(schemes=["redis", "tcp"]),
            validators.MinLengthValidator(40),
            validators.MaxLengthValidator(120),
        ]
    )


class TestModel1(models.Model):
    field1 = models.CharField(
        max_length=200, validators=[
            validators.int_list_validator, validators.MinLengthValidator(195)
        ]
    )
    field2 = models.BigIntegerField(
        validators=[
            validators.StepValueValidator(91)
            if hasattr(validators, "StepValueValidators") else validate_mod91
        ]
    )
    field3 = models.ForeignKey(TestModel0, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('field1', 'field2'), ('field2', 'field3'))


class TestModelA(models.Model):
    field1A = models.CharField(max_length=200)
    field2A = models.CharField(max_length=200)
    field3A = models.GenericIPAddressField()
    field4A = models.GenericIPAddressField(protocol="IPv4")
    field5A = models.GenericIPAddressField(
        validators=[validators.validate_ipv6_address]
    )
    field6A = models.GenericIPAddressField(protocol="IPv6")
    field7A = models.GenericIPAddressField(
        validators=[validators.validate_ipv4_address]
    )


class TestModelB(models.Model):
    field1B = models.CharField(max_length=100)
    field2B = models.ForeignKey(TestModelA, on_delete=models.CASCADE)


class TestModelC(models.Model):
    field1C = models.CharField(max_length=50)
    field2C = models.OneToOneField(TestModelB, on_delete=models.CASCADE)


class TestModelD(models.Model):
    field1D = models.IntegerField()
    field2D = models.ManyToManyField(TestModelA)


class TestModelE(models.Model):
    field1E = models.OneToOneField(TestModelB, on_delete=models.CASCADE)
    field2E = models.ManyToManyField(TestModelA)
    field3E = models.ForeignKey(TestModelC, on_delete=models.CASCADE)
    field4E = models.IntegerField()


class TestModelX(models.Model):
    field1X = models.IntegerField()


class TestModelY(models.Model):
    field1Y = models.IntegerField()
    field2Y = models.CharField(max_length=200, null=True)
    field3Y = models.ForeignKey(TestModelX, on_delete=models.CASCADE)


class SuperClass(models.Model):
    fieldS = models.IntegerField()
    fieldAbr = models.IntegerField()
    fieldFak = models.IntegerField()
    fieldMTM = models.ManyToManyField('self')


class SuperAbstract(models.Model):
    fieldAbs = models.IntegerField()

    class Meta:
        abstract = True


class ExtendAbstract(SuperAbstract):
    fieldExAbs = models.CharField(max_length=200)
    fieldZZZ = models.IntegerField()


class Extend_SuperClass(SuperClass):
    fieldExSup = models.CharField(max_length=200)


class ExtendExtendSuperClass(Extend_SuperClass):
    fieldExSup2 = models.CharField(max_length=200)


class ExtendSuperClassNoProxy(SuperClass):

    class Meta:
        proxy = False


class ProxyExtend(SuperClass):

    class Meta:
        proxy = True


class TestModelFieldsTwo(models.Model):
    fieldA = models.CharField(max_length=500)
    fieldB = models.IntegerField()
    fieldC = models.CharField(max_length=50)
    fieldD = models.IntegerField()
    fieldE = models.BooleanField()
    fieldF = models.IntegerField()
    fieldG = models.CharField(
        max_length=200,
        validators=[validators.validate_comma_separated_integer_list]
    )
    fieldH = models.BooleanField()
    fieldZ = models.ManyToManyField(TestModelE)
    fieldQ = models.FileField(
        upload_to=os.path.join("media", "trash"),
        validators=(
            [validators.FileExtensionValidator([".rst", ".json", ".txt"])]
            if hasattr(validators, "FileExtensionValidator") else []
        )
    )
    fieldR = models.FileField(
        upload_to=os.path.join("media", "trash"),
        validators=(
            [validators.FileExtensionValidator([".rst"])]
            if hasattr(validators, "FileExtensionValidator") else []
        )
    )
    fieldI = models.ImageField(
        upload_to=os.path.join('media', 'trash'),
        validators=(
            [validators.FileExtensionValidator([".png", ".jpg"])]
            if hasattr(validators, "FileExtensionValidator") else []
        )
    )


class TestModelFields(models.Model):
    fieldY = models.OneToOneField(TestModelY, on_delete=models.CASCADE)
    fieldA = models.CharField(max_length=500, primary_key=True)
    fieldB = models.IntegerField(null=True)
    fieldC = models.CharField(max_length=50, unique=True)
    fieldD = models.IntegerField()
    fieldE = models.BooleanField()
    fieldF = models.IntegerField()
    fieldG = models.CharField(max_length=200, null=True)
    fieldH = models.BooleanField()
    fieldX = models.ForeignKey(TestModelX, on_delete=models.CASCADE)
    fieldZ = models.ManyToManyField(TestModelE)

    class Meta:
        unique_together = ('fieldA', 'fieldC')


class CycleA(models.Model):
    ab = models.ForeignKey('CycleB', on_delete=models.CASCADE)
    ae = models.ForeignKey('CycleE', on_delete=models.CASCADE)
    a = models.IntegerField(validators=[
        validators.MaxValueValidator(-3),
        validators.MinValueValidator(-100),
    ])


class CycleB(models.Model):
    bc = models.ForeignKey('CycleC', on_delete=models.CASCADE)
    b = models.IntegerField()


class CycleC(models.Model):
    cc = models.ManyToManyField('self')
    ca = models.OneToOneField(CycleA, null=True, on_delete=models.CASCADE)
    c = models.DecimalField(max_digits=3, decimal_places=3)


class CycleD(models.Model):
    dc = models.ForeignKey(CycleC, on_delete=models.CASCADE)
    df = models.ForeignKey('CycleF', null=True, on_delete=models.CASCADE)
    d = models.IntegerField()


class CycleE(models.Model):
    ec = models.ForeignKey(CycleC, on_delete=models.CASCADE)
    ed = models.ForeignKey(CycleD, on_delete=models.CASCADE)
    e = models.IntegerField()


class CycleF(models.Model):
    fd = models.ForeignKey(CycleD, on_delete=models.CASCADE)
    f = models.IntegerField()


class AllFieldsModel(models.Model):
    bigint_field = models.BigIntegerField()
    int_field = models.IntegerField()
    email_field = models.EmailField()
    bool_field = models.BooleanField()
    char_field = models.CharField(max_length=100)
    decimal_field = models.DecimalField(max_digits=15, decimal_places=8)
    datetime_field = models.DateTimeField()
    date_field = models.DateField()
    duration_field = models.DurationField()
    float_field = models.FloatField()
    # null_bool_field = models.BooleanField(null=True)
    pos_int_field = models.PositiveIntegerField()
    small_pos_int_field = models.PositiveSmallIntegerField()
    small_int_field = models.SmallIntegerField()
    pos_big_int_field = (
        models.PositiveBigIntegerField()
        if hasattr(models, "PositiveBigIntegerField") else
        models.BigIntegerField()
    )
    text_field = models.TextField()
    time_field = models.TimeField()
    gen_ip_field = models.GenericIPAddressField()
    url_field = models.URLField()
    slug_field = models.SlugField()
    uuid_field = models.UUIDField()
    file_path_field = models.FilePathField()
    # binary_field = models.BinaryField(max_length=200)
    binary_field = models.BinaryField()
    file_field = models.FileField(upload_to=os.path.join('media', 'files'))
    image_field = models.ImageField(upload_to=os.path.join('media', 'images'))
    js_field = (
        models.JSONField() if hasattr(models, "JSONField")
        else models.TextField()
    )
