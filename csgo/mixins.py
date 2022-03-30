from django.contrib.auth.mixins import LoginRequiredMixin

class IsOwnerMixin(LoginRequiredMixin):
    """
        Check if the object in the view belongs to the currently
        logged in user. Object must have get_owner() function that
        returns a user object.s
    """
    def get_object(self,*args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if self.request.user != obj.get_owner():
            raise self.handle_no_permission()
        else:
            return obj