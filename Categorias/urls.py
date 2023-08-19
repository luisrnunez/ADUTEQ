from django.urls import path
from .views import lista_categorias,agregar_categoria,eliminar_categoria,editar_categoria

urlpatterns = [
    path('',lista_categorias),
    path('nueva/',agregar_categoria),
    path('eliminar/<int:cat_id>/', eliminar_categoria,name='eliminarcat'),
    path('editar/<int:cat_id>/', editar_categoria,name='editarcat')
]