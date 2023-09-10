import datetime
from gettext import translation
from ipaddress import summarize_address_range
import re
import datetime
import re
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from socios.models import Socios
from django.utils import timezone
from django.contrib.auth.models import User
from django.views import View
from socios.models import Socios, Aportaciones
from django.utils import timezone
from django.contrib.auth.models import User
from . import models
from django.core.paginator import Paginator, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils import timezone
from django.views.decorators.cache import cache_control

from django.core.mail import send_mail
from .models import AjustesSistema
from django.template.loader import render_to_string
from .models import Periodo
# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_(request):
    return render(request, "login.html")

def is_superuser_or_staff(user):
    return user.is_superuser or user.is_staff


class SinAccesoView(View):
    def get(self, request):
        mensaje = "Lo siento, no tienes acceso."
        # messages.warning(request, mensaje)
        return render(request, 'login.html', {'mensaje': mensaje})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cerrar_sesion(request):
    logout(request)
    return render(request, 'login.html')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cerrar_sesion(request):
    logout(request)
    return render(request, 'login.html')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Principal(request):
    try:
        ajustes, created = AjustesSistema.objects.get_or_create(defaults={'periodoAutomatico': True})
        periodo = Periodo.objects.get(activo=True)
        fecha_actual = timezone.now().date()
        if ajustes.periodoAutomatico and periodo.fecha_fin < fecha_actual:
            
            fechaCierre = periodo.fecha_fin 
            mes = fechaCierre.month
            anio = fechaCierre.year
            import calendar
            import locale
            locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
            nombreMes = calendar.month_name[mes+1].capitalize().upper()
            periodoNuevo = Periodo(anio=periodo.anio, nombre=nombreMes, fecha_inicio=periodo.fecha_fin, fecha_fin=f'{anio}-{mes+1}-{ajustes.dia_cierre}')
            periodoNuevo.save()

            # dar de baja al periodo pasado
            periodo.activo = False
            periodo.save()
            messages.warning(request,'Se ha cerrado automaticamente el periodo actual, nota: si desea que no se cierre automaticamente vaya a ajustes')
        if  periodo.fecha_fin == fecha_actual:
            messages.warning(request,'El periodo actual se cerrara mañana automaticamente, si no desea esta accion vaya a ajustes!')
    except :
        messages.warning(request,'No se encuentra registrado un periodo porfavor vaya ajustes.') 
        periodo={}
    return redirect('/principal/resumen/')
    # return render(request, "principal.html",{'periodo': periodo})


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def PanelActividades(request):
    try:
        periodo_seleccionado = Periodo.objects.filter(activo=True).first()
        if periodo_seleccionado:
            return render(request, "emp_actividades.html",{'periodo': periodo_seleccionado})
        else:
            messages.warning(request, 'Para poder realizar transaciones agregue un nuevo periodo')
            return render(request, "base.html",{'periodo': periodo_seleccionado})
    except:
        messages.warning(request,'No se encuentra registrado un periodo porfavor vaya ajustes.')
        return render(request, "emp_actividades.html")
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Autenticacion_usuarios(request):

    # if request.user.is_authenticated:
    #     return redirect('principal')

    try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            print(username, password, user)
            if user is not None:
                login(request, user)
                # redirige a la página de inicio después del inicio de sesión exitoso
                return redirect('principal')
            else:
            
                return render(request, 'login.html',{'error_message': 'Usuario o contraseña incorrecto, porfavor ingrese de nuevo'})
        else:
            return render(request, 'login.html')
    except:
            messages.warning(request, 'Actualiza la pagina por favor')
            return redirect('login.html')


from django.db import transaction
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def guardar_socio(request):

    try:
        with transaction.atomic():
            if request.method == 'POST':
                username = request.POST.get('username')
                password = request.POST.get('password')
                cedula = request.POST.get('cedula')
                first_name = request.POST.get('first_name')
                last_name = request.POST.get('last_name')
                fecha_nacimiento = request.POST.get('fecha_nacimiento')
                lugar_nacimiento = request.POST.get('lugar_nacimiento')
                email = request.POST.get('email')
                numero_telefonico = request.POST.get('numero_telefonico')
                numero_convencional = request.POST.get('numero_convencional')
                direccion_domiciliaria = request.POST.get('direccion_domiciliaria')
                facultad = request.POST.get('facultad')
                categoria = request.POST.get('categoria')
                dedicacion_academica = request.POST.get('dedicacion_academica')
                titulo = request.POST.get('titulo')
                aporte = request.POST.get('aporte')


                if 'foto' in request.FILES:
                    foto = request.FILES['foto']
                else:
                    foto=""

                user = User(username=username,password=password, email=email, first_name=first_name, last_name=last_name)
                
                valor = False;   
                if User.objects.filter(username=username).exists():
                        messages.warning(
                            request, 'El nombre de usuario ya está registrado')
                        valor = True
                if Socios.objects.filter(cedula=cedula).exists():
                        messages.warning(
                            request, 'El número de cédula ya está registrado')
                        valor = True
                if User.objects.filter(email=email).exists():
                        messages.warning(
                            request, 'El correo ya está registrado, ingrese otro')
                        valor = True
                if Socios.objects.filter(numero_telefonico=numero_telefonico).exists():
                        messages.warning(
                            request, 'El número de telefono ya está registrado')
                        valor = True
                if Socios.objects.filter(numero_convencional=numero_convencional).exists():
                        messages.warning(
                            request, 'El número de convencional ya está registrado')
                        valor = True

                if valor == True:
                    ListaDatos = carga_datos_html()
                    ListaDatos.update( {
                                    'socio': request.POST,'usuario': user
                                })
                    return render(request, 'emp_agg_socios.html', ListaDatos)

                user = User.objects.create_user(username=username,password=password, email=email,
                                    last_login=timezone.now().date(),
                                    is_superuser=False, first_name=first_name, last_name=last_name,
                                    is_staff=False, is_active=True, date_joined=timezone.now().date())
                
                socios = Socios(user=user,cedula=cedula, fecha_nacimiento=fecha_nacimiento,lugar_nacimiento=lugar_nacimiento,
                                    numero_telefonico=numero_telefonico,numero_convencional=numero_convencional, direccion_domiciliaria=direccion_domiciliaria,
                                    categoria=categoria,facultad=facultad,
                                    dedicacion_academica=dedicacion_academica,aporte=aporte,
                                    titulo=titulo,foto=foto)
            
            
                socios.save()
                messages.success(request, 'Se ha agregado un nuevo socio')
                enviar_email_nuevaSocio(username,password,email)

                # Redirigir a la página deseada después de guardar los datos
                return redirect('listar_socios')

    except Exception as e:
        # Si ocurre algún error durante la transacción, la transacción se revierte automáticamente
        messages.warning(request,'Ups, ha ocurrido un problema' ) 
        print(e)
    return render(request, 'emp_socios.html')

def enviar_email_nuevaSocio(username,password,email):
    subject = 'Registro de un nuevo socio'
    message = f'Te damos la bienvenidad en ADUTEQ, ahora podras ser parte de nosotros y acceder a buenos beneficios\n\nPara poder ver mensualmente tus consumos y todo sobre aduteq podras entrar a la app movil de aduteq, mediante las credenciales que te daremos podras entrar\n\n'
    message += f'Usuario: {username}\n\n Contraseña: {password}\n\n'
    message += 'Gracias.\n'
    from_email = 'tu_correo@example.com'  # Reemplaza esto con tu dirección de correo electrónico
    send_mail(subject, message, from_email, [email], fail_silently=False)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editar_socio(request, socio_id):
    socio = Socios.objects.get(id=socio_id)
    usuario = User.objects.get(id=socio.user_id)
    if request.method == 'POST':
        #try:
           
            if 'foto' in request.FILES:
                socio.foto = request.FILES['foto']
              
            # usuario.username = request.POST.get('username')
            # usuario.set_password(request.POST['password'])
            socio.cedula = request.POST.get('cedula')
            usuario.first_name = request.POST.get('first_name')
            usuario.last_name = request.POST.get('last_name')
            socio.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            socio.lugar_nacimiento = request.POST.get('lugar_nacimiento')
            usuario.email = request.POST.get('email')
            socio.numero_telefonico = request.POST.get('numero_telefonico')
            socio.numero_convencional = request.POST.get('numero_convencional')
            socio.direccion_domiciliaria = request.POST.get(
                'direccion_domiciliaria')
            socio.facultad = request.POST.get('facultad')
            socio.categoria = request.POST.get('categoria')
            socio.dedicacion_academica = request.POST.get(
                'dedicacion_academica')
            socio.titulo = request.POST.get('titulo')
            # socio.aporte = request.POST.get('aporte')

            # if User.objects.exclude(id=usuario.id).filter(username=usuario.username).exists():
            #     messages.warning(request, 'El nombre de usuario ya está registrado')
            #     return render(request, 'emp_edit_socios.html', {'socio': socio})
            # if Socios.objects.exclude(id=socio_id).filter(cedula=socio.cedula).exists():
            #     messages.warning(request, 'El número de cédula ya está registrado')
            #     return render(request, 'emp_edit_socios.html', {'socio': socio})
            # if User.objects.exclude(id=usuario.id).filter(email=usuario.email).exists():
            #     messages.warning(request, 'El correo ya está registrado')
            #     return render(request, 'emp_edit_socios.html', {'socio': socio})
            # if Socios.objects.exclude(id=socio_id).filter(numero_telefonico=socio.numero_telefonico).exists():
            #     messages.warning(request, 'El número de telefono ya está registrado')
            #     return render(request, 'emp_edit_socios.html', {'socio': socio})
            
            valor = False;   
            if User.objects.exclude(id=usuario.id).filter(username=usuario.username).exists():
                    messages.warning(
                        request, 'El nombre de usuario ya está registrado')
                    valor = True
            if Socios.objects.exclude(id=socio_id).filter(cedula=socio.cedula).exists():
                    messages.warning(
                        request, 'El número de cédula ya está registrado')
                    valor = True
            if User.objects.exclude(id=usuario.id).filter(email=usuario.email).exists():
                    messages.warning(
                        request, 'El correo ya está registrado, ingrese otro')
                    valor = True
            if Socios.objects.exclude(id=socio_id).filter(numero_telefonico=socio.numero_telefonico).exists():
                    messages.warning(
                        request, 'El número de telefono ya está registrado')
                    valor = True
            if Socios.objects.exclude(id=socio_id).filter(numero_convencional=socio.numero_convencional).exists():
                    messages.warning(
                        request, 'El número de convencional ya está registrado')
                    valor = True

            if valor == True:
                ListaDatos = carga_datos_html()
                ListaDatos.update( {
                                'socio': socio,'user': usuario
                            })
                return render(request, 'emp_edit_socios.html', ListaDatos)


            usuario.save()
            socio.save()

            messages.success(
                request, 'Se ha guardado correctamente este socio')
            return redirect('listar_socios')
        #except:
            #messages.warning(request, 'Error de integridad en los datos')
            #return redirect('listar_socios')
    else:
        ListaDatos = carga_datos_html()
        ListaDatos.update( {
                        'socio': socio,'user': usuario
                    })
        return render(request, 'emp_edit_socios.html', ListaDatos)


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def eliminar_socio(request, user_id, valor):
    socio = Socios.objects.get(id=user_id)

    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        print(valor)
        if valor == 0:
            socio.is_active = True
            socio.user.is_active=True
            socio.save()
            socio.user.save()
            messages.success(
                request, 'El socio se habilitado exitosamente.')
        else:
            socio.is_active = False
            socio.user.is_active=False
            socio.save()
            socio.user.save()
            messages.success(
                request, 'El socio ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación

    else:
        messages.warning(request, 'El socio no pudo ser eliminado')

    return redirect('listar_socios')


# def buscar_socios(request):

#    

#     return render(request, 'emp_socios.html', {'socios': socios})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def buscar_socios(request):
    if request.method == "POST":
        criterio = request.POST.get('criterio')
        valor = request.POST.get('query')
        socios = []

        if criterio:
            # Realiza las consultas según el criterio y el valor ingresados
            if criterio == 'nombres':
                users = User.objects.filter(first_name__icontains=valor)
                socios = Socios.objects.filter(user__in=users)
            elif criterio == 'apellidos':
                users = User.objects.filter(last_name__icontains=valor)
                socios = Socios.objects.filter(user__in=users)
            elif criterio == 'categoria':
                socios = Socios.objects.filter(categoria__icontains=valor)
            elif criterio == 'facultad':
                socios = Socios.objects.filter(facultad__icontains=valor)
            elif criterio == 'cedula':
                socios = Socios.objects.filter(cedula__icontains=valor)
            elif criterio == '1':
                users = User.objects.filter(is_active=True)
                socios = Socios.objects.filter(user__in=users)
            elif criterio == '0':
                users = User.objects.filter(is_active=False)
                socios = Socios.objects.filter(user__in=users)

        items_por_pagina = 10  # Cambia esto según tus necesidades
        paginator = Paginator(socios, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            socios_paginados = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            socios_paginados = paginator.get_page(1)

        # Renderiza una tabla parcial con los resultados
        rendered_table = render_to_string("tabla_parcialSocios.html", {"socios": socios_paginados})

        return JsonResponse({"rendered_table": rendered_table})

    return JsonResponse({"error": "Método no permitido"}, status=400)


def Recuperar_cuenta(request):
    return render(request, "recuperar_contra.html")


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ListaSocios(request):
    usuarios_activos_ids = User.objects.filter(is_staff=False,is_active=True).values_list('id', flat=True)
    socios = Socios.objects.filter(user_id__in=usuarios_activos_ids).order_by('id')
    periodo={}
    items_por_pagina = 20
    paginator = Paginator(socios, items_por_pagina)
    numero_pagina = request.GET.get('page')
    
    try:
        periodo_seleccionado = Periodo.objects.filter(activo=True).first()
        socios_pag=paginator.get_page(numero_pagina)
    except PageNotAnInteger:   
        socios_pag=paginator.get_page(1)
    return render(request, "emp_socios.html", {'socios': socios_pag,'periodo': periodo_seleccionado})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def AggSocio(request):
    categorias = models.Categorias.objects.all()
    facultades = models.Facultades.objects.all()
    categorias = models.Categorias.objects.all()
    dedicacionAcademica = models.DedicacionAcademica.objects.all()
    titulos = models.Titulos.objects.all()
    return render(request, "emp_agg_socios.html", {'socios': request.POST,'categorias': categorias,'facultades': facultades,'dedicacionAcademica': dedicacionAcademica,'titulos': titulos})

#--------------------SELECTS-----------
def agregar_categoria_socios (request):
    nombre = request.POST.get('nom_cat')
    descripcion = request.POST.get('descripcion')
    if models.Categorias.objects.filter(nombre_cat=nombre).exists():
        response = cargar_categorias()
        response.update({'valor':'1','icon': 'info', 'title':'Repetido' , 'text':'Ya se encuenta una facultad con este nombre'}
                        )
        return JsonResponse(response, safe=False)
    categorias = models.Categorias(nombre_cat=nombre, descripcion=descripcion)
    categorias.save()
    return JsonResponse(cargar_categorias(), safe=False)


def cargar_categorias():
    categorias = models.Categorias.objects.all()
    categorias_list = list(categorias.values())
    response = {
        'categorias': categorias_list
    }
    return response

@csrf_exempt
def agregar_facultad_socios (request):
    nombre = request.POST.get('nom_facu')
    descripcion = request.POST.get('descripcion')
    if models.Facultades.objects.filter(nombre_facu=nombre).exists():
        response = cargar_facu()
        response.update({'valor':'1','icon': 'info', 'title':'Repetido' , 'text':'Ya se encuenta una facultad con este nombre'}
                        )
        return JsonResponse(response, safe=False)
    facultades = models.Facultades(nombre_facu=nombre, descripcion=descripcion)
    facultades.save()
    return JsonResponse(cargar_facu(), safe=False)

def cargar_facu():
    facultades = models.Facultades.objects.all()
    facultades_list = list(facultades.values())
    response = {
        'facultades': facultades_list
    }
    return response

def agregar_dedicacion_socios (request):
    nombre = request.POST.get('nom_de')
    descripcion = request.POST.get('descripcion')
    if models.DedicacionAcademica.objects.filter(nombre_de=nombre).exists():
        response = cargar_dedicacion()
        response.update({'valor':'1','icon': 'info', 'title':'Repetido' , 'text':'Ya se encuentra registrado'}
                        )
        return JsonResponse(response, safe=False)
    dedicacionAcademica = models.DedicacionAcademica(nombre_de=nombre, descripcion=descripcion)
    dedicacionAcademica.save()
    return JsonResponse(cargar_dedicacion(), safe=False)


def cargar_dedicacion():
    dedicacionAcademica = models.DedicacionAcademica.objects.all()
    dedicacionAcademica_list = list(dedicacionAcademica.values())
    response = {
        'dedicacionAcademica': dedicacionAcademica_list
    }
    return response
     
def agregar_titulo_socios (request):
    nombre = request.POST.get('nom_ti')
    descripcion = request.POST.get('descripcion')
    if models.Titulos.objects.filter(nombre_ti=nombre).exists():
        response = cargar_titulos()
        response.update({'valor':'1','icon': 'info', 'title':'Repetido' , 'text':'Ya se encuenta registrado este titulo'}
                        )
        return JsonResponse(response, safe=False)

    titulos = models.Titulos(nombre_ti=nombre, descripcion=descripcion)
    titulos.save()    
    return JsonResponse(cargar_titulos(), safe=False)                                            

def cargar_titulos():
    titulos = models.Titulos.objects.all()
    titulos_list = list(titulos.values())
    response = {
        'titulos': titulos_list
    }
    return response

def carga_datos_html():
    facultades = models.Facultades.objects.all()
    categorias = models.Categorias.objects.all()
    dedicacionAcademica = models.DedicacionAcademica.objects.all()
    titulos = models.Titulos.objects.all()
    response = {
                'facultades': facultades,
                'categorias': categorias,
                'dedicacionAcademica': dedicacionAcademica,
                'titulos': titulos
            }
    return response

def eliminar_facultad (request):
    id = request.POST.get('id')
    facultad = models.Facultades.objects.get(id=id)
    facultad.delete()
    facultades = models.Facultades.objects.all()
    facultades_list = list(facultades.values())
    response = {
        'facultades': facultades_list
    }
    return JsonResponse(response, safe=False)

def eliminar_categoria (request):
    id = request.POST.get('id')
    categorias = models.Categorias.objects.get(id=id)
    categorias.delete()
    categorias = models.Categorias.objects.all()
    categorias_list = list(categorias.values())
    response = {
        'categorias': categorias_list
    }
    return JsonResponse(response, safe=False)

def eliminar_dedicacion (request):
    id = request.POST.get('id')
    dedicacionAcademica = models.DedicacionAcademica.objects.get(id=id)
    dedicacionAcademica.delete()
    dedicacionAcademica = models.DedicacionAcademica.objects.all()
    dedicacionAcademica_list = list(dedicacionAcademica.values())
    response = {
        'dedicacionAcademica': dedicacionAcademica_list
    }
    return JsonResponse(response, safe=False)

def eliminar_titulo (request):
    id = request.POST.get('id')
    titulos = models.Titulos.objects.get(id=id)
    titulos.delete()
    titulos = models.Titulos.objects.all()
    titulos_list = list(titulos.values())
    response = {
        'titulos': titulos_list
    }
    return JsonResponse(response, safe=False)



#----------------------APORTACIONES-----------------------------------------
def registrar_aportaciones_mensuales(request):
    socios = Socios.objects.all()

    hoy = timezone.now().date()
    primer_dia_mes_actual = hoy.replace(day=1)

    for socio in socios:
        aportaciones_ultimo_mes = Aportaciones.objects.filter(
            socio=socio,
            fecha__gte=primer_dia_mes_actual
        )

        if not aportaciones_ultimo_mes.exists() and socio.user.is_active:
            transaccion_ae = Aportaciones.objects.create(
                socio=socio,
                tipo_aportacion='AE',
                monto=3,  # Monto de Ayuda Económica
                fecha=hoy
            )

            transaccion_co = Aportaciones.objects.create(
                socio=socio,
                tipo_aportacion='CO',
                monto=10,  # Monto de Cuota Ordinaria
                fecha=hoy
            )

    return redirect('/socios/')

def veraportaciones(request):
     aportaciones=Aportaciones.objects.all()
     items_por_pagina = 8
     paginator = Paginator(aportaciones, items_por_pagina)
     numero_pagina = request.GET.get('page')
     try:
          aport_paginadas=paginator.get_page(numero_pagina)
     except PageNotAnInteger:
          aport_paginadas=paginator.get_page(1)
     return render (request, "aportaciones.html" ,{'aportaciones': aport_paginadas})

def veraportacionesocio(request, socio_id):
    socio=Socios.objects.get(id=socio_id)
    aportaciones=Aportaciones.objects.filter(socio=socio)
    items_por_pagina = 8
    paginator = Paginator(aportaciones, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
         apor_paginados=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
         apor_paginados=paginator.get_page(1)
    return render(request, 'aportaciones.html',{'aportaciones': apor_paginados})