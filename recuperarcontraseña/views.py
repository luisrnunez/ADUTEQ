from base64 import urlsafe_b64encode
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from numpy import vectorize

from ADUTEQ import settings
from .forms import CustomSetPasswordForm, CustomPasswordResetForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.contrib import messages
from django.urls import reverse_lazy
from Empleados.models import Empleado
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
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
            print(uid)
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


def recuperar_contra(request):
    print('dentro de la funcion')
    if request.method == 'POST':
        email = request.POST.get('email')
        print(email)
        if Empleado.objects.filter(correo_electronico=email).exists():
            # Generar el token de restablecimiento de contraseña
            emp = Empleado.objects.get(correo_electronico=email)
            emp_id = emp.user_id
            user = User.objects.get(id=emp_id)
            user_id = user.id
            print(user_id)
            print('Id del empleado: ',user_id)
            token_generator = default_token_generator
            token = token_generator.make_token(user)
            # Enviar el correo electrónico con el enlace que incluye el token
            subject = 'Recuperación de Contraseña'
            message = f'Hola, has solicitado un cambio de contraseña. Haz clic en el siguiente enlace para restablecer tu contraseña:\n\n'
            message += f'{settings.BASE_URL}/restablecer/{user_id}/{token}/\n\n'
            
            message += 'Si no realizaste esta solicitud, ignora este correo.\n\n'
            message += 'Gracias.\n'
            from_email = 'tu_correo@example.com'  # Reemplaza esto con tu dirección de correo electrónico
            send_mail(subject, message, from_email, [email], fail_silently=False)

            return render(request, 'recuperar_contra.html',{'email_exists': True})
        else:
            return render(request, 'recuperar_contra.html', {'email_exists': False})

    else:  
        print('get')
        return render(request, 'recuperar_contra.html')


def restablecer_contra(request, user_id, token):
    try:
        print('id del user: ', user_id)
        print('token: ', token)
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Token y uidb64 son válidos, renderizar la página de restablecimiento de contraseña.
        return render(request, 'restablecer_contra.html', {'user_id': user_id, 'token': token})
    else:
        # Token o uidb64 no son válidos, redirigir a una página de error o mostrar un mensaje.
        print('error')
        error_message = 'El enlace de restablecimiento de contraseña no es válido.'
        return render(request, 'error_.html', {'error_message': error_message})
    
def restablecer_contra_nueva(request, user_id, token):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        user = None
    print('id del user: ', user_id)
    print('token: ', token)
    print('Dentro de la funcion')
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                 error_message = 'Las contraseñas no coinciden. Inténtalo de nuevo.'
            else:
                user.set_password(password)
                user.save()
                return render(request, 'restablecer_contra.html', {'user_id': user_id, 'token': token,'message': 'Se ha cambiado correctamente la contraseña, ahora ya puede cerrar la pagina'})

        return render(request, 'restablecer_contra.html', {'user_id': user_id, 'token': token, 'error_message': error_message})
    else:
        error_message = 'El enlace de restablecimiento de contraseña no es válido.'
        return render(request, 'error_.html', {'error_message': error_message})
