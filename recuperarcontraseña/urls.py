from django.urls import include, path

from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from .views import CustomPasswordResetConfirmView, CustomPasswordResetDoneView, CustomPasswordResetCompleteView

urlpatterns = [

    #recuperar cuenta por correo
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('admin/', admin.site.urls),
    # path('reset-password/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    # path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<str:uidb64>/<str:token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    
]