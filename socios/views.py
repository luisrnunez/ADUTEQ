from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.

def login(request):
    return render(request,"index.html")

def about(request):
    return HttpResponse("QUEMAS")