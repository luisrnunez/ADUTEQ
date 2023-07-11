from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .forms import CustomSetPasswordForm, CustomPasswordResetForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.urls import reverse_lazy

# Create your views here.

class CustomPasswordResetView(PasswordResetView):
    template_name = 'recuperar_contra.html'
    html_email_template_name = 'correo.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'restablecer_pass.html'

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64).decode())
            user = self.get_user(uid)
            if default_token_generator.check_token(user, token):
                form = SetPasswordForm(user)
                context = {
                    'form': form,
                    'uidb64': uidb64,
                    'token': token,
                }
                return render(request, self.template_name, context)
            else:
                messages.error(request, 'El enlace de restablecimiento de contraseña no es válido.')
        except (TypeError, ValueError, OverflowError):
            messages.error(request, 'El enlace de restablecimiento de contraseña no es válido.')
            print(uid)
            print(token)
        return redirect('password_reset')
    # form_class = CustomSetPasswordForm

    def get_user(self, uid):
        try:
            return User.objects.get(id=uid)
        except User.DoesNotExist:
            return None
        
    def post(self, request, uidb64, token):
        form = SetPasswordForm(self.get_user(uidb64), request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('login')
        else:
            messages.error(request, 'Hubo un error al cambiar la contraseña. Por favor, intenta nuevamente.')
        return render(request, self.template_name, {'restablecer_pass': form})
    


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'
