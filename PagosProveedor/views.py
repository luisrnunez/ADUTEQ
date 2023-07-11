from datetime import date
from django.shortcuts import get_object_or_404, redirect, render
from .models import PagosProveedor
from django.contrib import messages
# Create your views here.
def lista_pagosp(request):
    pagosproveedor = PagosProveedor.objects.all()
    return render (request,'listar_pagosp.html', {'pagosproveedor' : pagosproveedor})


def aplicar_pago(request, PagosProveedor_id, valor):
    pagosproveedor = get_object_or_404(PagosProveedor, id=PagosProveedor_id)

    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        if valor == 0:
            pagosproveedor.valor_cancelado = True
            pagosproveedor.fecha_pago = date.today()
            pagosproveedor.save()
            messages.success(
            request, 'Se ha registrado el pago al proveedor exitosamente.')
        #else:
            #pagosproveedor.activo = False
            #pagosproveedor.save()
            #messages.success(
            #request, 'El socio ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación

    else:
        messages.warning(request, 'El pago no pudo ser procesado')

    return redirect('lista_pagosp')