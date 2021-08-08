### Procedures
Python Version - 3.8
Framework - Django
Note: Create an environment if necessary

$ git clone https://github.com/sreejasn7/geodecodercache.git
$ cd geodecodercache
$ pip install -r requirements.txt
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsuperuser


### Outputs 
$ python manage.py runserver 0.0.0.0:8000
Load Browser http://127.0.0.1:8000/get_address/-34.4391708/-58.7064573/


$ ./manage.py test
Helps in running the test cases and checks for the required test cases.

### Code structure

1. Home Module
    urls.py - Contains the redirection urls.

    converters.py - Contains to register float functionality and restricts the url parameters only to float values. 

    views.py - Contains the core functionalities.workflow for latitude/longitude across time

             - Important function is get function inside the class ReverseGeoDecoder. The central core function of this application. 
             - fetch_nominatim is a function inside the class ReverseGeoDecoder. Used to fetch nominatim calls.

    transactions.py - Contains DB save , update , validate. 
    models.py - Contains the DB model to save the API call. 
    admin.py - Regsiters the DB model class to admin functionality in Django. 
    tests.py - Automated tests




