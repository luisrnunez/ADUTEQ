from django.shortcuts import render,redirect
from .models import Socios,Proveedor,Pagos
from .forms import PagosForm


# Create your views here.
def lista_pagos(request):
    pagos = Pagos.objects.all()
    return render (request, 'listar_pagos.html', {'pagos' : pagos})

def agrefar_pagos(request):
    if request.method=='GET':
        socios=Socios.objects.all()
        proveedores=Proveedor.objects.all()
        return render (request, 'agregar_pago.html',{'socios': socios,'proveedores': proveedores})
    else:
        socio_id = request.POST.get('socio')
        socios = Socios.objects.get(id=socio_id)

        proveedor_id =request.POST.get('proveedor')
        proveedores=Proveedor.objects.get(id=proveedor_id)
        
        cantidad=request.POST.get('consumo_total')
        fecha=request.POST.get('fecha_consumo')

        pagos = Pagos.objects.create(socio=socios,proveedor=proveedores,consumo_total=cantidad,fecha_consumo=fecha)

        return redirect('/listar_pagos/')
    
def editar_pago(request, pago_id):
    if request.method=='GET':
        pagos = Pagos.objects.get(id=pago_id)
        form=PagosForm(instance=pagos)
        return render(request,'editar_pago.html',{'pagos': pagos, 'form': form})
    else:
        pagos = Pagos.objects.get(id=pago_id)
        form= PagosForm(request.POST, instance=pagos)
        print(request.POST)
        form.save()
        return redirect('/listar_pagos/')
    
def eliminar_pago (request, pago_id):
    pagos = Pagos.objects.get(id=pago_id)
    pagos.delete()
    return redirect('/listar_pagos/')