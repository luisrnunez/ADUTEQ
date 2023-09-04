import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Periodo
from . import models
from .models import Empleado
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib.auth import update_session_auth_hash
# Create your views here.

@login_required
def listar_empleados(request):
    empleados = models.Empleado.objects.all().order_by('nombres')
    items_por_pagina = 8
    paginator = Paginator(empleados, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        periodo_seleccionado = Periodo.objects.filter(activo=True).first()
        empleados_pag=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        empleados_pag=paginator.get_page(1)
    return render(request, "lista_empleados.html", {'empleados': empleados_pag,'periodo': periodo_seleccionado})

@login_required
def editar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)
    user = empleado.user
    if request.method == 'POST':
        empleado.username = request.POST.get('username')
        password = request.POST['password']
        if password:
            user.set_password(password)
        empleado.cedula = request.POST.get('cedula')
        empleado.nombres = request.POST.get('nombres')
        empleado.apellidos = request.POST.get('apellidos')
        empleado.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        empleado.correo_electronico = request.POST.get('correo_electronico')
        empleado.numero_telefonico = request.POST.get('numero_telefonico')
        empleado.direccion_domiciliaria = request.POST.get('direccion_domiciliaria')
        empleado.fecha_ingreso = request.POST.get('fecha_ingreso')
        empleado.titulo = request.POST.get('titulo')

        if User.objects.exclude(id=empleado.user_id).filter(username=empleado.username).exists():
            messages.warning(request, 'El nombre de usuario ya está registrado')
            return render(request, 'edit_empleados.html', {'empleado': empleado})
        if Empleado.objects.exclude(id=empleado_id).filter(cedula=empleado.cedula).exists():
            messages.warning(request, 'El número de cédula ya está registrado')
            return render(request, 'edit_empleados.html', {'empleado': empleado})
        if Empleado.objects.exclude(id=empleado_id).filter(cedula=empleado.correo_electronico).exists():
            messages.warning(request, 'El correo ya está registrado')
            return render(request, 'edit_empleados.html', {'empleado': empleado})
        if Empleado.objects.exclude(id=empleado_id).filter(cedula=empleado.numero_telefonico).exists():
            messages.warning(request, 'El número de telefono ya está registrado')
            return render(request, 'edit_empleados.html', {'empleado': empleado})

        user.save()
        empleado.save()

        messages.success(request, 'Se ha guardado correctamente este socio')
        return redirect('listar_empleados')
    else:
        return render(request, 'edit_empleados.html', {'empleado': empleado})


@login_required
def eliminar_empleado(request, empleado_id, valor):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        print (valor)
        if valor == 0:
            empleado.activo = True
            empleado.user.is_active=True
            empleado.save()
            empleado.user.save()
            messages.success(
            request, 'El empleado se habilitado exitosamente.') 
        else:
            empleado.activo = False
            empleado.user.is_active=False
            empleado.save()
            empleado.user.save()
            messages.success(
            request, 'El empleado ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación
      

    else:
        messages.warning(request, 'El socio no pudo ser eliminado')

    return redirect('listar_empleados')

@login_required
def agg_empleado(request):
    return render(request, "agg_empleados.html")

@login_required
def guardar_empleado(request):
    if request.method == 'POST':

      
        
        # Obtener los datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')
        cedula = request.POST.get('cedula')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        correo_electronico = request.POST.get('correo_electronico')
        numero_telefonico = request.POST.get('numero_telefonico')
        direccion_domiciliaria = request.POST.get('direccion_domiciliaria')
        fecha_ingreso = request.POST.get('fecha_ingreso')
        titulo = request.POST.get('titulo')
    
        

        #    Validaciones
        if User.objects.filter(username=username).exists():
            
            messages.warning(request, 'El usuario ya está registrado')
            return render(request, 'agg_empleados.html', {'empleado': request.POST})
        
        if not validar_cedula(cedula):
            messages.warning(
                request, 'La cédula ingresada ya está registrada')
        
            return render(request, 'agg_empleados.html', {'empleado': request.POST})

        if not validar_numero(numero_telefonico):
            
            messages.warning(
                request, 'El numero telefonico ingresado ya está registrada')
            return render(request, 'agg_empleados.html', {'empleado':  request.POST})

        # Validar la fecha de nacimiento
        if not validar_fecha_nacimiento(fecha_nacimiento):
          
            messages.warning(request, 'La fecha de nacimiento ingresada no es válida')
            return render(request, 'agg_empleados.html', {'empleado': request.POST})
        # Validar el correo electrónico
        if not validar_correo_electronico(correo_electronico):
           
            messages.warning(request, 'El correo electrónico ingresado no es válido')
            return render(request, 'agg_empleados.html', {'empleado': request.POST})
        # Crear el usuario
        user = User.objects.create_user(username=username, password=password,is_staff='True')

        # Crear el objeto Empleado
        empleado = Empleado(user=user, cedula=cedula, nombres=nombres, apellidos=apellidos,
                            fecha_nacimiento=fecha_nacimiento, correo_electronico=correo_electronico,
                            numero_telefonico=numero_telefonico, direccion_domiciliaria=direccion_domiciliaria,
                            fecha_ingreso=fecha_ingreso, titulo=titulo, activo='True')

       
        # Guardar el empleado en la base de datos
        empleado.save()
        messages.success(request, 'Se ha agregado un nuevo empleado')

        # Redirigir a la página deseada después de guardar los datos
        return redirect('listar_empleados')

    return render(request, 'lista_empleados.html')


def validar_cedula(cedula):
    # Verificar si ya existe un socio con la misma cédula
    try:
        Empleado.objects.get(cedula=cedula)
        return False
    except Empleado.DoesNotExist:
        return True
    
def validar_usuario(usuario):
    # Verificar si ya existe un socio con la misma cédula
    try:
        User.objects.get(usuario=usuario)
        return False
    except User.DoesNotExist:
        return True
    
def validar_numero(numero_telefonico):
    # Verificar si ya existe un socio con la misma cédula
    try:
        Empleado.objects.get(numero_telefonico=numero_telefonico)
        return False
    except Empleado.DoesNotExist:
        return True

def validar_fecha_nacimiento(fecha_nacimiento):
    # Verificar si la fecha de nacimiento es una fecha válida
    try:
        datetime.datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        
        return True
    except ValueError:
        return False

def validar_correo_electronico(correo_electronico):
    # Verificar si el correo electrónico tiene un formato válido
    try:
        Empleado.objects.get(correo_electronico=correo_electronico)
        return False
    except Empleado.DoesNotExist:
        return True

def restablecer_contra_emp(request):
    try:
        usuario_id = request.POST.get('user_id')
        print('usuario: ',usuario_id)
        user = User.objects.get(pk=usuario_id)
    except User.DoesNotExist:
        user = None
    passs = request.POST.get('password_old')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    contras = {
                'password_old': passs,
                'password': password,
                'confirm_password': confirm_password 
            }
    if user.check_password(passs):      
        if request.method == 'POST':

            if password != confirm_password:
                 error_message = 'Las contraseñas no coinciden. Inténtalo de nuevo.'
            else:
                user.set_password(password)
                user.save()
                #update_session_auth_hash(request, user)
                return render(request, 'restablecer_contra_emp.html', {'message': 'Se ha cambiado correctamente la contraseña, porfavor entre de nuevo.'})

        return render(request, 'restablecer_contra_emp.html', {'error_message': error_message, 'contras': contras})
    else:
        error_message = 'La contraseña actual no es correcta'
        return render(request, 'restablecer_contra_emp.html', {'error_message': error_message,'contras': contras})

    


    
@login_required
def actualizar_contra(request):
    return render(request, "restablecer_contra_emp.html")

@login_required
def info_empleado(request,empleado_id):
    print(empleado_id)
    empleado = get_object_or_404(Empleado, id=empleado_id)
    return render(request, 'edit_empleados_perfil.html', {'empleado': empleado})

@login_required
def editar_perfil(request):
   
    if request.method == 'POST':
        empleado_id = request.POST.get('user_id')
        empleado = get_object_or_404(Empleado, id=empleado_id)
        user = empleado.user
        empleado.username = request.POST.get('username')
        empleado.cedula = request.POST.get('cedula')
        empleado.nombres = request.POST.get('nombres')
        empleado.apellidos = request.POST.get('apellidos')
        empleado.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        empleado.correo_electronico = request.POST.get('correo_electronico')
        empleado.numero_telefonico = request.POST.get('numero_telefonico')
        empleado.direccion_domiciliaria = request.POST.get('direccion_domiciliaria')
        empleado.fecha_ingreso = request.POST.get('fecha_ingreso')
        empleado.titulo = request.POST.get('titulo')

        if User.objects.exclude(id=empleado.user_id).filter(username=empleado.username).exists():
            messages.warning(request, 'El nombre de usuario ya está registrado')
            return render(request, 'edit_empleados_perfil.html', {'empleado': empleado})
        if Empleado.objects.exclude(id=empleado_id).filter(cedula=empleado.cedula).exists():
            messages.warning(request, 'El número de cédula ya está registrado')
            return render(request, 'edit_empleados_perfil.html', {'empleado': empleado})
        if Empleado.objects.exclude(id=empleado_id).filter(cedula=empleado.correo_electronico).exists():
            messages.warning(request, 'El correo ya está registrado')
            return render(request, 'edit_empleados_perfil.html', {'empleado': empleado})
        if Empleado.objects.exclude(id=empleado_id).filter(cedula=empleado.numero_telefonico).exists():
            messages.warning(request, 'El número de telefono ya está registrado')
            return render(request, 'edit_empleados_perfil.html', {'empleado': empleado})

        user.save()
        empleado.save()

        messages.success(request, 'Se ha guardado correctamente la informacion de perfil')
        return redirect(f'/perfil/{empleado_id}/')

    

