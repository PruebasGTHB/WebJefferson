from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from django.http import JsonResponse
from .models import ConsumoEnergiaElectrica, ConsumoEnergiaTermica

from django.db import connection


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MedidorPosicion
from .serializers import MedidorPosicionSerializer
from .models import ConexionMedidores
from .serializers import ConexionMedidoresSerializer
from django.views.decorators.csrf import csrf_exempt


@api_view(['GET'])
@csrf_exempt
def obtener_posiciones(request):
    seccion = request.GET.get('seccion')
    if seccion:
        posiciones = MedidorPosicion.objects.filter(seccion=seccion)
    else:
        posiciones = MedidorPosicion.objects.all()
    serializer = MedidorPosicionSerializer(posiciones, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@csrf_exempt
def guardar_posiciones(request):
    for item in request.data:
        medidor_id = item.get('medidor_id')
        x = item.get('x')
        y = item.get('y')

        if not medidor_id or x is None or y is None:
            continue  # Evita registros vacíos o corruptos

        MedidorPosicion.objects.update_or_create(
            medidor_id=medidor_id,
            defaults={'x': x, 'y': y}
        )
    return Response({'status': 'success'})


@api_view(['GET'])
@csrf_exempt
def obtener_conexiones(request):
    conexiones = ConexionMedidores.objects.all()
    serializer = ConexionMedidoresSerializer(conexiones, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@csrf_exempt
def guardar_conexiones(request):
    ConexionMedidores.objects.all().delete()  # Opcional: borrar y reemplazar
    for item in request.data:
        ConexionMedidores.objects.create(**item)
    return Response({'status': 'success'})


# Verifica si el usuario es administrador


def es_admin(user):
    return user.is_superuser


# Vista de login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home_redirect')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home_redirect')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'core/registration/login.html')


@login_required
def monitoreo(request):
    return render(request, 'core/monitoreo/monitoreo.html')


# Redirecciona al ingreso correcto según tipo de usuario

@login_required
def home_redirect(request):
    if request.user.is_superuser:
        return redirect('menu')
    else:
        return redirect('menu_view')


# Vista común para todos: el banner o layout general
@login_required
def inicio_usuario(request):
    return render(request, 'core/index/index_usuario.html')


# VISTAS USUARIO
@login_required
def menu_usuario(request):
    return render(request, 'core/menu/menu_usuario.html')


@login_required
def ingresos_usuario(request):
    return render(request, 'core/ingresos/ingresos_usuario.html')


@login_required
def constantes_usuario(request):
    return render(request, 'core/constantes/constantes_usuario.html')


@login_required
def indicadores_usuario(request):
    return render(request, 'core/indicadores/indicadores_usuario.html')


@login_required
def dashboards_usuario(request):
    return render(request, 'core/dashboards/dashboards_usuario.html')


@login_required
def obtener_consumo_medidor(request, medidor_id):
    energia_total = "--"
    potencia_total = "--"

    # --- 1. Datos de energía eléctrica ---
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT "{medidor_id}" 
                FROM consumo_energia_electrica 
                WHERE año = 2025 AND mes = 4
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row and row[0] is not None:
                energia_total = float(row[0])
    except Exception as e:
        print("⚠️ Error en energía eléctrica:", e)

    # --- 2. Datos de energía térmica (GLP) ---
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT consumo_total_glp 
                FROM consumo_energia_termica_tabla 
                WHERE año = 2025 AND mes = 3
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row and row[0] is not None:
                potencia_total = float(row[0])
    except Exception as e:
        print("⚠️ Error en energía térmica:", e)

    return JsonResponse({
        "energia_total_kwh": energia_total,
        "potencia_total_kw": potencia_total,
    })

# VISTAS ADMINISTRADOR


@login_required
@user_passes_test(es_admin, login_url='menu')
def menu(request):
    return render(request, 'core/menu/menu.html')


@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def ingresos_admin(request):
    return render(request, 'core/ingresos/ingresos_admin.html')


@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def constantes_admin(request):
    return render(request, 'core/constantes/constantes_admin.html')


@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def indicadores_admin(request):
    return render(request, 'core/indicadores/indicadores_admin.html')


@login_required
@user_passes_test(es_admin, login_url='ingresos_usuario')
def dashboards_admin(request):
    return render(request, 'core/dashboards/dashboards_admin.html')


@login_required
def obtener_consumo_medidor(request, medidor_id):
    energia_total = "--"
    potencia_total = "--"

    # --- 1. Datos de energía eléctrica ---
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT "{medidor_id}" 
                FROM consumo_energia_electrica 
                WHERE año  = 2025 AND mes = 4
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row and row[0] is not None:
                energia_total = float(row[0])
    except Exception as e:
        print("⚠️ Error en energía eléctrica:", e)

    # --- 2. Datos de energía térmica (GLP) ---
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT riles_vapor
                FROM consumo_energia_termica_tabla 
                WHERE año = 2025 AND mes = 3
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row and row[0] is not None:
                potencia_total = float(row[0])
    except Exception as e:
        print("⚠️ Error en energía térmica:", e)

    return JsonResponse({
        "energia_total_kwh": energia_total,
        "potencia_total_kw": potencia_total,
    })
