# Elask Framework

A python based rest framework for elastcsearch. Built on top of flask & elasticsearch-dsl. The purpose of this framework is to provide REST Api development and also to provide the hooks to accomodating the business logic.


## Create virtualenv
```
virtualenv -p python3 venv
```
This elask framework will only work with python3.x<br >

## Activate virtualenv
```
source venv/bin/activate
```

## Installation
```
pip3 install elask
```

## Creating your project

```python
# Syntax
# elask-admin startproject --name <project_name>`
elask-admin startproject --name helloworld
```

## Project layout

    helloworld    # Parent project directory
    settings/
        __init__.py
        dev.py

## Create application
```python
# Syntax
# elask-admin startapp --name <app_name>
elask-admin startapp --name services
```

## Create your model

`services/models.py`
```python
from elask.db import models

# you can create your models here

class User(models.Model):
    name = models.CharField()
    description = models.CharField()

    class Meta:
        doc_type = "user"
        index = "user"
```

## Create your serializers
`services/serializers.py`
```python
from elask.serializers import Serializer

# you can create your serializers here
class UserSerializer(Serializer):

    class Meta:
        fields = ['id', 'name', 'description']
```

## Create your viewsets
`services/viewsets.py`
```python
from elask import viewsets
from services.models import User
from services.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    model = User

    parser = {
        'default': UserSerializer
    }
```

## Create your routes
`services/routes.py`
```python
from server import app
from flask_restful import Api
from services.viewsets import UserViewSet
api = Api(app)

# Example
api.add_resource(UserViewSet, '/user/', '/user/<pk>/')
```

## Include app in 'INSTALLED_APPS`
`settings/dev.py`
```python
"""
User Settings
"""
from datetime import datetime, timedelta

# Elasticsearch Domain
ELASTICSEARCH_DOMAIN = 'http://localhost:9200'

# Installed Apps
INSTALLED_APPS = [
    'services'
]

# Secret key for password hashing
SECRET_KEY = 'super-secret'
```

## Migrate
```
elask-admin migrate
```

## Run
```
python server.py
```

[http://localhost:5000/user/](http://localhost:5000/user/)

You can perform REST operations on this (GET, PUT, POST, DELETE).

# Available Management Command

The following are the avaialble commands

`elask-admin <command> <options>`

* ## startproject
* ## startapp
* ## migrate
* ## shell
* ## help
