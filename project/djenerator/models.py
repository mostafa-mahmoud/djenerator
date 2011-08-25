#!/usr/bin/env python
from django.db import models
# Create your models here.

class ExtendingModel(models.Model):
    pass


class NotExtendingModel(object):
    pass


class TestModel0(models.Model):
    field1= models.BooleanField()
    field2 = models.EmailField(max_length=200)


class TestModel1(models.Model):
    field1 = models.CharField(max_length=200)
    field2 = models.BigIntegerField()
    field3 = models.ForeignKey(TestModel0)


class TestModelA(models.Model):
    field1A = models.CharField(max_length=200)
    field2A = models.CharField(max_length=200)
    
    def __unicode__(self):
        return str(self.id) + " " + self.field1A + " " + self.field2A


class TestModelB(models.Model):
    field1B = models.CharField(max_length=100)
    field2B = models.ForeignKey(TestModelA)
    
    def __unicode__(self):
        return self.field1B + " " + str(self.field2B)


class TestModelC(models.Model):
    field1C = models.CharField(max_length=50)
    field2C = models.OneToOneField(TestModelB)
        
    def __unicode__(self):
        return self.field1C + " " + str(self.field2C)


class TestModelD(models.Model):
    field1D = models.IntegerField()
    field2D = models.ManyToManyField(TestModelA)
    
    def __unicode__(self):
        return str(self.field1D) + " " + str(self.field2D.all())    


class TestModelE(models.Model):
    field1E = models.OneToOneField(TestModelB)
    field2E = models.ManyToManyField(TestModelA)
    field3E = models.ForeignKey(TestModelC)
    field4E = models.IntegerField()
    
    def __unicode__(self):
        return str(self.field4E)


class TestModelX(models.Model):
    field1X = models.IntegerField()
    
    def __unicode__(self):
        return str(self.field1X)


class TestModelY(models.Model):
    field1Y = models.IntegerField()
    field2Y = models.CharField(max_length=200)
    field3Y = models.ForeignKey(TestModelX)
    
    def __unicode__(self):
        return str(self.field1Y) + " " + self.field2Y + " " + str(self.field3Y)


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
    

class ExtendSuperClass(SuperClass):
    fieldExSup = models.CharField(max_length=200) 
    

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
    fieldG = models.CharField(max_length=200)
    fieldH = models.BooleanField()
    fieldZ = models.ManyToManyField(TestModelE)
    

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
    

class CycleA(models.Model):
    ab = models.ForeignKey('CycleB')
    ae = models.ForeignKey('CycleE')
    a = models.IntegerField()
    

class CycleB(models.Model):
    bc = models.ForeignKey('CycleC')
    b = models.IntegerField()
    

class CycleC(models.Model):
    cc = models.ManyToManyField('self')
    ca = models.ManyToManyField(CycleA)
    c = models.DecimalField(max_digits=15, decimal_places=10)
    

class CycleD(models.Model):
    dc = models.ForeignKey(CycleC)
    df = models.ManyToManyField('CycleF')
    d = models.IntegerField()
    

class CycleE(models.Model):
    ec = models.ForeignKey(CycleC)
    ed = models.ForeignKey(CycleD)
    e = models.IntegerField()
    

class CycleF(models.Model):
    fd = models.ForeignKey(CycleD)
    f = models.IntegerField()


