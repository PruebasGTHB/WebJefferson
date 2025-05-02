# serializers.py
from rest_framework import serializers
from .models import MedidorPosicion, ConexionElemento


class MedidorPosicionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedidorPosicion
        fields = '__all__'


class ConexionElementoSerializer(serializers.ModelSerializer):
    origen_id = serializers.CharField(source='origen_object_id')
    destino_id = serializers.CharField(source='destino_object_id')
    origen_tipo = serializers.CharField(source='origen_content_type.model')
    destino_tipo = serializers.CharField(source='destino_content_type.model')
    estilo_linea = serializers.CharField(
        source='estilo_linea', required=False)  # ✅ AÑADIDO

    class Meta:
        model = ConexionElemento
        fields = ['origen_tipo', 'origen_id', 'destino_tipo',
                  'destino_id', 'start_socket', 'end_socket', 'estilo_linea']  # ✅ AÑADIDO


class ConexionElementoFrontendSerializer(serializers.ModelSerializer):
    origen_id = serializers.SerializerMethodField()
    destino_id = serializers.SerializerMethodField()
    seccion = serializers.SerializerMethodField()
    estilo_linea = serializers.CharField(read_only=True)  # 👈 CORRECTO

    class Meta:
        model = ConexionElemento
        fields = [
            'origen_id',
            'destino_id',
            'start_socket',
            'end_socket',
            'seccion',
            'estilo_linea'
        ]

    def get_origen_id(self, obj):
        return getattr(obj.origen, 'medidor_id', None) or getattr(obj.origen, 'div_id', None)

    def get_destino_id(self, obj):
        return getattr(obj.destino, 'medidor_id', None) or getattr(obj.destino, 'div_id', None)

    def get_seccion(self, obj):
        return getattr(obj.origen, 'seccion', None) or getattr(obj.destino, 'seccion', None)
