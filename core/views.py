from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from django.http import JsonResponse
from .models import ConsumoEnergiaElectrica, ConsumoEnergiaTermica, ConfiguracionInterfaz

from django.db import connection


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MedidorPosicion
from .serializers import MedidorPosicionSerializer
from .serializers import BloqueVisualSerializer
from .models import ConexionElemento
from .models import BloqueVisual
from .serializers import ConexionElementoFrontendSerializer
from django.views.decorators.csrf import csrf_exempt


def obtener_configuracion(request):
    config = ConfiguracionInterfaz.objects.first()
    return JsonResponse({'mostrar_cuadricula': config.mostrar_cuadricula if config else False})


def obtener_consumo_medidor(request, medidor_id):

    energia_total = "--"
    potencia_total = "--"

    # --- 1. Datos de energía eléctrica ---
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT "{medidor_id}" 
                FROM energia_electrica 
                WHERE año = 2025 AND mes = 4
                LIMIT 1
            ''')
            row = cursor.fetchone()
            if row and row[0] is not None:
                energia_total = float(row[0])
    except Exception as e:
        # ⚡ No imprimir el error, solo lo ignoramos
        pass

    # --- 2. Datos de potencia activa ---
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'''
                SELECT "{medidor_id}" 
                FROM potencia_activa 
                WHERE año = 2025 AND mes = 4
                LIMIT 1
            ''')
            row = cursor.fetchone()
            if row and row[0] is not None:
                potencia_total = float(row[0])
    except Exception as e:
        # ⚡ No imprimir el error, solo lo ignoramos
        pass

    return JsonResponse({
        "energia_total_kwh": energia_total,
        "potencia_total_kw": potencia_total,
    })


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
        seccion = item.get('seccion')  # ✅ NUEVO
        x = item.get('x')
        y = item.get('y')

        if not medidor_id or not seccion or x is None or y is None:
            continue  # Evita registros vacíos o corruptos

        try:
            # Filtramos por ID y sección
            medidor = MedidorPosicion.objects.filter(
                medidor_id=medidor_id, seccion=seccion).first()
            if medidor:
                medidor.x = x
                medidor.y = y
                medidor.save()

        except Exception as e:
            print(
                f"❌ Error actualizando medidor {medidor_id} en sección {seccion}: {e}")
            continue

    return Response({'status': 'success'})


@api_view(['GET'])
@csrf_exempt
def obtener_conexiones(request):
    conexiones = ConexionElemento.objects.all()
    serializer = ConexionElementoFrontendSerializer(conexiones, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def guardar_conexiones_generico(request):
    from .models import ConexionElemento
    from django.contrib.contenttypes.models import ContentType

    ConexionElemento.objects.all().delete()  # opcional: limpiar antes de guardar

    for item in request.data:
        # 'medidorposicion' o 'bloquevisual'
        origen_tipo = item.get('origen_tipo')
        destino_tipo = item.get('destino_tipo')
        origen_id = item.get('origen_id')
        destino_id = item.get('destino_id')

        # Buscar ContentTypes
        origen_ct = ContentType.objects.get(model=origen_tipo)
        destino_ct = ContentType.objects.get(model=destino_tipo)

        ConexionElemento.objects.create(
            origen_content_type=origen_ct,
            origen_object_id=origen_id,
            destino_content_type=destino_ct,
            destino_object_id=destino_id,
            start_socket=item.get('start_socket', 'bottom'),
            end_socket=item.get('end_socket', 'top'),
            descripcion=item.get('descripcion')
        )

    return Response({'status': 'success'})


@api_view(['GET'])
def obtener_bloques(request):
    seccion = request.GET.get('seccion')
    if seccion:
        bloques = BloqueVisual.objects.filter(seccion=seccion)
    else:
        bloques = BloqueVisual.objects.all()
    serializer = BloqueVisualSerializer(bloques, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def guardar_bloques(request):
    for item in request.data:
        div_id = item.get('div_id')
        if not div_id:
            continue

        bloque, _ = BloqueVisual.objects.get_or_create(div_id=div_id)
        for key, value in item.items():
            setattr(bloque, key, value)
        bloque.save()

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
