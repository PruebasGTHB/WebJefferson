# serializers.py
from rest_framework import serializers
from .models import MedidorPosicion, ConexionMedidores


class MedidorPosicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidorPosicion
        fields = '__all__'


class ConexionMedidoresSerializer(serializers.ModelSerializer):
    origen_id = serializers.CharField(source='origen.medidor_id')
    destino_id = serializers.CharField(source='destino.medidor_id')

    class Meta:
        model = ConexionMedidores
        fields = ['origen_id', 'destino_id', 'start_socket', 'end_socket']
