from core.models import MedidorPosicion
from django.views.decorators.cache import cache_page
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

from .models import ConexionElemento

from .serializers import ConexionElementoFrontendSerializer
from django.views.decorators.csrf import csrf_exempt


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import MedidorPosicion
from .forms import DuplicarMedidoresForm


import re
from django.http import JsonResponse
from django.db import connection
from django.db.models import Q


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from core.models import MedidorPosicion, ConexionElemento

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from core.models import MedidorPosicion, ConexionElemento


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.contrib.contenttypes.models import ContentType

from core.models import ConexionElemento, MedidorPosicion
from core.serializers import ConexionElementoFrontendSerializer


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Q
from core.models import ConexionElemento, MedidorPosicion
from django.contrib.contenttypes.models import ContentType
import hashlib


@api_view(['GET'])
def obtener_conexiones(request):
    seccion = request.query_params.get('seccion')
    if not seccion:
        return Response([], status=400)

    # Crea una clave de cache única por sección
    cache_key = f"conexiones_{hashlib.md5(seccion.encode()).hexdigest()}"
    timestamp_key = f"{cache_key}_timestamp"

    # Obtener el último update de la tabla
    ultima_conexion = ConexionElemento.objects.order_by('-updated_at').first()
    last_updated_db = ultima_conexion.updated_at.timestamp() if ultima_conexion else 0
    last_updated_cache = cache.get(timestamp_key)

    if cache.get(cache_key) and last_updated_cache == last_updated_db:
        return Response(cache.get(cache_key))

    # Si no hay cache válido, lo regeneramos
    medidor_ct = ContentType.objects.get_for_model(MedidorPosicion)
    medidor_ids = list(
        MedidorPosicion.objects.filter(
            seccion=seccion).values_list('id', flat=True)
    )
    medidores = MedidorPosicion.objects.filter(id__in=medidor_ids)
    medidor_dict = {str(m.id): m for m in medidores}

    conexiones = ConexionElemento.objects.filter(
        Q(origen_content_type=medidor_ct, origen_object_id__in=medidor_ids) |
        Q(destino_content_type=medidor_ct, destino_object_id__in=medidor_ids)
    )

    conexiones_validas = []
    for con in conexiones:
        con.origen = medidor_dict.get(
            str(con.origen_object_id)) if con.origen_content_type == medidor_ct else None
        con.destino = medidor_dict.get(
            str(con.destino_object_id)) if con.destino_content_type == medidor_ct else None

        if (
            (con.origen and con.origen.seccion == seccion) or
            (con.destino and con.destino.seccion == seccion)
        ):
            conexiones_validas.append(con)

    from core.serializers import ConexionElementoFrontendSerializer
    serializer = ConexionElementoFrontendSerializer(
        conexiones_validas, many=True)

    # Guardar en caché indefinidamente y asociar timestamp
    cache.set(cache_key, serializer.data, timeout=None)
    cache.set(timestamp_key, last_updated_db, timeout=None)

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


###########################################################################################################
###########################################################################################################


def duplicar_medidores_view(request):
    if request.method == 'POST':
        form = DuplicarMedidoresForm(request.POST)
        if form.is_valid():
            nueva_seccion = form.cleaned_data['nueva_seccion']
            selected_ids = request.POST.getlist('_selected_action')

            if not selected_ids:
                messages.warning(request, "No se seleccionó ningún medidor.")
                return redirect('admin:core_medidorposicion_changelist')

            medidores = MedidorPosicion.objects.filter(id__in=selected_ids)

            nuevos = []
            for m in medidores:
                m.pk = None  # Para crear un nuevo objeto
                m.seccion = nueva_seccion
                m.save()
                nuevos.append(m)

            messages.success(
                request, f"✅ {len(nuevos)} medidor(es) duplicados en '{nueva_seccion}'.")
            return redirect('admin:core_medidorposicion_changelist')
    else:
        # GET: mostrar formulario
        selected_ids = request.GET.getlist('_selected_action')
        medidores = MedidorPosicion.objects.filter(id__in=selected_ids)
        form = DuplicarMedidoresForm()
        context = {
            'form': form,
            'medidores': medidores,
            'ids': selected_ids,
        }
        return render(request, 'core/duplicar_medidores/duplicar_medidores_form.html', context)


###########################################################################################################
###########################################################################################################


def obtener_configuracion(request):
    config = ConfiguracionInterfaz.objects.first()
    return JsonResponse({'mostrar_cuadricula': config.mostrar_cuadricula if config else False})


###########################################################################################################
###########################################################################################################


@api_view(['GET'])
def obtener_consumo_medidor(request, medidor_id):
    seccion = request.GET.get('seccion')

    if not re.match(
        r'^(em\d+|pem3_em\d+|pem6_em\d+|diesel_flota|c2_diesel|c2_glp|c2_vapor|c3_diesel|c3_glp|c3_vapor|c4_diesel|c4_glp|c4_vapor|calderas_diesel|calderas_glp|calderas_vapor|flujo_s|flujo_r|vapor)$',
        medidor_id.lower()
    ):
        return JsonResponse({}, status=204)

    medidor = MedidorPosicion.objects.filter(medidor_id=medidor_id).first()
    if not medidor:
        return JsonResponse({}, status=204)

    if seccion and medidor.seccion != seccion:
        return JsonResponse({}, status=204)

    if medidor.categoria_visual not in ['medidor', 'energia_sola']:
        return JsonResponse({}, status=204)

    base_key = f"{medidor_id}_{seccion or 'global'}"
    cache_key = f"consumo_medidor_{hashlib.md5(base_key.encode()).hexdigest()}"
    timestamp_key = f"{cache_key}_ts"

    last_updated_db = medidor.updated_at.timestamp() if hasattr(medidor,
                                                                "updated_at") else 0
    last_updated_cache = cache.get(timestamp_key)

    if cache.get(cache_key) and last_updated_cache == last_updated_db:
        return JsonResponse(cache.get(cache_key))

    # Aplicar condición a energia_total_kwh
    if medidor.energia_total_kwh is not None:
        energia_total = float(medidor.energia_total_kwh)
        if energia_total < 2.5:
            energia_total = 0
    else:
        energia_total = "--"

    # Aplicar condición a potencia_total_kw
    if medidor.potencia_total_kw is not None:
        potencia_total = float(medidor.potencia_total_kw)
        if potencia_total < 2.5:
            potencia_total = 0
    else:
        potencia_total = "--"

    response_data = {
        "energia_total_kwh": energia_total,
        "potencia_total_kw": potencia_total,
    }

    cache.set(cache_key, response_data, timeout=None)
    cache.set(timestamp_key, last_updated_db, timeout=None)

    return JsonResponse(response_data)


###########################################################################################################
###########################################################################################################


# @api_view(['GET'])
# @csrf_exempt
# def obtener_posiciones(request):
#     seccion = request.GET.get('seccion')
#     if seccion:
#         posiciones = MedidorPosicion.objects.filter(seccion=seccion)
#     else:
#         posiciones = MedidorPosicion.objects.all()
#     serializer = MedidorPosicionSerializer(posiciones, many=True)
#     return Response(serializer.data)


# SUPUESTA API MEJORA ABAJO


@api_view(['GET'])
def obtener_posiciones(request):
    seccion = request.query_params.get('seccion')
    if not seccion:
        return Response([], status=400)

    campos_utilizados = [
        'id', 'medidor_id', 'x', 'y', 'seccion', 'categoria_visual',
        'tipo', 'tipo_descripcion', 'titulo', 'grafana_url',
        'editable', 'width', 'height', 'background', 'border_color',
        'border_width', 'border_radius', 'border_style', 'animate_class',
        'text_content', 'text_color', 'font_size', 'text_align',
        'text_vertical_align', 'font_weight', 'font_style', 'text_decoration',
        'mostrar_icono_estado', 'tipo_icono_estado', 'fondo_personalizado',
        'color_titulo', 'tamano_titulo', 'fuente_titulo', 'bold_titulo',
        'alineacion_vertical', 'seccion_destino',
        'energia_total_kwh', 'potencia_total_kw'
    ]

    # Cache keys
    cache_key = f"posiciones_{hashlib.md5(seccion.encode()).hexdigest()}"
    timestamp_key = f"{cache_key}_timestamp"

    # Última modificación real
    ultima_posicion = MedidorPosicion.objects.filter(
        seccion=seccion).order_by('-updated_at').first()
    last_updated_db = ultima_posicion.updated_at.timestamp() if ultima_posicion else 0
    last_updated_cache = cache.get(timestamp_key)

    # Usar cache si es válido
    if cache.get(cache_key) and last_updated_cache == last_updated_db:
        return Response(cache.get(cache_key))

    # Regenerar datos y cachearlos
    queryset = (
        MedidorPosicion.objects
        .filter(seccion=seccion)
        .values(*campos_utilizados)
        .order_by('categoria_visual')
    )

    data = list(queryset)

    cache.set(cache_key, data, timeout=None)
    cache.set(timestamp_key, last_updated_db, timeout=None)

    return Response(data)


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


###########################################################################################################
###########################################################################################################


###########################################################################################################
###########################################################################################################


###########################################################################################################
###########################################################################################################

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


# COMPARTIDAS
@login_required
def refrigeracion(request):
    return render(request, 'core/refrigeracion/refrigeracion.html')


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
