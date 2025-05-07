from django.contrib import admin
from django.urls import path
from core import views
from core import views_refrigeracion
from django.contrib.auth.views import LogoutView
from core.views_refrigeracion import datos_refrigeracion


urlpatterns = [
    # Ruta raíz redirige según tipo de usuario
    path('', views.home_redirect, name='home_redirect'),

    path('api/posiciones/', views.obtener_posiciones),
    path('api/guardar_posiciones/', views.guardar_posiciones),

    path('api/conexiones/', views.obtener_conexiones),
    path('api/guardar_conexiones/', views.guardar_conexiones_generico,
         name='guardar_conexiones'),



    path('api/consumos/<str:medidor_id>/', views.obtener_consumo_medidor),

    path('api/configuracion/', views.obtener_configuracion),

    # COMPARTIDAS
    path('refrigeracion/', views.refrigeracion, name='refrigeracion'),

    # DUPLICAR MEDIDORES
    path('admin/core/medidorposicion/duplicar/',
         views.duplicar_medidores_view, name='duplicar_medidores'),

    # Panel de administración Django
    path('admin/', admin.site.urls),

    # Login y logout
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Vista compartida (el layout común)
    path('inicio/', views.inicio_usuario, name='inicio_usuario'),
    path('monitoreo/', views.monitoreo, name='monitoreo'),

    # Rutas usuario
    path('menu_view/', views.menu_usuario, name='menu_view'),
    path('ingresos_view/', views.ingresos_usuario, name='ingresos_usuario'),
    path('constantes_view/', views.constantes_usuario,
         name='constantes_usuario'),
    path('indicadores_view/', views.indicadores_usuario,
         name='indicadores_usuario'),
    path('dashboards_view/', views.dashboards_usuario,
         name='dashboards_usuario'),
    #     path('api/consumos/<str:medidor_id>/',
    #          views.obtener_consumo_medidor, name='obtener_consumo_medidor'),


    # Rutas admin
    path('menu/', views.menu, name='menu'),
    path('ingresos/', views.ingresos_admin, name='ingresos_admin'),
    path('constantes/', views.constantes_admin, name='constantes_admin'),
    path('indicadores/', views.indicadores_admin, name='indicadores_admin'),
    path('dashboards/', views.dashboards_admin, name='dashboards_admin'),
    #     path('api/consumos/<str:medidor_id>/',
    #          views.obtener_consumo_medidor, name='obtener_consumo_medidor'),
    path('api/datos_refrigeracion/', datos_refrigeracion),
    path('api/datos_refrigeracion/', views_refrigeracion.datos_refrigeracion),
]
