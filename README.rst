Timeclock Application
=====================

Requirements
^^^^^^^^^^^^

- Python 3.6 and above
- django==3.2.14
- graphene-django==2.15.0
- django-graphql-jwt==0.3.4


Installation
^^^^^^^^^^^^

-  Clone the repository

      ::

          $ git clone https://github.com/adityacp/timeclock.git

-  Go to the project directory

      ::

          $ cd timeclock


- Installing project packages

      ::

          $ pip install -r requirements.txt


- Run migrations commands

      ::

          $ python manage.py makemigrations
          $ python manage.py migrate


- Create superuser

      ::

          $ python manage.py createsuperuser


- Run server Locally
      
      ::

          $ python manage.py runserver


- Run the localhost

      ::

          $ http://127.0.0.1:8000/graphql


