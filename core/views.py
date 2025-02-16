from django.shortcuts import render
from django.http import JsonResponse
from django.utils.timezone import now

import random


def get_dashboard_data(request, dashboard_id):
    """ Devuelve datos falsos dinámicos para cada dashboard. """
    data = {}

    if dashboard_id == "1":
        data = {
            "potencia": round(random.uniform(500, 1000), 2),
            "frecuencia": round(random.uniform(49.5, 50.5), 2)
        }

    elif dashboard_id == "2":
        data = {
            "voltaje": round(random.uniform(210, 240), 2),
            "corriente": round(random.uniform(5, 15), 2)
        }

    elif dashboard_id == "3":
        data = {
            "energia_consumida": round(random.uniform(1000, 3000), 2),
            "costo": round(random.uniform(50, 150), 2)
        }

    elif dashboard_id == "4":
        data = {
            "eficiencia": round(random.uniform(80, 99), 2),
            "perdidas": round(random.uniform(0, 50), 2)
        }

    elif dashboard_id == "5":
        data = {
            "panel_temperatura": round(random.uniform(30, 80), 2),
            "produccion_energia": round(random.uniform(500, 1500), 2)
        }

    return JsonResponse(data)


def obtener_hora_servidor(request):
    return JsonResponse({"hora_servidor": now().strftime("%H:%M:%S")})


def inicio(request):
    return render(request, 'core/index.html')


def dashboard1(request):
    return render(request, 'core/dashboard1.html')


def dashboard2(request):
    return render(request, 'core/dashboard2.html')


def dashboard3(request):
    return render(request, 'core/dashboard3.html')


def dashboard4(request):
    return render(request, 'core/dashboard4.html')


def dashboard5(request):
    return render(request, 'core/dashboard5.html')
