from django.shortcuts import render, redirect

def cuentas(request):
    return render ( request, 'cuentas_princ.html')