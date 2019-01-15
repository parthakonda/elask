"""
ViewSets are essentially just a type of class based view, that doesn't provide
any method handlers, such as `get()`, `post()`, etc... but instead has actions,
such as `list()`, `retrieve()`, `create()`, etc...
"""
from flask import request
from flask_jwt import jwt_required
from flask_jwt import current_identity

from elask import mixins
from elask import generics

from settings.dev import ENABLE_JWT, TENANT_FIELD


class ModelViewSet(
    generics.ListRetrieveAPIView,
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.DestroyAPIView,
    generics.GenericAPIView
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `destroy()` and `list()` actions.
    """
    pass
