from rest_framework import permissions


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        userGroup = request.user.groups.all()
        if userGroup.filter(name="client").exists():
            return True
        return False
        
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        userGroup = request.user.groups.all()
        if userGroup.filter(name="manager").exists():
            return True
        return False

class IsLivrer(permissions.BasePermission):
    def has_permission(self, request, view):
        userGroup = request.user.groups.all()
        if userGroup.filter(name="livreur").exists():
            return True
        return False