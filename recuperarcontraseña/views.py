from django.shortcuts import render
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .forms import CustomSetPasswordForm, CustomPasswordResetForm
from django.contrib.auth.models import User

# Create your views here.

class CustomPasswordResetView(PasswordResetView):
    template_name = 'recuperar_contra.html'
    html_email_template_name = 'correo.html'
    form_class = CustomPasswordResetForm

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'restablecer_pass.html'
    form_class = CustomSetPasswordForm

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
