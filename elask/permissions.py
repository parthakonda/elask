

class Permission(object):

    def has_permission(self, request, *args, **kwargs):
        raise NotImplementedError


class PermissionNotFoundException(Exception):
    pass


class AnonymousUserException(Exception):
    pass