# Bincom Test
## To get started, make sure python and mysql-server is installed
- For Linux users
`sudo apt install mysql-server`
- For windows users vist
[https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
Dont forget to add mysql to window PATH.

## Next create a new database
`echo "CREATE DATABASE bincom_test;" | mysql -u root -p`

## Next get the SQL database dump to get started
Download the dump file from https://drive.google.com/file/d/0B77xAtHK1hd4Ukx6SHpqTkd6TWM/view
- For Linux users
`cat bincom_test.sql | mysql -u user -p bincom_test`
- For Windows users
`Get-Content bincom_test.sql | mysql -u user -p bincom_test`

## Next install django and set up your poject and app
- `pip install django`
- `django-admin startproject bincom_test`
- `python manage.py startapp app_name`
- `python manage.py makemigrations`
- `python manage.py migrate`
### Don't forget to edit the Database settings in you project's settings.py
You can change it to this
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bincom_test',
        'USER': 'username',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS':{
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

## In your app directory, autogenerate the django model module from the database
`python manage.py inspectdb > models.py`

### To get geolocation information like latitude and longitudes use urllib.request.urlopen