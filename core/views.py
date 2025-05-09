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


@api_view(['GET'])
@csrf_exempt
@cache_page(60)  # Cache de 60 segundos (opcional pero recomendado)
def obtener_conexiones(request):
    seccion = request.query_params.get('seccion')
    if not seccion:
        return Response([], status=400)

    # IDs de medidores de la sección
    medidor_ids = list(
        MedidorPosicion.objects.filter(
            seccion=seccion).values_list('id', flat=True)
    )

    # Obtener solo conexiones relevantes
    conexiones = list(ConexionElemento.objects.filter(
        Q(origen_object_id__in=medidor_ids) |
        Q(destino_object_id__in=medidor_ids)
    ))

    # Cache manual de objetos por content_type e ID
    objetos_por_ct = {}

    for con in conexiones:
        for lado in ['origen', 'destino']:
            ct = getattr(con, f'{lado}_content_type')
            obj_id = getattr(con, f'{lado}_object_id')
            objetos_por_ct.setdefault(ct, set()).add(obj_id)

    # Cargar todos los objetos una sola vez
    objeto_cache = {}
    for ct, ids in objetos_por_ct.items():
        model = ct.model_class()
        for obj in model.objects.filter(id__in=ids):
            objeto_cache[(ct.id, str(obj.id))] = obj

    # Asignar objetos desde el cache y filtrar conexiones válidas
    conexiones_validas = []
    for con in conexiones:
        con.origen = objeto_cache.get(
            (con.origen_content_type.id, con.origen_object_id))
        con.destino = objeto_cache.get(
            (con.destino_content_type.id, con.destino_object_id))

        if (
            (con.origen and getattr(con.origen, 'seccion', None) == seccion) or
            (con.destino and getattr(con.destino, 'seccion', None) == seccion)
        ):
            conexiones_validas.append(con)

    serializer = ConexionElementoFrontendSerializer(
        conexiones_validas, many=True)
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

    # Validar formato del medidor
    if not re.match(
        r'^(em\d+|pem3_em\d+|pem6_em\d+|diesel_flota|c2_diesel|c2_glp|c2_vapor|c3_diesel|c3_glp|c3_vapor|c4_diesel|c4_glp|c4_vapor|calderas_diesel|calderas_glp|calderas_vapor|flujo_s|flujo_r|vapor)$',
        medidor_id.lower()
    ):
        return JsonResponse({}, status=204)

    # Buscar el primer registro con ese medidor_id
    medidor = MedidorPosicion.objects.filter(medidor_id=medidor_id).first()
    if not medidor:
        return JsonResponse({}, status=204)

    # Validar sección si aplica
    if seccion and medidor.seccion != seccion:
        return JsonResponse({}, status=204)

    # Aceptar solo si es de categoría 'medidor' o 'energia_sola'
    if medidor.categoria_visual not in ['medidor', 'energia_sola']:
        return JsonResponse({}, status=204)

    # Preparar valores
    energia_total = float(
        medidor.energia_total_kwh) if medidor.energia_total_kwh is not None else "--"
    potencia_total = float(
        medidor.potencia_total_kw) if medidor.potencia_total_kw is not None else "--"

    return JsonResponse({
        "energia_total_kwh": energia_total,
        "potencia_total_kw": potencia_total,
    })


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
@csrf_exempt
@cache_page(60)  # Opcional: cachea la respuesta por 60 segundos
def obtener_posiciones(request):
    seccion = request.query_params.get('seccion')
    if not seccion:
        return Response([], status=400)

    # Todos los campos que el frontend necesita
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

    queryset = (
        MedidorPosicion.objects
        .filter(seccion=seccion)
        .values(*campos_utilizados)
        .order_by('categoria_visual')
    )

    return Response(list(queryset))


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
