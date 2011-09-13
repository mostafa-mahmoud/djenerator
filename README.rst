==========
Djenerator
==========
Djenerator is a simple tool made to generate test/random data from the model description of django.

Installation
============
Run the setup.py script using the following command.::

        python setup.py install


How To Use
==========
#. The app 'djenerator' needs to be added to the installed apps in the settings of the project.

    * Note : when the data are generated, they are stored in a temporary database until they are serialized to a .json file.

#. Sample data should be added for every field that is not a related field.
   The sample data can be added by two methods.
   The first method is by adding a class called TestData to the model description, for each non-related field in the model, a variable of the same name should be added to the class TestData, the value of such a variable will be the sample data, the sample data can be either a list, tuple, string containing a name of file or function with no arguments, as an example  

   Sample data given as a list ::
  
       class Job(models.Model):
           job_name = models.CharField(max_length=50)
           
           class TestData:
               job_name = ['engineer', 'professor', 'technician']

   Sample data given as a tuple ::
        
       class Job(models.Model):
           job_name = models.CharField(max_length=50)
           
           class TestData:
               job_name = ('engineer', 'professor', 'technician')
        
   Sample data given as a function ::
        
       def values():
           res = []
           for i in range(1, 101):
               for j in range(1, 11):
                   res.append(i + j)
           return res

        
       class Money(models.Model):
           amount = models.IntegerField()

           class TestData:
               amount = values

   Sample data given as a string contains the name of a file ::
        
       class Person(models.Model):
          name = models.CharField(max_length=50)

          class TestData:
              name = 'list_of_names'
 
   The second method is by adding a file that contains the sample data with the signature 'sample__modelname__fieldname'; in this method there's no need for adding the class TestData.
    
   Files added for sample data must be stored in a folder called 'TestTemplates' that's located inside the project.
#. Constraints may be added, such that the models will be created only if they satisfy the given constraints. There are constraints that already exists in django, like unique field and unique_together, for example ::

        class Course(models.Model):
            course_name = models.CharField(max_length=200)
            course_code = models.IntegerField(unique=True)
            person = models.OneToOneField(Person, null=True)
            
            class TestData:
                course_name = course
                course_code = codes
            
            class Meta:
                unique_together = (('course_name', 'course_code'),)

   Such constraints are handled in the application, but if there are custom constraints that needs to be added, then a function that returns true if and only if the required constraints are satisfied should be added.
   The signature of the function will be as :: 

        predicate(current_values, reference_model, reference_field) 

   where current_values is a list of ordered pairs in the form (field name, field value), reference_model is a reference to the class of the model being filled and reference_field is a reference to the class of field being filled. The function also should handle that some of the fields might not be found in current_values as they are not filled yet, in such a case the constraint shouldn't return false unless the field as already filled with a value that doesn't satisfy the constraints.
   All the constraints functions should be added to a list, this list will be the value of a variable called 'constraints' that is nested in a class called 'Constraints' that is added for the description of the model, for example ::
        
        def gender_names(current_values, reference_model, reference_field):
            """
                This function is true if the gender of the model 
                matches the gender of the name.
            """
            dic = dict(current_values)
            keys = dic.keys()
            if not ('name' in keys and 'gender' in keys):
                return True
            else:
                is_male = dic['gender'] == 'M'
                is_male_name = dic['name'] in ['John', 'Eric', 'Dmitri']
                # return is_male XNOR is_male_name
                return not (is_male ^ is_male_name)


        class Person(models.Model):
            name = models.CharField(max_length=50)
            age = models.IntegerField()
            gender = models.CharField(max_length=1)

            class TestData:
                name = ('Julia', 'John', 'Eric', 'Jennifer', 'Dmitri', 'Mary')
                age = range(0, 101)
                gender = ('M', 'F')

            class Constraints:
                constraints = [genders_names] 

   If the previously created models are required and since there's a reference to the model in the constraint function, then they can be simply accessed by reference_model.objects.all()

#. The generation of data are then done by a command using manage.py file in the project::

        python manage.py generate number app_name output_file

   for example if there is an app called 'main', and I need to generate 20 of each model in the models description file, and put them to a file called 'hello.json', I would run the command ::
   
        python manage.py generate 20 main hello
    
   The arguments of the command follow the convention, I want 'number' sample models for each model in the app 'app_name', and store them in 'output_file'.

Running the tests
=================
Run the tests by running the command.::

    python runtests.py

TODOs and BUGS
==============
See: https://github.com/aelguindy/djenerator/issues 

