from datetime import datetime
from flask import request

from elask import mixins
from flask_jwt import current_identity, jwt_required
from flask_restful import Api, Resource, abort, reqparse
from marshmallow import Schema
from settings.dev import ENABLE_JWT, TENANT_FIELD
from elask.permissions import Permission, PermissionNotFoundException, AnonymousUserException


class GenericAPIView(Resource):
    """
    Base class for all generic views
    """
    model = None
    name = None
    action = None
    multi_tenant = False
    lookup_field = 'id'
    parent_lookup_field = 'parent_id'
    full_text_search = False
    exact_search_fields = False
    soft_delete = {
        'enabled': False,
        'on_field': None
    }
    permission_class = None

    @property
    def index(self):
        return self.get_current_index()

    @property
    def doc_type(self):
        return self.get_current_doc_type()

    @property
    def user_id(self):
        return current_identity['user_id'] if 'user_id' in current_identity else None

    @property
    def user_email(self):
        return current_identity['email'] if 'email' in current_identity else None

    @property
    def _lookup_field(self):
        return getattr(self, 'lookup_field', 'id')

    @property
    def current_user(self):
        return current_identity

    @property
    def _parent_lookup_field(self):
        return getattr(self, 'parent_lookup_field', 'parent_id')

    def get_permission_class(self):
        """
        @return <has_permission_class (True/False)
        @return <permission_class>
        """
        permission_class = getattr(self, 'permission_class', False)
        if permission_class is False or permission_class is None or not permission_class:
            return None
        if not issubclass(permission_class, Permission):
            raise PermissionNotFoundException
        return permission_class

    def check_permission(self, action, current_user, request, *args, **kwargs):
        """
        Will check for permission 
        @return True/False
        """
        permission_class = self.get_permission_class()
        if permission_class:
            permission_klass = permission_class()
            if getattr(permission_klass, 'has_permission', None) is None:
                raise NotImplementedError
            given_permission = permission_klass.has_permission(
                action, current_user, request, *args, **kwargs)
            return given_permission
        return True

    def is_parent_exists(self, parent_id=None):
        """
        To check whether a parent with parent_id
        exists or not
        """
        if parent_id is None:
            return False
        try:
            self.parent = self.parent.get(**{
                'index': self.index,
                'id': parent_id
            })
            #
            # if soft_deleted then return False
            #
            if self.soft_delete.get('enabled') is True:
                if getattr(self.parent, self.soft_delete.get('on_field')) is True:
                    return False
            return True
        except Exception as e:
            return False

    def get_current_doc_type(self):
        return self.model._doc_type.name

    def get_current_index(self):
        if self.multi_tenant is False:
            return self.model._doc_type.index
        if current_identity:
            return current_identity[TENANT_FIELD]
        else:
            raise AnonymousUserException("Anynymous User not allowed")

    def is_auth_required(self, action='default'):
        """
        To return the required action authentication 
        required configuration
        """
        if ENABLE_JWT is False:
            return False
        auth = getattr(self, 'auth_required', None)
        if auth is None:
            return False
        if isinstance(auth, bool):
            return auth
        if isinstance(auth, dict):
            return auth.get(action, False)
        return False

    def get_serializer_class(self):
        """
        To return the required serializer class
        """
        # Check parser is defined
        if hasattr(self, 'parser'):
            # Check parser is defined for the action
            if self.parser.get(self.action, None) is None:
                # Check if default parser is defined
                if self.parser.get('default', None) is None:
                    raise NotImplementedError
                else:
                    if issubclass(self.parser['default'], Schema) is False:
                        raise ValueError("Invalid Serializer Specified")
                    return self.parser['default']
            # Check is subclass of schema
            if issubclass(self.parser[self.action], Schema) is False:
                raise ValueError("Invalid Serializer Specified")
            return self.parser[self.action]
        # Check seializer is defined
        if hasattr(self, 'serializer') is False:
            raise NotImplementedError
        return self.serializer

    def _save_audit_details(self, mode='create', data=None):
        """
        Will save automatically for each record on create and update events
        """
        if mode == 'create':
            data.update({
                'created_by': self.user_email,
                'created_on': datetime.now()
            })
        data.update({
            'modified_by': self.user_email,
            'modified_on': datetime.now()
        })
        return data

    def get_email_engine(self):
        """
        Will look for default email engine
        """
        try:
            from settings.dev import EMAIL_ENGINE
            from importlib import import_module
            from email_engine import EmailEngine
            email_engine = import_module(
                ".".join(EMAIL_ENGINE.split('.')[:-1]))
            eg = getattr(email_engine, EMAIL_ENGINE.split(".")[-1], None)
            if eg is None:
                raise(ValueError, "Invalid Email engine")
            if issubclass(eg, EmailEngine) is False:
                raise(ValueError, "Invalid Email Engine")
            eg_ref = eg()
            return (True, eg_ref)
        except Exception as e:
            return (False, e.__str__())

    def get(self, *args, **kwargs):
        super(GenericAPIView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        super(GenericAPIView, self).post(*args, **kwargs)

    def put(self, *args, **kwargs):
        super(GenericAPIView, self).put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(GenericAPIView, self).delete(*args, **kwargs)


class CreateAPIView(mixins.CreateModelMixin,
                    GenericAPIView):
    """
    Concrete view for creating a document instance.
    """

    def _post(self, request, *args, **kwargs):
        """
        on method 'POST'
        """
        given_permission = self.check_permission(
            'create', self.current_user, request, *args, **kwargs)

        if not given_permission:
            return abort(403, message="You're not allowed to perform this action")

        if self._parent_lookup_field in kwargs:
            return self.create_with_parent(request, *args, **kwargs)

        return self.create(request, *args, **kwargs)

    @jwt_required()
    def _jpost(self, request, *args, **kwargs):
        return self._post(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        on method 'POST'
        """
        if self.is_auth_required('create'):
            return self._jpost(request, *args, **kwargs)
        return self._post(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    """
    Concrete view for listing documents.
    """

    def _get(self, request, *args, **kwargs):
        given_permission = self.check_permission(
            'list', self.current_user, request, *args, **kwargs)
        if not given_permission:
            return abort(403, message="You're not allowed to perform this action")
        if self._parent_lookup_field in kwargs:
            return self.list_with_parent(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    @jwt_required()
    def _jget(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        on method 'GET'
        """
        if self.is_auth_required('list'):
            return self._jget(request, *args, **kwargs)
        return self._get(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
    """
    Concrete view for retrieving a document instance.
    """

    def _retrieve(self, request, *args, **kwargs):
        given_permission = self.check_permission(
            'retrieve', self.current_user, request, *args, **kwargs)
        if not given_permission:
            return abort(403, message="You're not allowed to perform this action")
        if self._parent_lookup_field in kwargs:
            return self.retrieve_with_parent(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        on method 'GET'
        """
        if self._lookup_field in kwargs:
            if self.is_auth_required('retrieve'):
                return self._jretrieve(request, *args, **kwargs)
            return self._retrieve(request, *args, **kwargs)
        return abort(404, message="Invalid Lookup")


class ListRetrieveAPIView(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin, GenericAPIView):
    """
    Concrete view for listing and retrieving document instance(s).
    """

    def _get(self, request, *args, **kwargs):
        given_permission = self.check_permission(
            'list', self.current_user, request, *args, **kwargs)
        if not given_permission:
            return abort(403, message="You're not allowed to perform this action")
        if self._parent_lookup_field in kwargs:
            return self.list_with_parent(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

    def _retrieve(self, request, *args, **kwargs):
        given_permission = self.check_permission(
            'retrieve', self.current_user, request, *args, **kwargs)
        if not given_permission:
            return abort(403, message="You're not allowed to perform this action")
        if self._parent_lookup_field in kwargs:
            return self.retrieve_with_parent(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    @jwt_required()
    def _jget(self, request, *args, **kwargs):
        return self._get(request, *args, **kwargs)

    @jwt_required()
    def _jretrieve(self, request, *args, **kwargs):
        return self._retrieve(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        """
        on method 'GET'
        """
        if self._lookup_field in kwargs:
            if self.is_auth_required('retrieve'):
                return self._jretrieve(request, *args, **kwargs)
            return self._retrieve(request, *args, **kwargs)
        else:
            if self.is_auth_required('list'):
                return self._jget(request, *args, **kwargs)
            return self._get(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyModelMixin,
                     GenericAPIView):
    """
    Concrete view for deleting a document instance.
    """

    def _delete(self, request, *args, **kwargs):
        """
        method 'DELETE'
        """
        given_permission = self.check_permission(
            'destroy', self.current_user, request, *args, **kwargs)
        if not given_permission:
            return abort(403, message="You're not allowed to perform this action")
        if self._parent_lookup_field in kwargs:
            return self.destroy_with_parent(request, *args, **kwargs)
        return self.destroy(request, *args, **kwargs)

    @jwt_required()
    def _jdelete(self, request, *args, **kwargs):
        return self._delete(request, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        on method 'DELETE'
        """
        if self.is_auth_required('delete') or self.is_auth_required('destroy'):
            return self._jdelete(request, *args, **kwargs)
        return self._delete(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateModelMixin,
                    GenericAPIView):
    """
    Concrete view for updating a document instance.
    """

    def _put(self, request, *args, **kwargs):
        """
        method 'PUT'
        """
        given_permission = self.check_permission(
            'update', self.current_user, request, *args, **kwargs)
        if not given_permission:
            return abort(403, message="You're not allowed to perform this action")

        if self._parent_lookup_field in kwargs:
            return self.update_with_parent(request, *args, **kwargs)
        return self.update(request, *args, **kwargs)

    @jwt_required()
    def _jput(self, request, *args, **kwargs):
        return self._put(request, *args, **kwargs)

    def put(self, *args, **kwargs):
        """
        method 'PUT'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        method 'PATCH'
        """
        if self.is_auth_required('update'):
            return self._jput(request, *args, **kwargs)
        return self._put(request, *args, **kwargs)


class ListCreateAPIView(ListAPIView, CreateAPIView):
    """
    Concrete view for listing documents or creating a document instance.
    """
    pass


class RetrieveUpdateAPIView(RetrieveAPIView, UpdateAPIView):
    """
    Concrete view for retrieving, updating a document instance.
    """
    pass


class RetrieveDestroyAPIView(RetrieveAPIView, DestroyAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    pass


class RetrieveUpdateDestroyAPIView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    pass
