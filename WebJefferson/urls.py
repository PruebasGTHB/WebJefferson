
from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path("salir/", views.salir, name="salir"),
    path('inicio2/', views.inicio2, name='inicio2'),
    path('ingresos/', views.ingresos, name='ingresos'),
    path('constantes/', views.constantes, name='constantes'),
     path('indicadores/', views.indicadores, name='indicadores'),
    path("hora-servidor/", views.obtener_hora_servidor, name="hora_servidor"),
    path('accounts/', include('django.contrib.auth.urls'))
]
