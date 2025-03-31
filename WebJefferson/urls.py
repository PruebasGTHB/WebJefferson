from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Ruta raíz redirige según tipo de usuario
    path('', views.home_redirect, name='home_redirect'),

    # Panel de administración Django
    path('admin/', admin.site.urls),

    # Login y logout
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Vista compartida (el layout común)
    path('inicio/', views.inicio_usuario, name='inicio_usuario'),

    # Rutas usuario
    path('ingresos_usuario/', views.ingresos_usuario, name='ingresos_usuario'),
    path('constantes_usuario/', views.constantes_usuario,
         name='constantes_usuario'),
    path('indicadores_usuario/', views.indicadores_usuario,
         name='indicadores_usuario'),
    path('dashboards_usuario/', views.dashboards_usuario,
         name='dashboards_usuario'),

    # Rutas admin
    path('ingresos_admin/', views.ingresos_admin, name='ingresos_admin'),
    path('constantes_admin/', views.constantes_admin, name='constantes_admin'),
    path('indicadores_admin/', views.indicadores_admin, name='indicadores_admin'),
    path('dashboards_admin/', views.dashboards_admin, name='dashboards_admin'),
]
