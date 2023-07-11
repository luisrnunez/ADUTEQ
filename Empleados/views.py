import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from . import models
from .models import Empleado
# Create your views here.


def listar_empleados(request):
    empleados = models.Empleado.objects.all()
    return render(request, "lista_empleados.html", {'empleados': empleados})


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



def eliminar_empleado(request, empleado_id, valor):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        print (valor)
        if valor == 0:
            empleado.activo = True
            empleado.save()
            messages.success(
            request, 'El empleado se habilitado exitosamente.')
        else:
            empleado.activo = False
            empleado.save()
            messages.success(
            request, 'El empleado ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación
      

    else:
        messages.warning(request, 'El socio no pudo ser eliminado')

    return redirect('listar_empleados')

def agg_empleado(request):
    return render(request, "agg_empleados.html")

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
        user = User.objects.create_user(username=username, password=password,is_superuser='True')

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

