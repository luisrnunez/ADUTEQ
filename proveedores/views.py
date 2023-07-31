from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor, detallesCupos
from django.contrib import messages
from django.db.models import Q
from django.views import View
from datetime import date
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger

# Create your views here.
#metodo para mostrar todos los proveedores
def proveedor(request):
    proveedores=Proveedor.objects.all().order_by('nombre')
    items_por_pagina = 10

    paginator = Paginator(proveedores, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        proveedores_paginados = paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        proveedores_paginados = paginator.get_page(1)
    return render(request,'proveedores.html', {'proveedores': proveedores_paginados})

def formRegistro(request):
    return render(request,'aggProveedor.html')


#metodo para agregar nuevos proveedores
def aggProveedor(request):
    '''nombrep=request.POST.get['nombre']
    telefonop=request.POST.get['telefono']
    RUCp=request.POST.get['ruc']
    direccionp=request.POST.get['direccion']
    comisionp=request.POST.get['comision']
    estadop=request.POST.get['estado']'''
    
    proveedor=Proveedor(nombre=request.POST['nombre'], telefono=request.POST['telefono'], direccion=request.POST['direccion'], RUC=request.POST['ruc'], comision=request.POST['comision'], cupo=request.POST['cupo'], estado=request.POST['estado'])

    if(userexist(request.POST['nombre'],request.POST['ruc'])):
        response = {
                'status': 'error',
                'message': 'Ya existe un proveedor registrado con este nombre y RUC'
            }
    else:
        if(userexistn(request.POST['nombre'])):
            response = {
                'status': 'error',
                'message': 'Ya existe un proveedor registrado con este nombre'
            }
        else:
            if(userexistr(request.POST['ruc'])):
                response = {
                'status': 'error',
                'message': 'Ya existe un proveedor registrado con este RUC'
            }
            else:
                if(userexistr(request.POST['telefono'])):
                    response = {
                    'status': 'error',
                    'message': 'Ya existe un proveedor registrado con este telefono'
                }
                else:
                    proveedor.save()
                    response = {
                    'status': 'success',
                    'message': 'Proveedor registrado correctamente.'
                    }
    return JsonResponse(response)

        #messages.warning(request,"Este proveedor ya se encuentra registrado")
        #return redirect('/proveedores')
        #messages.success(request,"Proveedor agregado correctamente")
        #return redirect('/proveedores')

    '''proveedor=Proveedor.objects.create(nombre=nombrep, telefono=telefonop, direccion=direccionp, RUC=RUCp, comision=comisionp, estado=estadop)'''

#Metodos verificar si existe o no proveedor
def userexist(nombre, ruc):
    try:
        proveedor = Proveedor.objects.get(nombre=nombre, RUC=ruc)
        return True
    except Proveedor.DoesNotExist:
        return False
 
def userexistn(nombre):
    try:
        proveedor = Proveedor.objects.get(nombre=nombre)
        return True
    except Proveedor.DoesNotExist:
        return False    
def userexistr(ruc):
    try:
        proveedor = Proveedor.objects.get(RUC=ruc)
        return True
    except Proveedor.DoesNotExist:
        return False   

def userexistl(telefono):
    try:
        proveedor = Proveedor.objects.get(telefono=telefono)
        return True
    except Proveedor.DoesNotExist:
        return False  

#metodos editar proveedores
def editProveedor(request, codigo):
    proveedor=Proveedor.objects.get(id=codigo)
    return render(request,'editProveedor.html',{
        'proveedor': proveedor
    })

def editarPro(request):
    nombrep=request.POST.get('nombre')
    telefonop=request.POST.get('telefono')
    RUCp=request.POST.get('ruc')
    direccionp=request.POST.get('direccion')
    comisionp=request.POST.get('comision')
    cupop=request.POST.get('cupo')
    estadop=request.POST.get('estado')
    #proveedor=Proveedor.objects.get(id=request.POST.get('id'))
    proveedor= get_object_or_404(Proveedor, id=request.POST.get('id'))


    if Proveedor.objects.exclude(id=request.POST.get('id')).filter(RUC=RUCp).exists():
        response = {
            'status': 'error',
            'message': 'Ya existe un proveedor registrado con este RUC'
          }
    elif Proveedor.objects.exclude(id=request.POST.get('id')).filter(nombre=nombrep).exists():
        response = {
            'status': 'error',
            'message': 'Ya existe un proveedor registrado con este nombre'
      
          }
    elif Proveedor.objects.exclude(id=request.POST.get('id')).filter(telefono=telefonop).exists():
        response = {
            'status': 'error',
            'message': 'Ya existe un proveedor registrado con este télefono'
      
          }
          

    else:
        proveedor.nombre=nombrep
        proveedor.telefono=telefonop
        proveedor.RUC=RUCp
        proveedor.direccion=direccionp
        proveedor.comision=comisionp
        proveedor.cupo=cupop
        proveedor.estado=estadop
        proveedor.save()
        response = {
            'status': 'success',
            'message': 'Datos actualizados correctamente'
            }
    return JsonResponse(response)

#metodo para eliminar a los proveedores
def deleteProveedor(request, codigo, estado):
    #proveedor=Proveedor.objects.get(id=codigo)
    #proveedor.delete()
    #return redirect('/proveedores')

    proveedor = get_object_or_404(Proveedor, id=codigo)

    if request.method == 'GET':
        # Cambiar el estado del proveedor a inactivo
        print (estado)
        if estado == 0:
            proveedor.estado = True
            proveedor.save()
            messages.success(
            request, 'El proveedor se habilitado exitosamente.')
        else:
            proveedor.estado = False
            proveedor.save()
            messages.success(
            request, 'El proveedor ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación
      

    else:
        messages.warning(request, 'El proveedor no pudo ser eliminado')

    return redirect('/proveedores')

#metodo para verificar existencia AJAX
def verificarexi(request):
    nombre = request.POST.get('nombre')
    existe = Proveedor.objects.filter(nombre=nombre).exists()
    return JsonResponse({'existe': existe})

#Barra de busqueda
def busqueda(request):
    query = request.GET.get('query', '')
    results = Proveedor.objects.filter(Q(nombre__icontains=query))
    return render(request, 'busqueda.html', {'resultados': results})

def prueba(request):
    return render(request,'prueba.html')

#----------------------------------------------------------------------------------
def presagregar_pdf(request, det_id): 
    registro_pago = detallesCupos.objects.get(id=det_id)
    if request.method == 'GET':
        return render(request,'editar_detalles_prestamo.html', {'pago_men': registro_pago}) 
    else:
        archivo_pdf = request.FILES['evidencia']
        registro_pago.evidencia=archivo_pdf
        registro_pago.save()
        return redirect('/detallescupo/' + str(detallesCupos.proveedor.id))

def verdetallescupos(request, proveedor_id):
    proveedor=Proveedor.objects.get(id=proveedor_id)
    cupos=detallesCupos.objects.filter(proveedor=proveedor)
    items_por_pagina = 10
    paginator = Paginator(cupos, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        cupos_paginados = paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        cupos_paginados = paginator.get_page(1)
    return render(request,'detalles_cupos.html', {'cupos': cupos_paginados, 'proveedor':proveedor})


def editCupos(request, codigo):
    cupos=detallesCupos.objects.get(id=codigo)
    return render(request,'editarcupos.html',{
        'cupo': cupos
    })
def editarcupos(request):
    detallecupo=get_object_or_404(detallesCupos, id=request.POST.get('id'))
    nuevocupo=request.POST.get('cupo')
    nuevafecha=date.today()
    
    detallecupo.cupo=nuevocupo
    detallecupo.fechaccupo=nuevafecha
    if (request.method == 'POST'):
        detallecupo.save()
        response = {
            'status': 'success',
            'message': 'Datos actualizados correctamente'
      
          }
    else:
        response = {
            'status': 'error',
            'message': 'Ups, algo ha salido mal'
      
          }
    return JsonResponse(response)