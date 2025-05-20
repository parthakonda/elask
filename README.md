# Elask Framework

A Python-based REST framework for Elasticsearch. Built on top of Flask and elasticsearch-dsl. Its purpose is to simplify REST API development with Elasticsearch and provide hooks for custom business logic.


## Create virtualenv
```bash
virtualenv -p python3 venv
```
This Elask framework is compatible only with Python 3.x.

## Activate virtualenv
```
source venv/bin/activate
```

## Installation
```bash
pip3 install elask
```

## Creating your project

To create a new project, use the `elask-admin startproject` command:
```bash
# elask-admin startproject --name <project_name>
elask-admin startproject --name helloworld
```

## Project layout

This will create a project directory with the following structure:
```
helloworld    # Parent project directory
settings/
    __init__.py
    dev.py
```

## Create application

To create a new application within your project, use `elask-admin startapp`:
```bash
# elask-admin startapp --name <app_name>
elask-admin startapp --name services
```

## Create your model

### `services/models.py`
```python
from elask.db import models

class User(models.Model):
    name = models.CharField()
    description = models.CharField()

    class Meta:
        doc_type = "user"
        index = "user"
```

## Create your serializers
### `services/serializers.py`
```python
from elask.serializers import Serializer

class UserSerializer(Serializer):

    class Meta:
        fields = ['id', 'name', 'description']
```

## Create your viewsets
### `services/viewsets.py`
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
### `services/routes.py`
```python
from server import app
from flask_restful import Api
from services.viewsets import UserViewSet

api = Api(app)

# Example
api.add_resource(UserViewSet, '/user/', '/user/<pk>/')
```

## Include app in `INSTALLED_APPS`
### `settings/dev.py`
```python
"""
Development settings for the Elask project.
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
```bash
elask-admin migrate
```

## Run
```bash
python server.py
```

Navigate to [http://localhost:5000/user/](http://localhost:5000/user/).

You can now perform REST operations (GET, PUT, POST, DELETE) on this endpoint.

# Available Management Commands

The following management commands are available:
```bash
elask-admin <command> <options>
```

* `startproject`
* `startapp`
* `migrate`
* `shell`
* `help`

# Contributing
Contributions are welcome! If you'd like to contribute to Elask, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name` or `git checkout -b bugfix/issue-number`).
3. Make your changes and commit them with clear and concise messages.
4. Push your changes to your fork.
5. Create a pull request to the main Elask repository.

# License
This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
