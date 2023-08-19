from django.shortcuts import render, redirect, get_object_or_404
from .models import Categorias
from .forms import CategoriasForm
from django.core.exceptions import ValidationError


# Create your views here.
def lista_categorias(request):
    categorias = Categorias.objects.all()
    return render (request, 'listar_categorias.html', {'categorias' : categorias})

def agregar_categoria (request):
   categorias = Categorias(nombre_cat=request.POST['nom_cat'], descripcion=request.POST['descripcion'])
   categorias.save()
   return redirect('/categorias/')

def eliminar_categoria (request, cat_id):
    categorias = Categorias.objects.get(id=cat_id)
    print(categorias)
    categorias.delete()
    return redirect('/categorias/')

def editar_categoria (request, cat_id):
    if request.method=='GET':
        categorias = Categorias.objects.get(id=cat_id)
        form=CategoriasForm(instance=categorias)
        return render(request,'editar_categoria.html',{'categorias': categorias, 'form': form})
    else:
        categorias = Categorias.objects.get(id=cat_id)
        form= CategoriasForm(request.POST, instance=categorias)
        print(request.POST)
        form.save()
        return redirect('/categorias/')