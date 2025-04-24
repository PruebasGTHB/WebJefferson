# serializers.py
from rest_framework import serializers
from .models import MedidorPosicion
from .models import ConexionMedidores


class MedidorPosicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidorPosicion
        fields = '__all__'


class ConexionMedidoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConexionMedidores
        fields = '__all__'
