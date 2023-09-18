from datetime import date
import datetime
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Periodo
from .models import AjustesSistema
# Create your views here.

@login_required
def mostrar_ajustes(request):
    periodos_activos = Periodo.objects.filter(activo=True)
    
    if periodos_activos:
        periodo_actual = periodos_activos[0]
        dias_restantes = (periodo_actual.fecha_fin - date.today()).days
    else:
        periodo_actual = None
        dias_restantes = None
    ajustes, created = AjustesSistema.objects.get_or_create(defaults={'periodoAutomatico': True})
    context = {
        'periodo': periodo_actual,
        'dias_restantes': dias_restantes,
        'ajustes' : ajustes
    }
    
    return render(request, 'ajustes_sistema.html', context)


@login_required
def agregar_periodo(request):
    print('entra a funcion')
    if request.method == 'POST':
        print('POST')
        anio = request.POST.get('anio')
        nombre = request.POST.get('nombre')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        descripcion = request.POST.get('descripcion')
        print(anio)
        print(fecha_inicio)
        # Crear un nuevo objeto Periodo y guardarlo en la base de datos
        periodo = Periodo(anio=anio, nombre=nombre, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, descripcion=descripcion)
        periodo.save()
        
        return JsonResponse({'mensaje': 'El período se agregó exitosamente.'})
    return render(request, 'agregar_periodo.html')


@login_required
def cerrar_periodo(request):
    try:
        codigo = request.POST.get('codigo')
        periodo = Periodo.objects.get(id=codigo)
        periodo.activo = False
        periodo.save()

        
        return JsonResponse({'success': True})
    except Periodo.DoesNotExist:
        return JsonResponse({'success': False})
    

@login_required
def guardar_cierre_automatico(request):
    if request.method == 'POST' :
        cierre_automatico = request.POST.get('cierre_automatico')
        ajustes, created = AjustesSistema.objects.get_or_create(defaults={'periodoAutomatico': True})
        
        if cierre_automatico == 'si':
            ajustes.periodoAutomatico = True
        else:
            ajustes.periodoAutomatico = False
        ajustes.save()
        response = { 'periodoAutomatico' : ajustes.periodoAutomatico }
        return JsonResponse(response)
    return JsonResponse({'message': 'Error en la solicitud AJAX.'}, status=400)
