
from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.ingresos, name='ingresos'),
    path("salir/", views.salir, name="salir"),
    path('constantes/', views.constantes, name='constantes'),
    path('indicadores/', views.indicadores, name='indicadores'),
    path('dashboards/', views.dashboards, name='dashboards'),
    path("hora-servidor/", views.obtener_hora_servidor, name="hora_servidor"),
    path('accounts/', include('django.contrib.auth.urls'))
]
