=====
Usage
=====

Adding to installed apps
------------------------

   To use djenerator in your project, add it to your `INSTALLED_APPS`:

    .. code-block:: python

        INSTALLED_APPS = (
            ...
            'djenerator',
            ...
        )


    * Note : when the data is being generated, it is stored in a temporary database until they are serialized to a JSON file.

Adding sources of values
------------------------

   Sample data are randomly generated for each (not related) field unless there are sample values that are added. The sample data can be added in two ways.

   The first way is by adding a class called `TestData` to the model description, such that for each non-related field in the model there's a corresponding variable with the same name, the value of such variable will be the sample dataprovided.

   Sample data given as a list:

    .. code-block:: python

       class Job(models.Model):
           job_name = models.CharField(max_length=50)

           class TestData:
               job_name = ['engineer', 'professor', 'technician']

   Sample data given as a tuple:

    .. code-block:: python

       class Job(models.Model):
           job_name = models.CharField(max_length=50)

           class TestData:
               job_name = ('engineer', 'professor', 'technician')

   Sample data given as a generator function:

    .. code-block:: python

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

   Sample data given as a string contains the name of a file:

    .. code-block:: python

       class Person(models.Model):
          name = models.CharField(max_length=50)

          class TestData:
              name = 'file_list_of_names'

   The second way is by adding a file that contains the sample data with the signature 'sample__modelname__fieldname'; in this method there's no need for adding the class `TestData`.

   Files added for sample data must be stored in a folder called `TestTemplates` that's located inside the app directory, as shown in example app.

Adding constraints
------------------

   Constraints may be added, such that the models will be created only if they satisfy the given constraints. There are constraints that already exists in django, like unique field and unique_together, for example:

    .. code-block:: python

        class Course(models.Model):
            course_name = models.CharField(max_length=200)
            course_code = models.IntegerField(unique=True) # here
            person = models.OneToOneField(Person, null=True)

            class TestData:
                course_name = course
                course_code = codes

            class Meta:
                unique_together = (('course_name', 'course_code'),) # here

   Such constraints are handled in djenerator, but if there are custom constraints that need to be added, then a function should be added that returns true if and only if the required constraints are satisfied. The signature of the function will be as :

    .. code-block:: python

        predicate(current_values, reference_model, reference_field)

   Where `current_values` is a list of ordered pairs in the form (field name, field value) which is a partial field assignment for the model, `reference_model` is a reference to the class of the model being filled and `reference_field` is a reference to the class of field being filled. The function also should handle that some of the fields might not be assigned yet in `current_values`, in such case the constraint shouldn't return `false` unless the partial field assignment doesn't satisfy the constraint.
   All the constraints functions should be added to a list, this list will be the value of a variable called 'constraints' that is nested in a class called 'Constraints' that is added for the description of the model, for example:


    .. code-block:: python

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

Generating commands
-------------------

   The generation of data are then done by a command using manage.py file in your project:

    .. code-block:: bash

        $ python manage.py jenerate size app_name output_file

   There's another command that can be used for data generation, in this case the generated data will be dumped in the database:

    .. code-block:: bash

        $ python manage.py jendb size app_name

   for example if there is an app called 'example', and I need to generate 20 of each model in the models description file, and put them to a file called 'hello.json' (or put them in the database), I would run the command:

    .. code-block:: bash

        $ python manage.py jenerate 20 example hello
        $ python manage.py jendb 20 example

   * The arguments of the command follow the convention, I want 'number' sample models for each model in the app 'app_name', and store them in 'output_file'.

   `model_sizes` is an additional option that can be used to override the number of instances to be generated for some specific models; after using the option, the models and the corresponding sizes should be given as a list of arguments in the format 'model_name:model_size', and if there's a model not in this list, then the default `size` will be used, as shown by the command:

    .. code-block:: bash

        $ python manage.py jenerate number app_name output_file --model_sizes modelA:sizeA modelB:sizeB # ...
        $ python manage.py jendb number app_name --model_sizes modelA:sizeA modelB:sizeB # ...

   For example, these commands will generate 20 instances for each model; but only 1 instance for Student, and 2 instances of Course:

    .. code-block:: bash

        $ python manage.py jenerate 20 example hello --model_sizes Student:1 Course:2
        $ python manage.py jendb 20 example --model_sizes Student:1 Course:2


Use inside python
-----------------

   Djenerator can be used inside python as well, one needs to call the function 'djenerator' located in the module djenerator.djenerator. (Those are 3 djenerator's, yes) :

    .. code-block:: python

        from djenerator.djenerator import djenerator
        djenerator(app_path, size, output_file, **size_options)


   where `app_path` is the app name, `size` is the sample size to be generated for each model, and `output_file` is a file object in which the data will be dumped. If the `output_file` is `None`, then the data will be dumped into the database. The argument `size_options` is a dictionary that maps a 'model_name' to 'model_size' which is the number of generated instances for this model by djenerator, and if a model isn't in the dictionary, then the default `size` will be used.

