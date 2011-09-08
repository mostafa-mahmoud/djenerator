
from django.db import models

class Job(models.Model):
    job_name = models.CharField(max_length=50)
    
    class TestData:
        job_name = 'job'

    def __unicode__(self):
        return self.job_name


class JobProxy(Job):

    class Meta:
        proxy = True


class RelTry(models.Model):
    a = models.CharField(max_length=200)
    b = models.ManyToManyField('self')

    class TestData:
        a = ['Her', 'Her2']
    
    def __unicode__(self):
        return self.a + " " + str([x.id for x in self.b.all()])


def gender_name(variable, model, field):
    l = dict(variable)
    if 'gender' in l.keys() and 'name' in l.keys():
        return not ((l['gender'] == 'M') ^ (l['name'] in ['abdallah', 'adel', 'adham', 'ahmad', 'ahmed', 'ali', 'amr', 'eslam', 'farid', 'hassan', 'hesham', 'hisham', 'ibrahim', 'islam', 'kareem', 'karim', 'khalid', 'mahmod', 'mahmoud', 'medhat', 'michel', 'mina', "mo'men", 'mohamed', 'mohammed', 'mostafa', 'moustafa', 'muhammed', 'mustafa', 'nader', 'omar', 'ramy', 'ramzi', 'seif', 'tamer', 'usif', 'waleed', 'walid', 'youssef']))
    else:
        return True


def codes():
    return [(x + y + 1) for x in range(100, 1100, 100) for y in range(1, 10)]


def names():
    return ['Mostafa', 'Mahmoud', 'Abdallah', 'Ramy', 'Ali', 'Ahmad', 'Mohammed', 'Tarek']


class Person(models.Model):
    name = models.CharField(max_length=200, unique=True)
    last_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    job = models.ForeignKey(Job)
    gender = models.CharField(max_length=1)
    
    class Meta:
        unique_together = (('name', 'last_name'),)
    
    class Constraints:
        constraints = [gender_name]
    
    class TestData:
        name = 'first_name'
        last_name = names()
        address = ['C7.303', 'C7.301', 'C7.310', 'C7.215', 'C5.303']
        gender = ['M', 'F']

    def __unicode__(self):
        return self.gender + " " + self.name + " " + self.last_name + ", " + self.address + ", " + str(self.job)


class Student(Person):
    student_id = models.IntegerField()

    class TestData:
        student_id = range(10)

    def __unicode__(self):
        return str(self.student_id)


def course():
    return ['Theory of computation', 'Numerical analysis', 'Discrete Mathematics', 'Analysis of algorithms', 'Electric circuits', 'Quantum mechanics']


class Course(models.Model):
    course_name = models.CharField(max_length=200)
    course_code = models.IntegerField(unique=True)
    person = models.OneToOneField(Person)
    
    class TestData:
        course_name = course
        course_code = codes
    
    class Meta:
        unique_together = (('course_name', 'course_code'),)
    
    def __unicode__(self):
        return str(self.course_code) + " " + self.course_name + " by " + str(self.person)

