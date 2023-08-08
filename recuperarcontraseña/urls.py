from django.urls import include, path

from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from .views import CustomPasswordResetConfirmView, CustomPasswordResetDoneView, CustomPasswordResetCompleteView,recuperar_contra

urlpatterns = [

    #recuperar cuenta por correo
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('admin/', admin.site.urls),
    # path('reset-password/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    # path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/confirm/<str:uid>/<str:token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('recuperacion/envio/', recuperar_contra, name='recuperar_contra'),
    path('restablecer/<str:user_id>/<str:token>/', views.restablecer_contra, name='restablecer_contra'),
    path('restablecer/<str:user_id>/<str:token>/nueva/', views.restablecer_contra_nueva, name='restablecer_contra_nueva'),
    
]