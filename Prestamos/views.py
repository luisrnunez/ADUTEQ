from datetime import date
from django.shortcuts import get_object_or_404, render, redirect
from .models import Prestamo,Socios
from django.contrib import messages

def guardar_prestamo(request):
    if request.method == 'POST':
        monto = request.POST.get('monto')
        fecha_prestamo = request.POST.get('fecha_prestamo')
        fecha_pago = request.POST.get('fecha_pago')
        plazo_meses = request.POST.get('plazo_meses')
        tasa_interes = request.POST.get('tasa_interes')
        descripcion = request.POST.get('descripcion')
        socio_id = request.POST.get('socio')
        socios = Socios.objects.get(id=socio_id)
        prestamo = Prestamo(socio=socios,monto=monto,fecha_pago=fecha_pago,fecha_prestamo=fecha_prestamo, plazo_meses=plazo_meses, tasa_interes=tasa_interes, descripcion=descripcion)
        if Prestamo.objects.filter(socio_id=socios, cancelado=False).exists():
            messages.warning(request,'Este socio ya tiene un prestamo activo por lo que no es posible registrar el prestamo')
            socios =  Socios.objects.select_related('user').all()
            return render(request, 'agregar_prestamo.html',{'socios' :socios,'prestamo' :prestamo})  
        
        messages.success(request,'EL prestamo fue creado exitosamente!!')
        Prestamo.objects.create(socio=socios,monto=monto,fecha_pago=fecha_pago,fecha_prestamo=fecha_prestamo, plazo_meses=plazo_meses, tasa_interes=tasa_interes, descripcion=descripcion,cancelado=False)

        return redirect('mostrar_prestamo')
    else:
        prestamo = Prestamo.objects.all()
        socios =  Socios.objects.select_related('user').all()
        return render(request, 'agregar_prestamo.html', {'prestamo': prestamo,'socios' : socios })



def editar_prestamo(request, prestamo_id):
    if request.method=='GET':
        prestamos = Prestamo.objects.get(id=prestamo_id)
        print(prestamo_id)
        socios =  Socios.objects.select_related('user').all()
        return render(request,'editar_prestamo.html', {'prestamo': prestamos,'socios' : socios })
    else:
        prestamos.prestamos = Prestamo.objects.get(id=prestamo_id)
        prestamos.monto = request.POST.get('monto')
        prestamos.fecha_prestamo = request.POST.get('fecha_prestamo')
        prestamos.fecha_pago = request.POST.get('fecha_pago')
        prestamos.plazo_meses = request.POST.get('plazo_meses')
        prestamos.tasa_interes = request.POST.get('tasa_interes')
        prestamos.descripcion = request.POST.get('descripcion')
        messages.success(request,'EL prestamo fue editado de forma exitosa')
        prestamos.save()

        return redirect('mostrar_prestamo')
    
def mostrar_prestamo(request):
    prestamos = Prestamo.objects.all()
    socios =  Socios.objects.select_related('user').all()
    return render(request, 'mostrar_prestamo.html', {'prestamos': prestamos,'socios' : socios })


def aplicar_pago(request, prestamo_id, valor):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)

    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        print (valor)
        if valor == 0:
            prestamo.cancelado = True
            prestamo.fecha_pago = date.today()
            prestamo.save()
            messages.success(
            request, 'Se ha registrado el pago del prestamo exitosamente.')
        #else:
            #pagosproveedor.activo = False
            #pagosproveedor.save()
            #messages.success(
            #request, 'El socio ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación

    else:
        messages.warning(request, 'El pago no pudo ser procesado')

    return redirect('mostrar_prestamo')