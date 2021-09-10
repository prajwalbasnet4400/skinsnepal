from django.contrib.auth.views import (LoginView,LogoutView,PasswordChangeView,
                                        PasswordChangeDoneView,PasswordResetView,PasswordResetConfirmView,
                                        PasswordResetDoneView,PasswordResetCompleteView)
from django.shortcuts import redirect, render
from django.views.generic.base import View
from django.views.generic.edit import FormView
from .forms import RegisterForm
class Login(LoginView):
    pass

class Logout(LogoutView):
    pass
class PasswordChange(PasswordChangeView):
    pass

class PasswordChangeDone(PasswordChangeDoneView):
    pass

class PasswordReset(PasswordResetView):
    pass

class PasswordResetConfirm(PasswordResetConfirmView):
    pass

class PasswordResetDone(PasswordResetDoneView):
    pass

class PasswordResetComplete(PasswordResetCompleteView):
    pass

class Signup(View):
    template_name = 'registration/signup.html'
    form_class = RegisterForm
    success_url = '/'

    def get(self,request,*args, **kwargs):
        ctx = {}
        ctx['form'] = self.form_class()
        return render(request,self.template_name,ctx)
    
    def post(self,request,*args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
        else:
            print('invalid form')
        
        return redirect('signup')