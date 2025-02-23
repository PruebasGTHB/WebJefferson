from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def obtener_hora_servidor(request):
    return JsonResponse({"hora_servidor": now().strftime("%H:%M:%S")})


@login_required
def inicio(request):
    return render(request, 'core/index2.html')


def inicio2(request):
    return render(request, 'core/index.html')


def salir(request):
    logout(request)
    return redirect('/')
