from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

# Create your models here.


####################################################################################################################################################################
####################################################################################################################################################################


class BloqueVisual(models.Model):
    SECCION_CHOICES = [
        ('Vista General Planta', 'Vista General Planta'),
        ('Empalme 1 Planta Harina', 'Empalme 1 Planta Harina'),
        ('Empalme 2 Planta Congelado', 'Empalme 2 Planta Congelado'),
        ('Empalme 3 Pontón Tor', 'Empalme 3 Pontón Tor'),
        ('General Flota', 'General Flota'),
        ('Sala de Calderas', 'Sala de Calderas'),
        ('Planta Harina', 'Planta Harina'),
        ('Planta Congelado', 'Planta Congelado'),
        ('Flota', 'Flota'),
        ('Planta Harina/Congelados', 'Planta Harina/Congelados'),
    ]

    div_id = models.CharField(max_length=100, unique=True)
    seccion = models.CharField(
        max_length=100, choices=SECCION_CHOICES, default='Vista General Planta')
    x = models.FloatField(default=4575.3279)
    y = models.FloatField(default=1941.9883)

    # Estilos generales
    width = models.CharField(max_length=10, blank=True,
                             null=True, default='100px')
    height = models.CharField(
        max_length=10, blank=True, null=True, default='100px')
    background = models.CharField(
        max_length=50, blank=True, null=True, default='transparent')
    border_color = models.CharField(max_length=50, blank=True, null=True)
    border_width = models.CharField(
        max_length=10, blank=True, null=True, default='0px')
    border_radius = models.CharField(
        max_length=10, blank=True, null=True, default='0px')
    animate_class = models.CharField(max_length=100, blank=True, null=True)

    # Texto interno y estilo del texto
    text_content = models.TextField(blank=True, null=True)
    text_color = models.CharField(
        max_length=20, blank=True, null=True, default='#000000')
    font_size = models.CharField(
        max_length=10, blank=True, null=True, default='16px')
    text_align = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('left', 'Izquierda'),
        ('center', 'Centro'),
        ('right', 'Derecha')
    ], default='center')
    text_vertical_align = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('start', 'Arriba'),
        ('center', 'Centro'),
        ('end', 'Abajo')
    ], default='center')

    # Diseño adicional del Div
    border_style = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('solid', 'Sólido'),
            ('dashed', 'Guiones'),
            ('dotted', 'Punteado'),
            ('double', 'Doble'),
            ('groove', 'Surco'),
        ],
        default='solid'
    )

    # Decoraciones de texto
    font_weight = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('normal', 'Normal'),
            ('bold', 'Negrita'),
        ],
        default='normal'
    )

    font_style = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('normal', 'Normal'),
            ('italic', 'Cursiva'),
        ],
        default='normal'
    )

    text_decoration = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('none', 'Ninguno'),
            ('underline', 'Subrayado'),
        ],
        default='none'
    )
    editable = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_bloquevisual'


####################################################################################################################################################################
####################################################################################################################################################################


class ConsumoEnergiaElectrica(models.Model):
    medidor = models.CharField(max_length=10)
    año = models.IntegerField(default=2025)
    mes = models.IntegerField()
    energia_total_kwh = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'energia_electrica'
        managed = False


####################################################################################################################################################################


class ConsumoEnergiaTermica(models.Model):
    medidor = models.CharField(max_length=10)
    año = models.IntegerField(default=2025)
    mes = models.IntegerField()
    consumo_total_glp_kw = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'potencia_activa'
        managed = False


####################################################################################################################################################################
####################################################################################################################################################################


class MedidorPosicion(models.Model):
    MEDIDOR_TIPO_CHOICES = [
        ('M', 'Medido'),
        ('C', 'Calculado'),
    ]

    CATEGORIA_CHOICES = [
        ('medidor', 'Medidor'),
        ('titulo', 'Título'),
    ]

    SECCION_CHOICES = [
        ('Vista General Planta', 'Vista General Planta'),
        ('Empalme 1 Planta Harina', 'Empalme 1 Planta Harina'),
        ('Empalme 2 Planta Congelado', 'Empalme 2 Planta Congelado'),
        ('Empalme 3 Pontón Tor', 'Empalme 3 Pontón Tor'),
        ('General Flota', 'General Flota'),
        ('Sala de Calderas', 'Sala de Calderas'),
        ('Planta Harina', 'Planta Harina'),
        ('Planta Congelado', 'Planta Congelado'),
        ('Flota', 'Flota'),
        ('Planta Harina/Congelados', 'Planta Harina/Congelados'),
    ]

    medidor_id = models.CharField(max_length=50, blank=True, null=True)
    x = models.FloatField(default=4575.3279)
    y = models.FloatField(default=1941.9883)

    seccion = models.CharField(
        max_length=100,
        choices=SECCION_CHOICES,
        default='Vista General Planta',
    )

    tipo = models.CharField(
        max_length=1,
        choices=MEDIDOR_TIPO_CHOICES,
        default='M'
    )

    categoria_visual = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default='medidor',
        blank=True,
    )

    titulo = models.CharField(max_length=100, blank=True)
    grafana_url = models.URLField(blank=True, null=True)
    editable = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medidor_id or '(Sin ID)'} @ {self.seccion} ({self.x:.2f}, {self.y:.2f})"

    class Meta:
        db_table = 'core_medidorposicion'
        constraints = [
            models.UniqueConstraint(
                fields=['medidor_id', 'seccion'], name='unique_medidor_por_seccion')
        ]


####################################################################################################################################################################
####################################################################################################################################################################


class ConexionElemento(models.Model):
    SOCKET_OPTIONS = [
        ('top', 'Arriba'),
        ('bottom', 'Abajo'),
        ('left', 'Izquierda'),
        ('right', 'Derecha'),
    ]

    # Origen genérico
    origen_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='origen_tipo')
    origen_object_id = models.CharField(max_length=100)
    origen = GenericForeignKey('origen_content_type', 'origen_object_id')

    # Destino genérico
    destino_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='destino_tipo')
    destino_object_id = models.CharField(max_length=100)
    destino = GenericForeignKey('destino_content_type', 'destino_object_id')

    start_socket = models.CharField(
        max_length=10,
        choices=SOCKET_OPTIONS,
        default='bottom',
        blank=True
    )

    end_socket = models.CharField(
        max_length=10,
        choices=SOCKET_OPTIONS,
        default='top',
        blank=True
    )

    ESTILO_LINEA_CHOICES = [
        ('cyan-grid', 'Cian Grid'),
        ('red-straight', 'Rojo Recto'),
        ('green-fluid', 'Verde Fluido'),
        ('orange-arc', 'Naranja Arco'),
        ('blue-magnet', 'Azul Magneto'),
        ('purple-curve', 'Púrpura Curva'),
        ('gray-straight', 'Gris Recto'),
        ('pink-line', 'Rosado Lineal'),
        ('lime-grid', 'Lima Grid'),
        ('amber-path', 'Ámbar Camino'),

        # Animadas
        ('ani-pink-grid', '🌀 Rosado Animado Grid'),
        ('ani-orange-arc', '🌀 Naranja Animado Arco'),
        ('ani-blue-fluid', '🌀 Azul Animado Fluido'),
        ('ani-red-straight', '🌀 Rojo Animado Recto'),
        ('ani-teal-magnet', '🌀 Teal Magneto'),
        ('ani-indigo-dash', '🌀 Índigo Dash'),
        ('ani-yellow-blink', '🌀 Amarillo Blink'),
        ('ani-cyan-fade', '🌀 Cian Fade'),
        ('ani-green-pulse', '🌀 Verde Pulso'),
        ('ani-violet-spark', '🌀 Violeta Spark'),
        ('ani-brown-glow', '🌀 Marrón Glow'),
        ('ani-charcoal-arc', '🌀 Carbón Arco'),
        ('ani-maroon-fluid', '🌀 Marrón Fluido'),
        ('ani-beige-magnet', '🌀 Beige Magnet'),
        ('ani-navy-curve', '🌀 Azul Marino Curva'),
    ]

    estilo_linea = models.CharField(
        max_length=30,
        choices=ESTILO_LINEA_CHOICES,
        default='cyan-grid',
        blank=True,
        verbose_name="Estilo visual"
    )

    descripcion = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.origen} → {self.destino}"


####################################################################################################################################################################
####################################################################################################################################################################


class ConfiguracionInterfaz(models.Model):
    mostrar_cuadricula = models.BooleanField(default=False)

    def __str__(self):
        return "Configuración de la Interfaz"


####################################################################################################################################################################
####################################################################################################################################################################
