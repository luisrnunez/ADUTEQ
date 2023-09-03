from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import PagosProveedor
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Periodo
from django.template.loader import render_to_string
# Create your views here.
@login_required
def lista_pagosp(request):

    # Obtener todos los períodos el año del periodo
    periodos = Periodo.objects.all() 
    anos = periodos.values_list('anio', flat=True).distinct()

    #obtener la lista de pagos por el select(periodo)
    periodoid = request.POST.get('periodoid')
    fechas_periodo = {}
    if periodoid:
        periodo_seleccionado = Periodo.objects.filter(id=periodoid).first()
        print(periodo_seleccionado)
        if periodo_seleccionado:
            fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
           
            print(periodo_seleccionado)
            pagosproveedor = PagosProveedor.objects.filter(fecha_creacion__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("proveedor","fecha_creacion")
            context = {
                'pagosproveedor': pagosproveedor,
                    'periodos': periodos,
                    'anos': anos,
                    'fechas_periodo': fechas_periodo,
                    'periodo_seleccionado': periodo_seleccionado,
            }
            rendered_table = render_to_string("listar_pagosp_partial.html",context)
            return JsonResponse({"rendered_table": rendered_table})
    
    #lista de pagos del periodo actual
    try:
        periodo_seleccionado = Periodo.objects.filter(activo=True).first()
        fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
        pagosproveedor = PagosProveedor.objects.filter(fecha_creacion__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("proveedor","fecha_creacion")
        
    except:
        if periodo_seleccionado == None:
            pagosproveedor = {}
    context = {
                    'pagosproveedor': pagosproveedor,
                    'periodos': periodos,
                    'anos': anos,
                    'fechas_periodo': fechas_periodo,
                    'periodo_seleccionado': periodo_seleccionado,
            }
    return render (request,'listar_pagosp.html',context)


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

    return redirect('/listar_pagosp/')


def presagregar_pdf(request, det_id): 
    pagop = PagosProveedor.objects.get(id=det_id)
    if request.method == 'GET':
        return render(request,'subir_evidencia_prov.html', {'pagop': pagop}) 
    else:
        archivo_pdf = request.FILES['evidencia']
        pagop.evidencia=archivo_pdf
        pagop.save()
        return redirect('/listar_pagosp/')
