from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


# 🔹 1. Vista para mostrar la tabla en el HTML


def obtener_hora_servidor(request):
    return JsonResponse({"hora_servidor": now().strftime("%H:%M:%S")})


@login_required
def inicio(request):
    return render(request, 'core/index2.html')


def ingresos(request):
    return render(request, 'core/ingresos.html')


def constantes(request):
    return render(request, 'core/constantes.html')


def indicadores(request):
    return render(request, 'core/indicadores.html')


def dashboards(request):
    return render(request, 'core/dashboards.html')


def salir(request):
    logout(request)
    return redirect('/')
