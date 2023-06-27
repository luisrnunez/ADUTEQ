from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from . import models




# Create your views here.

def login_(request):
    return render(request,"login.html")

def Principal(request):
    return render(request,"emp_principal.html")

def Autenticacion_usuarios(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('principal') # redirige a la página de inicio después del inicio de sesión exitoso
        else:
           # messages.warning(request,"Usuario o contraseña incorrecto, porfavor ingrese de nuevo")
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrecto, porfavor ingrese de nuevo'})
    else:
        return render(request, 'login.html')

def guardar_socio(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        usuario = request.POST.get('usuario')
        password = request.POST.get('password')
        cedula = request.POST.get('cedula')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        lugar_nacimiento = request.POST.get('lugar_nacimiento')
        correo_electronico = request.POST.get('correo_electronico')
        numero_telefonico = request.POST.get('numero_telefonico')
        numero_convencional = request.POST.get('numero_convencional')
        direccion_domiciliaria = request.POST.get('direccion_domiciliaria')
        facultad = request.POST.get('facultad')
        categoria = request.POST.get('categoria')
        dedicacion_academica = request.POST.get('dedicacion_academica')
        fecha_ingreso = request.POST.get('fecha_ingreso')
        titulo = request.POST.get('titulo')
        aporte = request.POST.get('aporte')
        foto = request.FILES['foto'] if 'foto' in request.FILES else None

        # Convertir la foto a una secuencia de bytes
        foto_bytes = foto.read() if foto else None
        #foto = request.FILES.get('foto')  # Si se está enviando un archivo

        # Crear una instancia del modelo Socio y guardar los datos en la base de datos
        socio = models.Socios(usuario=usuario,password=password,cedula=cedula, nombres=nombres, apellidos=apellidos, fecha_nacimiento=fecha_nacimiento,
                      lugar_nacimiento=lugar_nacimiento, correo_electronico=correo_electronico,
                      numero_telefonico=numero_telefonico, numero_convencional=numero_convencional,
                      direccion_domiciliaria=direccion_domiciliaria, facultad=facultad, categoria=categoria,
                      dedicacion_academica=dedicacion_academica, fecha_ingreso=fecha_ingreso, titulo=titulo, aporte=aporte,
                      foto=foto_bytes)

        # Guardar el objeto Socio en la base de datos
        socio.save()

        # Redirigir a una página de éxito o mostrar un mensaje de éxito
        return redirect('listar_socios')

    # Si no es una solicitud POST, renderizar el formulario
    return render(request, 'emp_agg_socios.html')



def editar_socio(request, socio_id):
    socio = get_object_or_404(models.Socios, id=socio_id)
    
    if request.method == 'POST':
        socio.usuario = request.POST.get('usuario')
        socio.password = request.POST.get('password')
        socio.cedula = request.POST.get('cedula')
        socio.nombres = request.POST.get('nombres')
        socio.apellidos = request.POST.get('apellidos')
        socio.fecha_nacimiento = request.POST.get('fecha_nacimiento')
        socio.lugar_nacimiento = request.POST.get('lugar_nacimiento')
        socio.correo_electronico = request.POST.get('correo_electronico')
        socio.numero_telefonico = request.POST.get('numero_telefonico')
        socio.numero_convencional = request.POST.get('numero_convencional')
        socio.direccion_domiciliaria = request.POST.get('direccion_domiciliaria')
        socio.facultad = request.POST.get('facultad')
        socio.categoria = request.POST.get('categoria')
        socio.dedicacion_academica = request.POST.get('dedicacion_academica')
        socio.fecha_ingreso = request.POST.get('fecha_ingreso')
        socio.titulo = request.POST.get('titulo')
        socio.aporte = request.POST.get('aporte')
        socio.foto = request.FILES['foto'] if 'foto' in request.FILES else None

        # Convertir la foto a una secuencia de bytes
        foto_bytes = socio.foto.read() if socio.foto else None
        #foto = request.FILES.get('foto')  # Si se está enviando un archivo
        # Guardar el objeto Socio en la base de datos
        socio.save()

        messages.success(request,'Se ha guardado correctamente este socio')
        return redirect('listar_socios')
    else:
        return render(request, 'emp_edit_socios.html', {'socio': socio})

    

def eliminar_socio(request, socio_id):
    socio = get_object_or_404(models.Socios, id=socio_id)
    
    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        socio.activo = False
        socio.save()

        # Agregar un mensaje de confirmación
        messages.success(request, 'El socio ha sido dado de baja exitosamente.')
       
    else: 
        messages.warning(request, 'El socio no pudo ser eliminado')

    return redirect('listar_socios')


def Recuperar_cuenta(request):
    return render(request,"recuperar_contra.html")

def ListaSocios(request):
    socios = models.Socios.objects.all()
    return render(request,"emp_socios.html", {'socios': socios})

def AggSocio(request):
    return render(request,"emp_agg_socios.html")

