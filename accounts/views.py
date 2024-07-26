from django.shortcuts import render,redirect
from django.views.generic import FormView
from .forms import UserRegistrationForm,UserUpdateForm
from django.contrib.auth import login,logout
from django.contrib.auth.views import LoginView , LogoutView
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def passwordChange_confirmation_email(user,subject, template):
    message = render_to_string(template, {
        'user' : user,
    })

    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

class UserPasswordChangeView(LoginRequiredMixin,PasswordChangeView):
    template_name = 'password_change_form.html'
    success_url = reverse_lazy('profile')

    def form_valid(self,form):
        form.save()
        update_session_auth_hash(self.request,form.user)
        messages.success(self.request, 'Your password updated')

        passwordChange_confirmation_email(self.request.user,"Password confirmation", "password_change_email.html")
        return super().form_valid(form)
    
class UserRegistrationView(FormView):
    template_name = 'user_registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self,form):
        print(form.cleaned_data)
        user = form.save()
        login(self.request, user)
        print(user)
        return super().form_valid(form) 
    

class UserLoginView(LoginView):
    template_name = 'user_login.html'
    def get_success_url(self):
        return reverse_lazy('home')
    
class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        return reverse_lazy('login')
    
class UserBankAccountUpdateView(View):
    template_name = 'profile.html'

    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the user's profile page
        return render(request, self.template_name, {'form': form})