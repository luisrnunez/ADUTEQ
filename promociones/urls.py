from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [ 
    path('promociones/', views.ListaPromociones),
    path('habilitar_desabilitar/<int:promo_id>/<int:valor>/', views.habilitar_desabilitar_promocion, name='hab_des' ),

    path('resultados/', views.obtener_resultados, name='resultados'),

    path('aggpromo/', views.formRegistro, name='aggpromo' ),
    path('agregarpromo/', views.aggPromo, name='agregarpromo' ),

    path('editpromo/<int:promo_id>', views.editar_promo, name='editpromo' ),
    path('eliminarpromo/<int:promo_id>/', views.eliminarpromo, name='eliminarpromo'),

    path('enviar_promocion_a_todos/<int:promo_id>/', views.enviar_promocion_a_todos, name='enviar_promocion_a_todos'),

    path('buscar_promos/', views.buscar_promo, name='buscar_promos'),
    path('buscar_proveedores/', views.buscar_proveedores, name='buscar_proveedores'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
