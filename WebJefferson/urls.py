
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('api/dashboard/<str:dashboard_id>/',
         views.get_dashboard_data, name='dashboard_data'),
    path("hora-servidor/", views.obtener_hora_servidor, name="hora_servidor"),
    path('dashboard/1/', views.dashboard1, name='dashboard1'),
    path('dashboard/2/', views.dashboard2, name='dashboard2'),
    path('dashboard/3/', views.dashboard3, name='dashboard3'),
    path('dashboard/4/', views.dashboard4, name='dashboard4'),
    path('dashboard/5/', views.dashboard5, name='dashboard5'),
    path('admin/', admin.site.urls),
]
