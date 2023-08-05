from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import AyudasMot,AyudasEconomicas, Socios

# Create your views here.
def motivos(request):
    motivos=AyudasMot.objects.all()
    return render(request,'motivoayuda.html', {
        'motivos': motivos
    })

#metodo para agregar nuevos motivos
def formRegistro(request):
    return render(request,'aggmotivo.html')

def aggMotivo(request):
    motivo=AyudasMot(motivo=request.POST['motivo'], descripcion=request.POST['descripcion'])

    if(userexist(request.POST['motivo'])):
        response = {
                'status': 'error',
                'message': 'Ya existe un motivo registrado con este nombre'
            }
    else:
        motivo.save()
        response = {
            'status': 'success',
            'message': 'Motivo registrado correctamente.'
            }
    return JsonResponse(response)


#Metodos verificar si existe o no proveedor
def userexist(motivo):
    try:
        motivo = AyudasMot.objects.get(motivo=motivo)
        return True
    except AyudasMot.DoesNotExist:
        return False

#metodos editar proveedores
def feditMotivo(request, codigo):
    motivos=AyudasMot.objects.get(id=codigo)
    return render(request,'editmotivo.html',{
        'motivos': motivos
    })

def editarmotivo(request):
    motivop=request.POST.get('motivo')
    descripcionp=request.POST.get('descripcion')
    evidenciap=request.POST.get('evidencia')
    motivoo= get_object_or_404(AyudasMot, id=request.POST.get('id'))

    if AyudasMot.objects.exclude(id=request.POST.get('id')).filter(motivo=motivop).exists():
        response = {
            'status': 'error',
            'message': 'Ya existe un motivo registrado con este nombre'

          }
    else:
        motivoo.motivo=motivop
        motivoo.descripcion=descripcionp
        # motivoo.evidencia=evidenciap
        motivoo.save()
        response = {
            'status': 'success',
            'message': 'Datos actualizados correctamente'
            }

    return JsonResponse(response)

#metodo para eliminar un motivo.
def deleteMotivo(request, codigo):
    motivo=AyudasMot.objects.get(id=codigo)
    motivo.delete()
    return redirect('/motivos')


#--------------------------------------------------------------------
#-----------------------------Ayudas economicas----------------------
# def mostrar_opciones(request):
#     opciones = Socios.objects.all()
#     return render(request, 'aggAyuda.html', {'opciones': opciones})

def viewayudas(request):
    ayudas=AyudasEconomicas.objects.all()
    return render(request,'ayudasecon.html', {
        'ayudas': ayudas
    })

def formRegistroAyuda(request):
    opciones = Socios.objects.select_related('user').all()
    motivos=AyudasMot.objects.all()
    return render(request,'aggAyuda.html',{
        'opciones':opciones, 'motivos':motivos
    })

def aggAyuda(request):
    socio=Socios.objects.get(id=request.POST['socio'])
    mmotivo=AyudasMot.objects.get(id=request.POST['motivo'])

    ayuda=AyudasEconomicas(socio=socio, descripcion=request.POST['descripcion'], evidencia=request.POST['evidencia'], total=request.POST['total'], motivo=mmotivo, fecha=request.POST['fecha'])

    if(request.method == 'POST'):
        ayuda.save()
        response = {
            'status': 'success',
            'message': 'Ayuda agregada correctamente.'
            }
    else:
        response = {
            'status': 'error',
            'message': 'Ha existido algún error, intentelo de nuevo'
            }
    return JsonResponse(response)

#metodo para eliminar una ayuda.
def deleteAyuda(request, codigo):
    ayuda=AyudasEconomicas.objects.get(id=codigo)
    ayuda.delete()
    return redirect('/verayudas')

#metodos editar ayudas
def feditAyuda(request, codigo):
    opciones = Socios.objects.all()
    motivos=AyudasMot.objects.all()
    ayuda=AyudasEconomicas.objects.get(id=codigo)
    return render(request,'editarayuda.html',{
        'ayuda': ayuda, 'socios': opciones, 'motivos':motivos
    })