from django.contrib import admin

# Register your models here.
from .models import MedidorPosicion, ConexionMedidores

admin.site.register(MedidorPosicion)
admin.site.register(ConexionMedidores)
