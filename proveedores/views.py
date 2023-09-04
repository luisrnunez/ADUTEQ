from django.shortcuts import render, redirect, get_object_or_404

from Periodo.models import Periodo
from .models import Proveedor, detallesCupos, CuentaBancaria
from django.contrib import messages
from django.db.models import Q
from django.views import View
from datetime import date
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
# Create your views here.
#metodo para mostrar todos los proveedores
def proveedor(request):
    proveedores=Proveedor.objects.filter(estado=True).order_by('nombre')
    items_por_pagina = 10

    paginator = Paginator(proveedores, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        periodo_seleccionado = Periodo.objects.filter(activo=True).first()
        proveedores_paginados = paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        proveedores_paginados = paginator.get_page(1)
    return render(request,'proveedores.html', {'proveedores': proveedores_paginados,'periodo': periodo_seleccionado})

def formRegistro(request):
    return render(request,'aggProveedor.html')


#metodo para agregar nuevos proveedores
@login_required
def aggProveedor(request):
    '''nombrep=request.POST.get['nombre']
    telefonop=request.POST.get['telefono']
    RUCp=request.POST.get['ruc']
    direccionp=request.POST.get['direccion']
    comisionp=request.POST.get['comision']
    estadop=request.POST.get['estado']'''
    
    proveedor=Proveedor(nombre=request.POST['nombre'], telefono=request.POST['telefono'], direccion=request.POST['direccion'], ruc=request.POST['ruc'], comision=request.POST['comision'], cupo=request.POST['cupo'], estado=request.POST['estado'])

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
        proveedor = Proveedor.objects.get(nombre=nombre, ruc=ruc)
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
        proveedor = Proveedor.objects.get(ruc=ruc)
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


    if Proveedor.objects.exclude(id=request.POST.get('id')).filter(ruc=RUCp).exists():
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
        proveedor.ruc=RUCp
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

    if request.method == "POST":
        criterio = request.POST.get('criterio')
        valor = request.POST.get('query')
        prov = []
        if criterio:
            # Filtrar socios según el criterio y el valor ingresados
            if criterio == 'nombres':
                prov = Proveedor.objects.filter(nombre__icontains=valor)
            elif criterio == 'telefono':
                prov = Proveedor.objects.filter(telefono__icontains=valor)
            elif criterio == 'ruc':
                prov = Proveedor.objects.filter(ruc__icontains=valor)
            elif criterio == '1':
                prov = Proveedor.objects.filter(estado=True)
            elif criterio == '0':
                prov = Proveedor.objects.filter(estado=False)
        rendered_table = render_to_string("busqueda.html", {"proveedores": prov})
        
        return JsonResponse({"rendered_table": rendered_table})

    return JsonResponse({"error": "Método no permitido"}, status=400)


def busqueda_detalles_cupos(request):
    if request.method == "POST":
        criterio = request.POST.get('criterio')
        valor = request.POST.get('query')
        detalles_cupos = []

        if criterio:
            # Filtrar detalles de cupos según el criterio y el valor ingresados
            if criterio == 'nombres':
                detalles_cupos = detallesCupos.objects.filter(socio__user__first_name__icontains=valor)
            # elif criterio == 'telefono':
            #     detalles_cupos = detallesCupos.objects.filter(socio__telefono__icontains=valor)
            # elif criterio == 'ruc':
            #     detalles_cupos = detallesCupos.objects.filter(socio__RUC__icontains=valor)
            # elif criterio == '1':
            #     detalles_cupos = detallesCupos.objects.filter(proveedor__estado=True)
            # elif criterio == '0':
            #     detalles_cupos = detallesCupos.objects.filter(proveedor__estado=False)

        rendered_table = render_to_string("table_cupos.html", {"detalles_cupos": detalles_cupos})
        return JsonResponse({"rendered_table": rendered_table})

    return JsonResponse({"error": "Método no permitido"}, status=400)

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
    
    restaurar_cupo_original = request.POST.get('restaurar_cupo') == 'on'

    if (request.method == 'POST'):
        if(restaurar_cupo_original):
            detallecupo.cupo=nuevocupo
            detallecupo.fechaccupo=nuevafecha
            detallecupo.permanente=True
        else:
            detallecupo.cupo=nuevocupo
            detallecupo.fechaccupo=nuevafecha
            detallecupo.permanente=False

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

@login_required
def agregarCuenta(request, codigo):
    try:
        proveedor = Proveedor.objects.get(id=codigo)
        cuentas = CuentaBancaria.objects.filter(proveedor=proveedor)
    except Proveedor.DoesNotExist:
        proveedor = None
        cuentas = []

    context = {
        'proveedor': proveedor,
        'cuentas': cuentas
    }

    return render(request, 'lista_cuentas_banco.html', context)

@login_required
def agregarnuevacuenta(request,codigo):


    proveedor = get_object_or_404(Proveedor, id=codigo)
    return render(request, 'agregar_cuenta.html', {'proveedor': proveedor})

def agregarnuevacuentabancaria(request,codigo):
    if request.method == 'POST':
        cuenta = CuentaBancaria(proveedor_id=codigo,banco=request.POST.get('banco')
                                ,numero_cuenta=request.POST.get('n_cuenta')
                                ,tipo_cuenta=request.POST.get('tipo')
                                ,titular_cuenta=request.POST.get('titular')
                                ,cedulaORuc=request.POST.get('cedula_ruc'))
      
        cuenta.save()
        try:
            proveedor = Proveedor.objects.get(id=codigo)
            cuentas = CuentaBancaria.objects.filter(proveedor=proveedor)
        except Proveedor.DoesNotExist:
            proveedor = None
            cuentas = []

        context = {
            'proveedor': proveedor,
            'cuentas': cuentas
        }
        messages.success(request, 'Se ha agregado una nueva cuenta')
        return render(request, 'lista_cuentas_banco.html', context)
    

def eliminarcuenta(request,codigo,prov):
    print(codigo)
    cuenta= get_object_or_404(CuentaBancaria, id=codigo)
    cuenta.delete()
    proveedor = get_object_or_404(Proveedor, id=prov)
    print(proveedor)
    print(prov)
    try:
        proveedor = Proveedor.objects.get(id=prov)
        cuentas = CuentaBancaria.objects.filter(proveedor=proveedor)
    except Proveedor.DoesNotExist:
        proveedor = None
        cuentas = []

    context = {
        'proveedor': proveedor,
        'cuentas': cuentas
    }
    messages.success(request, 'Se ha eliminado correctamente esta cuenta bancaria')
    return render(request, 'lista_cuentas_banco.html', context)